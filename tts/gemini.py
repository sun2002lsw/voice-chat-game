import contextlib
import mimetypes
import os
import struct
from dataclasses import dataclass
from pathlib import Path

from google import genai
from google.genai import types

_MODEL = "gemini-3.1-flash-tts-preview"

# Gemini 3.1 Flash TTS Preview 가격 (https://ai.google.dev/gemini-api/docs/pricing)
_INPUT_PRICE_PER_M_TOKENS_USD = 1.00
_OUTPUT_PRICE_PER_M_TOKENS_USD = 20.00


@dataclass(frozen=True)
class Usage:
    prompt_tokens: int
    output_tokens: int
    total_tokens: int

    @property
    def cost_usd(self) -> float:
        input_cost = self.prompt_tokens * _INPUT_PRICE_PER_M_TOKENS_USD
        output_cost = self.output_tokens * _OUTPUT_PRICE_PER_M_TOKENS_USD
        return (input_cost + output_cost) / 1_000_000


_DEFAULT_BITS_PER_SAMPLE = 16
_DEFAULT_SAMPLE_RATE = 24000
_WAV_HEADER_PREFIX_BYTES = 36
_WAV_PCM_FORMAT_CODE = 1
_WAV_FMT_SUBCHUNK_SIZE = 16
_NUM_CHANNELS = 1


def generate_voice(
    *,
    text: str,
    output_path: Path,
    voice_name: str,
    director_note: str,
    scene: str,
) -> Usage:
    client = _build_client()
    contents = _build_contents(text=text, director_note=director_note, scene=scene)
    config = _build_config(voice_name=voice_name)

    audio_chunks: list[bytes] = []
    mime_type: str | None = None
    last_usage = None

    stream = client.models.generate_content_stream(
        model=_MODEL,
        contents=contents,
        config=config,
    )
    for chunk in stream:
        if chunk.usage_metadata is not None:
            last_usage = chunk.usage_metadata
        if chunk.parts is None:
            continue

        part = chunk.parts[0]
        if part.inline_data and part.inline_data.data:
            audio_chunks.append(part.inline_data.data)
            if mime_type is None:
                mime_type = part.inline_data.mime_type

    if not audio_chunks or mime_type is None:
        msg = f"음성 생성 실패: {output_path.name}"
        raise RuntimeError(msg)

    audio_bytes = b"".join(audio_chunks)
    if mimetypes.guess_extension(mime_type) is None:
        audio_bytes = _wrap_as_wav(audio_bytes, mime_type)

    output_path.write_bytes(audio_bytes)

    if last_usage is None:
        return Usage(prompt_tokens=0, output_tokens=0, total_tokens=0)

    return Usage(
        prompt_tokens=last_usage.prompt_token_count or 0,
        output_tokens=last_usage.candidates_token_count or 0,
        total_tokens=last_usage.total_token_count or 0,
    )


def _build_client() -> genai.Client:
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        msg = "GEMINI_API_KEY 또는 GOOGLE_API_KEY 환경변수가 설정되지 않았습니다"
        raise RuntimeError(msg)
    return genai.Client(api_key=api_key)


def _build_contents(
    *,
    text: str,
    director_note: str,
    scene: str,
) -> list[types.Content]:
    prompt = (
        "Read the following transcript based on the director's note.\n"
        "\n"
        "# Director's note\n"
        f"{director_note}\n"
        "\n"
        "## Scene:\n"
        f"{scene}\n"
        "\n"
        "## Transcript:\n"
        f"{text}"
    )
    return [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt)],
        ),
    ]


def _build_config(*, voice_name: str) -> types.GenerateContentConfig:
    return types.GenerateContentConfig(
        temperature=1,
        response_modalities=["audio"],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice_name),
            ),
        ),
    )


def _wrap_as_wav(audio_data: bytes, mime_type: str) -> bytes:
    bits_per_sample, sample_rate = _parse_audio_mime_type(mime_type)
    data_size = len(audio_data)
    bytes_per_sample = bits_per_sample // 8
    block_align = _NUM_CHANNELS * bytes_per_sample
    byte_rate = sample_rate * block_align
    chunk_size = _WAV_HEADER_PREFIX_BYTES + data_size

    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF",
        chunk_size,
        b"WAVE",
        b"fmt ",
        _WAV_FMT_SUBCHUNK_SIZE,
        _WAV_PCM_FORMAT_CODE,
        _NUM_CHANNELS,
        sample_rate,
        byte_rate,
        block_align,
        bits_per_sample,
        b"data",
        data_size,
    )
    return header + audio_data


def _parse_audio_mime_type(mime_type: str) -> tuple[int, int]:
    bits_per_sample = _DEFAULT_BITS_PER_SAMPLE
    rate = _DEFAULT_SAMPLE_RATE

    for raw_param in mime_type.split(";"):
        param = raw_param.strip()
        if param.lower().startswith("rate="):
            with contextlib.suppress(ValueError, IndexError):
                rate = int(param.split("=", 1)[1])
        elif param.startswith("audio/L"):
            with contextlib.suppress(ValueError, IndexError):
                bits_per_sample = int(param.split("L", 1)[1])

    return bits_per_sample, rate

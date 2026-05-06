import { useCallback, useEffect, useRef, useState } from "react";

type SpeechRecognitionAlternative = { transcript: string };
type SpeechRecognitionResult = {
  isFinal: boolean;
  readonly length: number;
  item(index: number): SpeechRecognitionAlternative;
  [index: number]: SpeechRecognitionAlternative;
};
type SpeechRecognitionResultList = {
  readonly length: number;
  item(index: number): SpeechRecognitionResult;
  [index: number]: SpeechRecognitionResult;
};
type SpeechRecognitionEvent = {
  resultIndex: number;
  results: SpeechRecognitionResultList;
};
type SpeechRecognitionErrorEvent = { error: string };

interface SpeechRecognitionInstance {
  lang: string;
  continuous: boolean;
  interimResults: boolean;
  start(): void;
  stop(): void;
  abort(): void;
  onresult: ((event: SpeechRecognitionEvent) => void) | null;
  onerror: ((event: SpeechRecognitionErrorEvent) => void) | null;
  onend: (() => void) | null;
}

type SpeechRecognitionCtor = new () => SpeechRecognitionInstance;

declare global {
  interface Window {
    SpeechRecognition?: SpeechRecognitionCtor;
    webkitSpeechRecognition?: SpeechRecognitionCtor;
  }
}

function getCtor(): SpeechRecognitionCtor | undefined {
  if (typeof window === "undefined") return undefined;
  return window.SpeechRecognition ?? window.webkitSpeechRecognition;
}

type Options = {
  onFinalText: (text: string) => void;
  lang?: string;
  autoStart?: boolean;
};

export function useSpeechRecognition({
  onFinalText,
  lang = "ko-KR",
  autoStart = false,
}: Options) {
  const recognitionRef = useRef<SpeechRecognitionInstance | null>(null);
  const onFinalTextRef = useRef(onFinalText);
  const userActiveRef = useRef(false);
  const errorBlockedRef = useRef(false);
  const startRef = useRef<() => void>(() => {});
  const startedAtRef = useRef<number>(0);
  const [isListening, setIsListening] = useState(false);
  const [isSupported] = useState(() => getCtor() !== undefined);

  useEffect(() => {
    onFinalTextRef.current = onFinalText;
  }, [onFinalText]);

  useEffect(() => {
    startRef.current = () => {
      if (recognitionRef.current) return;
      const Ctor = getCtor();
      if (!Ctor) return;

      const recognition = new Ctor();
      recognition.lang = lang;
      recognition.continuous = true;
      recognition.interimResults = false;

      recognition.onresult = (event) => {
        let chunk = "";
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const result = event.results[i];
          if (result.isFinal) {
            chunk += result[0].transcript;
          }
        }
        const trimmed = chunk.trim();
        if (trimmed) {
          onFinalTextRef.current(trimmed);
        }
      };
      recognition.onerror = (event) => {
        if (
          event.error === "not-allowed" ||
          event.error === "service-not-allowed"
        ) {
          errorBlockedRef.current = true;
          userActiveRef.current = false;
        }
        // 그 외(no-speech, audio-capture, network)는 onend의 자동 재시작에 맡김
      };
      recognition.onend = () => {
        recognitionRef.current = null;
        if (userActiveRef.current && !errorBlockedRef.current) {
          // Chrome이 1초 안에 끝낸 경우: user gesture 없이는 시작 불가한 상태 → 루프 방지
          if (Date.now() - startedAtRef.current < 1000) {
            setIsListening(false);
            return;
          }
          window.setTimeout(() => {
            if (
              userActiveRef.current &&
              !errorBlockedRef.current &&
              !recognitionRef.current
            ) {
              startRef.current();
            }
          }, 500);
        } else {
          setIsListening(false);
        }
      };

      recognitionRef.current = recognition;
      startedAtRef.current = Date.now();
      try {
        recognition.start();
        setIsListening(true);
      } catch {
        recognitionRef.current = null;
        setIsListening(false);
      }
    };
  }, [lang]);

  const start = useCallback(() => {
    errorBlockedRef.current = false;
    userActiveRef.current = true;
    startRef.current();
  }, []);

  const stop = useCallback(() => {
    userActiveRef.current = false;
    const r = recognitionRef.current;
    if (!r) return;
    try {
      r.stop();
    } catch {
      // ignore
    }
  }, []);

  useEffect(() => {
    if (autoStart && isSupported) {
      errorBlockedRef.current = false;
      userActiveRef.current = true;
      startRef.current();
    }
    return () => {
      userActiveRef.current = false;
      const r = recognitionRef.current;
      if (!r) return;
      r.onresult = null;
      r.onerror = null;
      r.onend = null;
      try {
        r.stop();
      } catch {
        // already stopped
      }
      recognitionRef.current = null;
    };
  }, [autoStart, isSupported]);

  return { isSupported, isListening, start, stop };
}

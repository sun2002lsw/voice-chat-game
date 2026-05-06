import { useEffect, useRef, useState } from "react";
import type { MouseEvent } from "react";

import styles from "./AudioPlayer.module.css";

type Props = {
  voiceUrl: string;
  stepKey: string;
  visitCount: number;
  onEnded?: () => void;
};

function formatTime(seconds: number): string {
  if (!Number.isFinite(seconds)) return "0:00";
  const total = Math.max(0, Math.floor(seconds));
  const m = Math.floor(total / 60);
  const s = total % 60;
  return `${m}:${s.toString().padStart(2, "0")}`;
}

export function AudioPlayer({ voiceUrl, stepKey, visitCount, onEnded }: Props) {
  const src =
    `${voiceUrl}?step=${encodeURIComponent(stepKey)}&v=${visitCount}`;
  const cacheKey = `${stepKey}#${visitCount}`;

  const audioRef = useRef<HTMLAudioElement>(null);
  const trackRef = useRef<HTMLDivElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);

  useEffect(() => {
    setCurrentTime(0);
    setDuration(0);
    setIsPlaying(false);
  }, [stepKey, visitCount]);

  function togglePlay() {
    const audio = audioRef.current;
    if (audio === null) return;
    if (audio.paused) {
      void audio.play();
    } else {
      audio.pause();
    }
  }

  function seek(event: MouseEvent<HTMLDivElement>) {
    const audio = audioRef.current;
    const track = trackRef.current;
    if (audio === null || track === null) return;
    if (!Number.isFinite(audio.duration) || audio.duration === 0) return;
    const rect = track.getBoundingClientRect();
    const ratio = (event.clientX - rect.left) / rect.width;
    const clamped = Math.max(0, Math.min(1, ratio));
    audio.currentTime = clamped * audio.duration;
  }

  const progressPct = duration > 0 ? (currentTime / duration) * 100 : 0;

  return (
    <div className={styles.player}>
      <audio
        key={cacheKey}
        ref={audioRef}
        src={src}
        autoPlay
        controls
        hidden
        onPlay={() => setIsPlaying(true)}
        onPause={() => setIsPlaying(false)}
        onTimeUpdate={(e) => setCurrentTime(e.currentTarget.currentTime)}
        onLoadedMetadata={(e) => setDuration(e.currentTarget.duration)}
        onEnded={() => {
          setIsPlaying(false);
          onEnded?.();
        }}
      />
      <button
        type="button"
        className={styles.button}
        onClick={togglePlay}
        aria-label={isPlaying ? "일시정지" : "재생"}
      >
        {isPlaying ? "❚❚" : "▶"}
      </button>
      <div
        className={styles.trackContainer}
        ref={trackRef}
        onClick={seek}
        role="slider"
        aria-valuemin={0}
        aria-valuemax={duration}
        aria-valuenow={currentTime}
        aria-label="재생 위치"
        tabIndex={0}
      >
        <div className={styles.track}>
          <div
            className={styles.fill}
            style={{ width: `${progressPct}%` }}
          />
        </div>
      </div>
      <span className={styles.time}>
        {formatTime(currentTime)} / {formatTime(duration)}
      </span>
    </div>
  );
}

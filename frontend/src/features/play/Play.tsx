import { useCallback, useEffect, useRef, useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";

import { fetchStep, HttpError } from "../../api/client";
import type { StepInfo } from "../../types";

import { ConditionsPanel } from "./conditions/ConditionsPanel";
import { AudioPlayer } from "./picture/AudioPlayer";
import { PicturePanel } from "./picture/PicturePanel";
import { DialogPanel } from "./dialog/DialogPanel";

import styles from "./Play.module.css";

const MIN_LEFT_WIDTH = 320;
const MIN_RIGHT_WIDTH = 380;
const MIN_CENTER_WIDTH = 200;
const FALLBACK_AUDIO_HEIGHT = 60;

export function Play() {
  const { name } = useParams<{ name: string }>();
  const location = useLocation();
  const navigate = useNavigate();

  const [stepInfo, setStepInfo] = useState<StepInfo | null>(null);
  const [dialog, setDialog] = useState<string[]>([]);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [centerWidth, setCenterWidth] = useState<number | null>(null);
  const [pictureHeight, setPictureHeight] = useState<number | null>(null);

  const layoutRef = useRef<HTMLDivElement>(null);
  const audioRef = useRef<HTMLDivElement>(null);
  const aspectRef = useRef<number | null>(null);
  const stepInfoRef = useRef<StepInfo | null>(null);
  stepInfoRef.current = stepInfo;

  const recomputeLayout = useCallback(() => {
    const aspect = aspectRef.current;
    const layout = layoutRef.current;
    if (aspect === null || layout === null) return;

    const layoutH = layout.clientHeight;
    const layoutW = layout.clientWidth;
    const playerEl = audioRef.current?.firstElementChild as HTMLElement | undefined;
    const minAudioH = playerEl?.offsetHeight ?? FALLBACK_AUDIO_HEIGHT;
    const maxPictureH = layoutH - minAudioH;
    const idealCenterW = maxPictureH * aspect;
    const maxCenterW = layoutW - MIN_LEFT_WIDTH - MIN_RIGHT_WIDTH;

    if (idealCenterW <= maxCenterW) {
      setCenterWidth(Math.max(MIN_CENTER_WIDTH, idealCenterW));
      setPictureHeight(maxPictureH);
    } else {
      setCenterWidth(maxCenterW);
      setPictureHeight(maxCenterW / aspect);
    }
  }, []);

  const handleAspectChange = useCallback(
    (aspect: number) => {
      aspectRef.current = aspect;
      recomputeLayout();
    },
    [recomputeLayout],
  );

  useEffect(() => {
    window.addEventListener("resize", recomputeLayout);
    return () => window.removeEventListener("resize", recomputeLayout);
  }, [recomputeLayout]);

  // 최초 스텝 로드
  useEffect(() => {
    const firstStepName = (location.state as { firstStepName?: string } | null)
      ?.firstStepName;
    if (!name || !firstStepName) {
      navigate("/");
      return;
    }
    fetchStep(name, firstStepName)
      .then((info) => {
        setStepInfo(info);
        setDialog([info.script]);
      })
      .catch(() => navigate("/"));
  }, []);

  // 키보드 숫자키로 다음 스텝 선택
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      const info = stepInfoRef.current;
      if (!info || info.is_terminal || isLoading) return;
      // 입력 필드에 포커스가 있으면 무시
      const tag = (e.target as HTMLElement).tagName;
      if (tag === "INPUT" || tag === "TEXTAREA") return;

      const num = parseInt(e.key, 10);
      if (isNaN(num) || num < 0 || num >= info.next_step_names.length) return;

      const nextStepName = info.next_step_names[num];
      setIsLoading(true);
      fetchStep(name!, nextStepName)
        .then((next) => {
          setStepInfo(next);
          setDialog((prev) => [...prev, next.script]);
        })
        .catch((err: unknown) => {
          if (err instanceof HttpError) {
            setErrorMessage("스텝을 불러오지 못했습니다.");
          }
        })
        .finally(() => setIsLoading(false));
    }

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isLoading, name]);

  if (stepInfo === null) {
    return null;
  }

  const layoutStyle =
    centerWidth !== null
      ? {
          gridTemplateColumns:
            `minmax(${MIN_LEFT_WIDTH}px, 1fr) ${centerWidth}px ` +
            `minmax(${MIN_RIGHT_WIDTH}px, 1fr)`,
        }
      : undefined;

  const centerStyle =
    pictureHeight !== null
      ? { gridTemplateRows: `${pictureHeight}px 1fr` }
      : undefined;

  return (
    <div className={styles.layout} ref={layoutRef} style={layoutStyle}>
      <aside className={styles.debug}>
        <ConditionsPanel
          conditions={stepInfo.conditions}
          nextStepNames={stepInfo.next_step_names}
          isTerminal={stepInfo.is_terminal}
          isLoading={isLoading}
        />
      </aside>
      <section className={styles.center} style={centerStyle}>
        <div className={styles.picture}>
          <PicturePanel
            pictureUrl={stepInfo.picture_url}
            stepKey={stepInfo.step_name}
            onAspectChange={handleAspectChange}
          />
        </div>
        <div className={styles.audio} ref={audioRef}>
          <AudioPlayer
            voiceUrl={stepInfo.voice_url}
            stepKey={stepInfo.step_name}
            loop={stepInfo.loop}
          />
        </div>
      </section>
      <aside className={styles.chat}>
        <DialogPanel
          scenarioName={name ?? ""}
          dialog={dialog}
          isTerminal={stepInfo.is_terminal}
          onHome={() => navigate("/")}
        />
      </aside>
      {errorMessage !== null && (
        <div role="alert" className={styles.alert}>
          <span>{errorMessage}</span>
          <button type="button" onClick={() => setErrorMessage(null)} aria-label="알림 닫기">
            닫기
          </button>
        </div>
      )}
    </div>
  );
}

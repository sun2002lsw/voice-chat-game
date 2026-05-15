import { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { fetchState, HttpError, submitInput } from "../../api/client";
import type { DialogEntry, SessionState } from "../../types";

import { ChatPanel } from "./chat/ChatPanel";
import { DebugPanel } from "./debug/DebugPanel";
import { AudioPlayer } from "./picture/AudioPlayer";
import { PicturePanel } from "./picture/PicturePanel";

import styles from "./Play.module.css";

const MIN_LEFT_WIDTH = 320;
const MIN_RIGHT_WIDTH = 380;
const MIN_CENTER_WIDTH = 200;
const FALLBACK_AUDIO_HEIGHT = 60;

export function Play() {
  const { name } = useParams<{ name: string }>();
  const [state, setState] = useState<SessionState | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [pendingUserText, setPendingUserText] = useState<string | null>(null);
  const [audioKey, setAudioKey] = useState(0);
  const [centerWidth, setCenterWidth] = useState<number | null>(null);
  const [pictureHeight, setPictureHeight] = useState<number | null>(null);
  const navigate = useNavigate();

  const layoutRef = useRef<HTMLDivElement>(null);
  const audioRef = useRef<HTMLDivElement>(null);
  const aspectRef = useRef<number | null>(null);

  const recomputeLayout = useCallback(() => {
    const aspect = aspectRef.current;
    const layout = layoutRef.current;
    if (aspect === null || layout === null) return;

    const layoutH = layout.clientHeight;
    const layoutW = layout.clientWidth;

    // Audio's natural (un-grown) height is the AudioPlayer content height
    // — read from its first child, since the wrapper itself may already be
    // expanded by a previous layout pass.
    const playerEl = audioRef.current?.firstElementChild as
      | HTMLElement
      | undefined;
    const minAudioH = playerEl?.offsetHeight ?? FALLBACK_AUDIO_HEIGHT;

    const maxPictureH = layoutH - minAudioH;
    const idealCenterW = maxPictureH * aspect;
    const maxCenterW = layoutW - MIN_LEFT_WIDTH - MIN_RIGHT_WIDTH;

    let nextCenterW: number;
    let nextPictureH: number;
    if (idealCenterW <= maxCenterW) {
      nextCenterW = Math.max(MIN_CENTER_WIDTH, idealCenterW);
      nextPictureH = maxPictureH;
    } else {
      nextCenterW = maxCenterW;
      nextPictureH = maxCenterW / aspect;
    }

    setCenterWidth(nextCenterW);
    setPictureHeight(nextPictureH);
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

  useEffect(() => {
    if (name === undefined) return;
    let cancelled = false;
    fetchState(name)
      .then((s) => {
        if (cancelled) return;
        setState(s);
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        if (err instanceof HttpError && err.status === 404) {
          navigate("/");
          return;
        }
        setErrorMessage("진행 상태를 불러오지 못했습니다.");
      });
    return () => {
      cancelled = true;
    };
  }, [name, navigate]);

  const alert = errorMessage !== null && (
    <div role="alert" className={styles.alert}>
      <span>{errorMessage}</span>
      <button
        type="button"
        onClick={() => setErrorMessage(null)}
        aria-label="알림 닫기"
      >
        닫기
      </button>
    </div>
  );

  if (name === undefined || state === null) {
    return alert || null;
  }

  async function handleSubmit(text: string) {
    if (name === undefined) return;
    if (pendingUserText !== null) return;

    const index = parseInt(text, 10);
    if (isNaN(index)) return;

    setPendingUserText(text);
    try {
      const newState = await submitInput(name, index);
      setState(newState);
      setAudioKey((k) => k + 1);
    } catch {
      setErrorMessage("전송에 실패했습니다.");
    } finally {
      setPendingUserText(null);
    }
  }

  const isPending = pendingUserText !== null;
  const dialog: DialogEntry[] = isPending
    ? [
        ...state.dialog,
        {
          role: "user",
          text: pendingUserText,
          created_at: new Date().toISOString(),
        },
      ]
    : state.dialog;

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
        <DebugPanel stateLog={state.state_log} />
      </aside>
      <section className={styles.center} style={centerStyle}>
        <div className={styles.picture}>
          <PicturePanel
            pictureUrl={state.picture_url}
            stepKey={state.current_step_name}
            visitCount={state.current_visit_count}
            onAspectChange={handleAspectChange}
          />
        </div>
        <div className={styles.audio} ref={audioRef}>
          <AudioPlayer
            voiceUrl={state.voice_url}
            stepKey={state.current_step_name}
            visitCount={state.current_visit_count}
            audioKey={audioKey}
          />
        </div>
      </section>
      <aside className={styles.chat}>
        <ChatPanel
          scenarioName={state.scenario_name}
          dialog={dialog}
          isTerminal={state.is_terminal}
          isPending={isPending}
          onSubmit={handleSubmit}
          onHome={() => navigate("/")}
        />
      </aside>
      {alert}
    </div>
  );
}

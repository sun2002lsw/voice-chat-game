import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { fetchState, HttpError, submitInput } from "../../api/client";
import type { SessionState } from "../../types";

import { ChatPanel } from "./chat/ChatPanel";
import { DebugPanel } from "./debug/DebugPanel";
import { AudioPlayer } from "./picture/AudioPlayer";
import { PicturePanel } from "./picture/PicturePanel";

import styles from "./Play.module.css";

export function Play() {
  const { name } = useParams<{ name: string }>();
  const [state, setState] = useState<SessionState | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const navigate = useNavigate();

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
    try {
      const newState = await submitInput(name, text);
      setState(newState);
    } catch {
      setErrorMessage("전송에 실패했습니다.");
    }
  }

  return (
    <div className={styles.layout}>
      <aside className={styles.debug}>
        <DebugPanel stateLog={state.state_log} />
      </aside>
      <section className={styles.center}>
        <div className={styles.picture}>
          <PicturePanel
            pictureUrl={state.picture_url}
            stepKey={state.current_step_name}
          />
        </div>
        <div className={styles.audio}>
          <AudioPlayer
            voiceUrl={state.voice_url}
            stepKey={state.current_step_name}
          />
        </div>
      </section>
      <aside className={styles.chat}>
        <ChatPanel
          scenarioName={state.scenario_name}
          dialog={state.dialog}
          isTerminal={state.is_terminal}
          onSubmit={handleSubmit}
        />
      </aside>
      {alert}
    </div>
  );
}

import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { fetchState, submitInput } from "../api/client";
import { AudioPlayer } from "../components/AudioPlayer";
import { ChatPanel } from "../components/ChatPanel";
import { DebugPanel } from "../components/DebugPanel";
import { PicturePanel } from "../components/PicturePanel";
import type { SessionState } from "../types";

import styles from "./Play.module.css";

export function Play() {
  const { name } = useParams<{ name: string }>();
  const [state, setState] = useState<SessionState | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (name === undefined) return;
    fetchState(name)
      .then(setState)
      .catch(() => navigate("/"));
  }, [name, navigate]);

  if (name === undefined || state === null) {
    return null;
  }

  async function handleSubmit(text: string) {
    if (name === undefined) return;
    const newState = await submitInput(name, text);
    setState(newState);
  }

  return (
    <div className={styles.layout}>
      <aside className={styles.debug}>
        <DebugPanel stateLog={state.state_log} />
      </aside>
      <section className={styles.picture}>
        <PicturePanel
          pictureUrl={state.picture_url}
          stepKey={state.current_step_name}
        />
      </section>
      <aside className={styles.chat}>
        <ChatPanel
          scenarioName={state.scenario_name}
          dialog={state.dialog}
          isTerminal={state.is_terminal}
          onSubmit={handleSubmit}
        />
      </aside>
      <AudioPlayer
        voiceUrl={state.voice_url}
        stepKey={state.current_step_name}
      />
    </div>
  );
}

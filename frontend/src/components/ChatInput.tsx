import { useState } from "react";
import type { FormEvent } from "react";

import styles from "./ChatInput.module.css";

type Props = {
  onSubmit: (text: string) => void;
  disabled: boolean;
};

export function ChatInput({ onSubmit, disabled }: Props) {
  const [text, setText] = useState("");

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const trimmed = text.trim();
    if (trimmed === "") return;
    onSubmit(trimmed);
    setText("");
  }

  return (
    <form className={styles.form} onSubmit={handleSubmit}>
      <input
        type="text"
        className={styles.input}
        value={text}
        onChange={(e) => setText(e.target.value)}
        disabled={disabled}
        placeholder="메시지를 입력하세요"
      />
      <button type="submit" className={styles.sendButton} disabled={disabled}>
        전송
      </button>
    </form>
  );
}

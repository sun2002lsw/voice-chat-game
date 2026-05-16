import { useEffect, useRef, useState } from "react";
import type { FormEvent, KeyboardEvent } from "react";

import styles from "./ChatInput.module.css";

type Props = {
  onSubmit: (text: string) => void;
  disabled: boolean;
  submitDisabled: boolean;
};

export function ChatInput({ onSubmit, disabled, submitDisabled }: Props) {
  const [text, setText] = useState("");
  const cannotSubmit = disabled || submitDisabled;

  const onSubmitRef = useRef(onSubmit);
  useEffect(() => {
    onSubmitRef.current = onSubmit;
  }, [onSubmit]);

  useEffect(() => {
    const trimmed = text.trim();
    if (trimmed === "") return;
    if (cannotSubmit) return;
    const handle = window.setTimeout(() => {
      onSubmitRef.current(trimmed);
      setText("");
    }, 1000);
    return () => window.clearTimeout(handle);
  }, [text, cannotSubmit]);

  function submit() {
    const trimmed = text.trim();
    if (trimmed === "") return;
    onSubmit(trimmed);
    setText("");
  }

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (cannotSubmit) return;
    submit();
  }

  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key !== "Enter") return;
    if (event.shiftKey) return;
    if (event.nativeEvent.isComposing) return;
    event.preventDefault();
    if (cannotSubmit) return;
    submit();
  }

  return (
    <form className={styles.form} onSubmit={handleSubmit}>
      <textarea
        className={styles.input}
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={disabled}
        placeholder="메시지를 입력하세요 (Shift+Enter 줄바꿈)"
        rows={2}
      />
      <button
        type="submit"
        className={styles.sendButton}
        disabled={cannotSubmit}
      >
        전송
      </button>
    </form>
  );
}

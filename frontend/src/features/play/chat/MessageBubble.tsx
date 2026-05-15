import styles from "./MessageBubble.module.css";

type Props = {
  text: string;
};

export function MessageBubble({ text }: Props) {
  return (
    <div className={styles.characterRow} data-role="character">
      <div className={styles.characterBubble}>{text}</div>
    </div>
  );
}

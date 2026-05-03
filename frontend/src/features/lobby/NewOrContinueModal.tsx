import styles from "./NewOrContinueModal.module.css";

type Props = {
  scenarioName: string;
  onNewGame: () => void;
  onContinue: () => void;
  onClose: () => void;
};

export function NewOrContinueModal({
  scenarioName,
  onNewGame,
  onContinue,
  onClose,
}: Props) {
  return (
    <div className={styles.backdrop} onClick={onClose}>
      <div
        className={styles.modal}
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
      >
        <h2 className={styles.title}>{scenarioName}</h2>
        <p className={styles.message}>진행 기록이 있습니다. 어떻게 시작할까요?</p>
        <div className={styles.actions}>
          <button type="button" onClick={onContinue}>이어하기</button>
          <button type="button" onClick={onNewGame}>새로하기</button>
          <button type="button" onClick={onClose}>닫기</button>
        </div>
      </div>
    </div>
  );
}

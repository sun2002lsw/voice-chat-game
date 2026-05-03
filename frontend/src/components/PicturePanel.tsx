import styles from "./PicturePanel.module.css";

type Props = {
  pictureUrl: string;
  stepKey: string;
};

export function PicturePanel({ pictureUrl, stepKey }: Props) {
  const src = `${pictureUrl}?step=${encodeURIComponent(stepKey)}`;
  return (
    <div className={styles.panel}>
      <img className={styles.image} src={src} alt="현재 장면" />
    </div>
  );
}

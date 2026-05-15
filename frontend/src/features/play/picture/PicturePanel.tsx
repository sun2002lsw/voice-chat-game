import type { SyntheticEvent } from "react";

import styles from "./PicturePanel.module.css";

type Props = {
  pictureUrl: string;
  stepKey: string;
  onAspectChange?: (aspect: number) => void;
};

export function PicturePanel({ pictureUrl, stepKey, onAspectChange }: Props) {
  const src = `${pictureUrl}?step=${encodeURIComponent(stepKey)}`;

  function handleLoad(event: SyntheticEvent<HTMLImageElement>) {
    const img = event.currentTarget;
    if (img.naturalWidth === 0 || img.naturalHeight === 0) return;
    onAspectChange?.(img.naturalWidth / img.naturalHeight);
  }

  return (
    <div className={styles.panel}>
      <img
        className={styles.image}
        src={src}
        alt="현재 장면"
        onLoad={handleLoad}
      />
    </div>
  );
}

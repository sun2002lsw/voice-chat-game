type Props = {
  voiceUrl: string;
  stepKey: string;
};

export function AudioPlayer({ voiceUrl, stepKey }: Props) {
  const src = `${voiceUrl}?step=${encodeURIComponent(stepKey)}`;
  return <audio key={stepKey} src={src} autoPlay controls />;
}

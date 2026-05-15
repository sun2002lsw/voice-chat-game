import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { AudioPlayer } from "./AudioPlayer";

describe("AudioPlayer", () => {
  it("renders <audio> with voice_url + step + key query", () => {
    const { container } = render(
      <AudioPlayer
        voiceUrl="/api/scenarios/test_cafe/voice/0"
        stepKey="1. 인사"
        audioKey={0}
      />,
    );

    const audio = container.querySelector("audio");
    expect(audio).not.toBeNull();
    expect(audio).toHaveAttribute(
      "src",
      "/api/scenarios/test_cafe/voice/0?step=1.%20%EC%9D%B8%EC%82%AC&k=0",
    );
  });

  it("has autoPlay enabled", () => {
    const { container } = render(
      <AudioPlayer
        voiceUrl="/api/scenarios/test_cafe/voice/0"
        stepKey="step1"
        audioKey={0}
      />,
    );

    expect(container.querySelector("audio")).toHaveAttribute("autoplay");
  });

  it("renders the controls UI", () => {
    const { container } = render(
      <AudioPlayer
        voiceUrl="/api/scenarios/test_cafe/voice/0"
        stepKey="step1"
        audioKey={0}
      />,
    );

    expect(container.querySelector("audio")).toHaveAttribute("controls");
  });

  it("updates src when audioKey changes (cycle cache busting)", () => {
    const { container, rerender } = render(
      <AudioPlayer
        voiceUrl="/api/scenarios/test_cafe/voice/0"
        stepKey="step1"
        audioKey={0}
      />,
    );

    rerender(
      <AudioPlayer
        voiceUrl="/api/scenarios/test_cafe/voice/1"
        stepKey="step1"
        audioKey={1}
      />,
    );

    expect(container.querySelector("audio")).toHaveAttribute(
      "src",
      "/api/scenarios/test_cafe/voice/1?step=step1&k=1",
    );
  });
});

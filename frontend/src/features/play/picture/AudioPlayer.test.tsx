import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { AudioPlayer } from "./AudioPlayer";

describe("AudioPlayer", () => {
  it("renders <audio> with voice_url + step + visit query", () => {
    const { container } = render(
      <AudioPlayer
        voiceUrl="/api/scenarios/test_cafe/voice"
        stepKey="1. 인사"
        visitCount={1}
        audioKey={0}
      />,
    );

    const audio = container.querySelector("audio");
    expect(audio).not.toBeNull();
    expect(audio).toHaveAttribute(
      "src",
      "/api/scenarios/test_cafe/voice?step=1.%20%EC%9D%B8%EC%82%AC&v=1",
    );
  });

  it("has autoPlay enabled", () => {
    const { container } = render(
      <AudioPlayer
        voiceUrl="/api/scenarios/test_cafe/voice"
        stepKey="step1"
        visitCount={1}
        audioKey={0}
      />,
    );

    expect(container.querySelector("audio")).toHaveAttribute("autoplay");
  });

  it("renders the controls UI (play/pause/seek/volume)", () => {
    const { container } = render(
      <AudioPlayer
        voiceUrl="/api/scenarios/test_cafe/voice"
        stepKey="step1"
        visitCount={1}
        audioKey={0}
      />,
    );

    expect(container.querySelector("audio")).toHaveAttribute("controls");
  });

  it("updates src when stepKey changes", () => {
    const { container, rerender } = render(
      <AudioPlayer
        voiceUrl="/api/scenarios/test_cafe/voice"
        stepKey="step1"
        visitCount={1}
        audioKey={0}
      />,
    );

    rerender(
      <AudioPlayer
        voiceUrl="/api/scenarios/test_cafe/voice"
        stepKey="step2"
        visitCount={1}
        audioKey={0}
      />,
    );

    expect(container.querySelector("audio")).toHaveAttribute(
      "src",
      "/api/scenarios/test_cafe/voice?step=step2&v=1",
    );
  });

  it("updates src when visitCount changes (self-loop cache busting)", () => {
    const { container, rerender } = render(
      <AudioPlayer
        voiceUrl="/api/scenarios/test_cafe/voice"
        stepKey="step1"
        visitCount={1}
        audioKey={0}
      />,
    );

    rerender(
      <AudioPlayer
        voiceUrl="/api/scenarios/test_cafe/voice"
        stepKey="step1"
        visitCount={2}
        audioKey={0}
      />,
    );

    expect(container.querySelector("audio")).toHaveAttribute(
      "src",
      "/api/scenarios/test_cafe/voice?step=step1&v=2",
    );
  });
});

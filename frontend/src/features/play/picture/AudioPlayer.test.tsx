import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { AudioPlayer } from "./AudioPlayer";

describe("AudioPlayer", () => {
  it("renders <audio> with voice_url + step query", () => {
    const { container } = render(
      <AudioPlayer
        voiceUrl="/api/scenarios/test_cafe/voice"
        stepKey="1. 인사"
      />,
    );

    const audio = container.querySelector("audio");
    expect(audio).not.toBeNull();
    expect(audio).toHaveAttribute(
      "src",
      "/api/scenarios/test_cafe/voice?step=1.%20%EC%9D%B8%EC%82%AC",
    );
  });

  it("has autoPlay enabled", () => {
    const { container } = render(
      <AudioPlayer
        voiceUrl="/api/scenarios/test_cafe/voice"
        stepKey="step1"
      />,
    );

    expect(container.querySelector("audio")).toHaveAttribute("autoplay");
  });

  it("renders the controls UI", () => {
    const { container } = render(
      <AudioPlayer
        voiceUrl="/api/scenarios/test_cafe/voice"
        stepKey="step1"
      />,
    );

    expect(container.querySelector("audio")).toHaveAttribute("controls");
  });
});

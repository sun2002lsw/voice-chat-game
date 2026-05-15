import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { PicturePanel } from "./PicturePanel";

describe("PicturePanel", () => {
  it("renders <img> with picture_url + step query", () => {
    render(
      <PicturePanel
        pictureUrl="/api/scenarios/test_cafe/picture"
        stepKey="1. 인사"
      />,
    );

    const img = screen.getByRole("img");
    expect(img).toHaveAttribute(
      "src",
      "/api/scenarios/test_cafe/picture?step=1.%20%EC%9D%B8%EC%82%AC",
    );
  });

  it("updates src when stepKey changes", () => {
    const { rerender } = render(
      <PicturePanel
        pictureUrl="/api/scenarios/test_cafe/picture"
        stepKey="step1"
      />,
    );

    rerender(
      <PicturePanel
        pictureUrl="/api/scenarios/test_cafe/picture"
        stepKey="step2"
      />,
    );

    expect(screen.getByRole("img")).toHaveAttribute(
      "src",
      "/api/scenarios/test_cafe/picture?step=step2",
    );
  });
});

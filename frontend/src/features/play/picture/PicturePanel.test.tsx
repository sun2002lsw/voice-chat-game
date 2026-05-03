import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { PicturePanel } from "./PicturePanel";

describe("PicturePanel", () => {
  it("renders <img> with picture_url + step + visit query", () => {
    render(
      <PicturePanel
        pictureUrl="/api/scenarios/test_cafe/picture"
        stepKey="1. 인사"
        visitCount={1}
      />,
    );

    const img = screen.getByRole("img");
    expect(img).toHaveAttribute(
      "src",
      "/api/scenarios/test_cafe/picture?step=1.%20%EC%9D%B8%EC%82%AC&v=1",
    );
  });

  it("updates src when visitCount changes (self-loop cache busting)", () => {
    const { rerender } = render(
      <PicturePanel
        pictureUrl="/api/scenarios/test_cafe/picture"
        stepKey="1. 인사"
        visitCount={1}
      />,
    );

    rerender(
      <PicturePanel
        pictureUrl="/api/scenarios/test_cafe/picture"
        stepKey="1. 인사"
        visitCount={2}
      />,
    );

    expect(screen.getByRole("img")).toHaveAttribute(
      "src",
      "/api/scenarios/test_cafe/picture?step=1.%20%EC%9D%B8%EC%82%AC&v=2",
    );
  });
});

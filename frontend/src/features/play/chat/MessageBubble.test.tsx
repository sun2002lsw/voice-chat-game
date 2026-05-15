import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { MessageBubble } from "./MessageBubble";

describe("MessageBubble", () => {
  it("renders text", () => {
    render(<MessageBubble text="어서오세요" />);

    expect(screen.getByText("어서오세요")).toBeInTheDocument();
  });

  it("has data-role character attribute", () => {
    const { container } = render(<MessageBubble text="어서오세요" />);

    expect(container.querySelector("[data-role='character']")).not.toBeNull();
  });
});

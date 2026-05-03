import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import type { DialogEntry } from "../types";

import { MessageBubble } from "./MessageBubble";

const characterEntry: DialogEntry = {
  role: "character",
  text: "어서오세요",
  created_at: "2026-05-03T14:23:00Z",
};

const userEntry: DialogEntry = {
  role: "user",
  text: "주문할게요",
  created_at: "2026-05-03T14:24:00Z",
};

describe("MessageBubble", () => {
  it("renders character text", () => {
    render(<MessageBubble entry={characterEntry} />);

    expect(screen.getByText("어서오세요")).toBeInTheDocument();
  });

  it("renders user text", () => {
    render(<MessageBubble entry={userEntry} />);

    expect(screen.getByText("주문할게요")).toBeInTheDocument();
  });

  it("tags row with data-role attribute (character)", () => {
    const { container } = render(<MessageBubble entry={characterEntry} />);

    expect(container.querySelector("[data-role='character']")).not.toBeNull();
  });

  it("tags row with data-role attribute (user)", () => {
    const { container } = render(<MessageBubble entry={userEntry} />);

    expect(container.querySelector("[data-role='user']")).not.toBeNull();
  });

  it("shows time (HH:mm) only on user messages", () => {
    const { rerender } = render(<MessageBubble entry={userEntry} />);
    expect(screen.getByText(/^\d{2}:\d{2}$/)).toBeInTheDocument();

    rerender(<MessageBubble entry={characterEntry} />);
    expect(screen.queryByText(/^\d{2}:\d{2}$/)).not.toBeInTheDocument();
  });
});

import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import type { DialogEntry } from "../types";

import { ChatPanel } from "./ChatPanel";

const dialog: DialogEntry[] = [
  {
    role: "character",
    text: "어서오세요",
    created_at: "2026-05-03T14:00:00Z",
  },
  {
    role: "user",
    text: "주문할게요",
    created_at: "2026-05-03T14:01:00Z",
  },
];

describe("ChatPanel", () => {
  it("renders scenario name at the top", () => {
    render(
      <ChatPanel
        scenarioName="카페 주문"
        dialog={dialog}
        isTerminal={false}
        onSubmit={() => {}}
      />,
    );

    expect(screen.getByRole("heading", { name: "카페 주문" })).toBeInTheDocument();
  });

  it("renders one bubble per dialog entry", () => {
    render(
      <ChatPanel
        scenarioName="카페 주문"
        dialog={dialog}
        isTerminal={false}
        onSubmit={() => {}}
      />,
    );

    expect(screen.getByText("어서오세요")).toBeInTheDocument();
    expect(screen.getByText("주문할게요")).toBeInTheDocument();
  });

  it("disables input when isTerminal is true", () => {
    render(
      <ChatPanel
        scenarioName="카페 주문"
        dialog={dialog}
        isTerminal={true}
        onSubmit={() => {}}
      />,
    );

    expect(screen.getByRole("textbox")).toBeDisabled();
  });

  it("forwards user submission to onSubmit prop", async () => {
    const onSubmit = vi.fn();
    const user = userEvent.setup();
    render(
      <ChatPanel
        scenarioName="카페 주문"
        dialog={dialog}
        isTerminal={false}
        onSubmit={onSubmit}
      />,
    );

    await user.type(screen.getByRole("textbox"), "다음 입력{Enter}");

    expect(onSubmit).toHaveBeenCalledWith("다음 입력");
  });
});

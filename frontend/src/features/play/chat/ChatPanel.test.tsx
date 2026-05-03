import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import type { DialogEntry } from "../../../types";

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
        isPending={false}
        onSubmit={() => {}}
        onHome={() => {}}
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
        isPending={false}
        onSubmit={() => {}}
        onHome={() => {}}
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
        isPending={false}
        onSubmit={() => {}}
        onHome={() => {}}
      />,
    );

    expect(screen.getByRole("textbox")).toBeDisabled();
  });

  it("blocks submit and shows typing indicator when isPending", () => {
    render(
      <ChatPanel
        scenarioName="카페 주문"
        dialog={dialog}
        isTerminal={false}
        isPending={true}
        onSubmit={() => {}}
        onHome={() => {}}
      />,
    );

    expect(screen.getByRole("textbox")).not.toBeDisabled();
    expect(screen.getByRole("button", { name: "전송" })).toBeDisabled();
    expect(screen.getByRole("status", { name: "응답 작성 중" })).toBeInTheDocument();
  });

  it("does not show typing indicator when not pending", () => {
    render(
      <ChatPanel
        scenarioName="카페 주문"
        dialog={dialog}
        isTerminal={false}
        isPending={false}
        onSubmit={() => {}}
        onHome={() => {}}
      />,
    );

    expect(
      screen.queryByRole("status", { name: "응답 작성 중" }),
    ).not.toBeInTheDocument();
  });

  it("forwards user submission to onSubmit prop", async () => {
    const onSubmit = vi.fn();
    const user = userEvent.setup();
    render(
      <ChatPanel
        scenarioName="카페 주문"
        dialog={dialog}
        isTerminal={false}
        isPending={false}
        onSubmit={onSubmit}
        onHome={() => {}}
      />,
    );

    await user.type(screen.getByRole("textbox"), "다음 입력{Enter}");

    expect(onSubmit).toHaveBeenCalledWith("다음 입력");
  });

  it("calls onHome when 로비로 가기 button is clicked", async () => {
    const onHome = vi.fn();
    const user = userEvent.setup();
    render(
      <ChatPanel
        scenarioName="카페 주문"
        dialog={dialog}
        isTerminal={false}
        isPending={false}
        onSubmit={() => {}}
        onHome={onHome}
      />,
    );

    await user.click(screen.getByRole("button", { name: "로비로 가기" }));

    expect(onHome).toHaveBeenCalledOnce();
  });
});

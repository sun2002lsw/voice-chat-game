import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { ChatInput } from "./ChatInput";

describe("ChatInput", () => {
  it("calls onSubmit with text when 전송 is clicked", async () => {
    const onSubmit = vi.fn();
    const user = userEvent.setup();
    render(
      <ChatInput onSubmit={onSubmit} disabled={false} submitDisabled={false} />,
    );

    await user.type(screen.getByRole("textbox"), "안녕하세요");
    await user.click(screen.getByRole("button", { name: "전송" }));

    expect(onSubmit).toHaveBeenCalledOnce();
    expect(onSubmit).toHaveBeenCalledWith("안녕하세요");
  });

  it("submits on Enter key", async () => {
    const onSubmit = vi.fn();
    const user = userEvent.setup();
    render(
      <ChatInput onSubmit={onSubmit} disabled={false} submitDisabled={false} />,
    );

    await user.type(screen.getByRole("textbox"), "엔터로 보냄{Enter}");

    expect(onSubmit).toHaveBeenCalledOnce();
    expect(onSubmit).toHaveBeenCalledWith("엔터로 보냄");
  });

  it("inserts newline on Shift+Enter and does not submit", async () => {
    const onSubmit = vi.fn();
    const user = userEvent.setup();
    render(
      <ChatInput onSubmit={onSubmit} disabled={false} submitDisabled={false} />,
    );
    const textbox = screen.getByRole("textbox") as HTMLTextAreaElement;

    await user.type(textbox, "첫줄{Shift>}{Enter}{/Shift}둘째줄");

    expect(onSubmit).not.toHaveBeenCalled();
    expect(textbox.value).toBe("첫줄\n둘째줄");
  });

  it("ignores empty submissions", async () => {
    const onSubmit = vi.fn();
    const user = userEvent.setup();
    render(
      <ChatInput onSubmit={onSubmit} disabled={false} submitDisabled={false} />,
    );

    await user.click(screen.getByRole("button", { name: "전송" }));

    expect(onSubmit).not.toHaveBeenCalled();
  });

  it("ignores whitespace-only submissions", async () => {
    const onSubmit = vi.fn();
    const user = userEvent.setup();
    render(
      <ChatInput onSubmit={onSubmit} disabled={false} submitDisabled={false} />,
    );

    await user.type(screen.getByRole("textbox"), "    ");
    await user.click(screen.getByRole("button", { name: "전송" }));

    expect(onSubmit).not.toHaveBeenCalled();
  });

  it("clears input after submit", async () => {
    const onSubmit = vi.fn();
    const user = userEvent.setup();
    render(
      <ChatInput onSubmit={onSubmit} disabled={false} submitDisabled={false} />,
    );
    const input = screen.getByRole("textbox") as HTMLTextAreaElement;

    await user.type(input, "abc");
    await user.click(screen.getByRole("button", { name: "전송" }));

    expect(input.value).toBe("");
  });

  it("disables both textarea and button when disabled prop is true", () => {
    render(
      <ChatInput onSubmit={() => {}} disabled={true} submitDisabled={false} />,
    );

    expect(screen.getByRole("textbox")).toBeDisabled();
    expect(screen.getByRole("button", { name: "전송" })).toBeDisabled();
  });

  it("keeps textarea editable but blocks submit when only submitDisabled", async () => {
    const onSubmit = vi.fn();
    const user = userEvent.setup();
    render(
      <ChatInput onSubmit={onSubmit} disabled={false} submitDisabled={true} />,
    );
    const textbox = screen.getByRole("textbox") as HTMLTextAreaElement;

    expect(textbox).not.toBeDisabled();
    expect(screen.getByRole("button", { name: "전송" })).toBeDisabled();

    await user.type(textbox, "보낼 수 없음{Enter}");

    expect(onSubmit).not.toHaveBeenCalled();
    expect(textbox.value).toBe("보낼 수 없음");
  });
});

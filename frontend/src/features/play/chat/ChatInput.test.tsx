import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { ChatInput } from "./ChatInput";

describe("ChatInput", () => {
  it("calls onSubmit with text when 전송 is clicked", async () => {
    const onSubmit = vi.fn();
    const user = userEvent.setup();
    render(<ChatInput onSubmit={onSubmit} disabled={false} />);

    await user.type(screen.getByRole("textbox"), "안녕하세요");
    await user.click(screen.getByRole("button", { name: "전송" }));

    expect(onSubmit).toHaveBeenCalledOnce();
    expect(onSubmit).toHaveBeenCalledWith("안녕하세요");
  });

  it("submits on Enter key", async () => {
    const onSubmit = vi.fn();
    const user = userEvent.setup();
    render(<ChatInput onSubmit={onSubmit} disabled={false} />);

    await user.type(screen.getByRole("textbox"), "엔터로 보냄{Enter}");

    expect(onSubmit).toHaveBeenCalledOnce();
    expect(onSubmit).toHaveBeenCalledWith("엔터로 보냄");
  });

  it("ignores empty submissions", async () => {
    const onSubmit = vi.fn();
    const user = userEvent.setup();
    render(<ChatInput onSubmit={onSubmit} disabled={false} />);

    await user.click(screen.getByRole("button", { name: "전송" }));

    expect(onSubmit).not.toHaveBeenCalled();
  });

  it("clears input after submit", async () => {
    const onSubmit = vi.fn();
    const user = userEvent.setup();
    render(<ChatInput onSubmit={onSubmit} disabled={false} />);
    const input = screen.getByRole("textbox") as HTMLInputElement;

    await user.type(input, "abc");
    await user.click(screen.getByRole("button", { name: "전송" }));

    expect(input.value).toBe("");
  });

  it("disables input and button when disabled prop is true", () => {
    render(<ChatInput onSubmit={() => {}} disabled={true} />);

    expect(screen.getByRole("textbox")).toBeDisabled();
    expect(screen.getByRole("button", { name: "전송" })).toBeDisabled();
  });
});

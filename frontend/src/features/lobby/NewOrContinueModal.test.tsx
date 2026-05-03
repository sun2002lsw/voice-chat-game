import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { NewOrContinueModal } from "./NewOrContinueModal";

const baseProps = {
  scenarioName: "test_cafe",
  onNewGame: () => {},
  onContinue: () => {},
  onClose: () => {},
};

describe("NewOrContinueModal", () => {
  it("renders the scenario name", () => {
    render(<NewOrContinueModal {...baseProps} />);

    expect(screen.getByText("test_cafe")).toBeInTheDocument();
  });

  it("calls onNewGame when 새로하기 is clicked", async () => {
    const onNewGame = vi.fn();
    const user = userEvent.setup();
    render(<NewOrContinueModal {...baseProps} onNewGame={onNewGame} />);

    await user.click(screen.getByRole("button", { name: "새로하기" }));

    expect(onNewGame).toHaveBeenCalledOnce();
  });

  it("calls onContinue when 이어하기 is clicked", async () => {
    const onContinue = vi.fn();
    const user = userEvent.setup();
    render(<NewOrContinueModal {...baseProps} onContinue={onContinue} />);

    await user.click(screen.getByRole("button", { name: "이어하기" }));

    expect(onContinue).toHaveBeenCalledOnce();
  });

  it("calls onClose when 닫기 is clicked", async () => {
    const onClose = vi.fn();
    const user = userEvent.setup();
    render(<NewOrContinueModal {...baseProps} onClose={onClose} />);

    await user.click(screen.getByRole("button", { name: "닫기" }));

    expect(onClose).toHaveBeenCalledOnce();
  });
});

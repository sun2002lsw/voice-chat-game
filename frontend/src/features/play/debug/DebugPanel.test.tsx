import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import type { StateLogEntry } from "../../../types";

import { DebugPanel } from "./DebugPanel";

const startEntry: StateLogEntry = {
  step_name: "1. 인사",
  conditions: ["주문", "메뉴 질문"],
  next_step_names: ["2. 결제", "1. 안내"],
  character_script: "어서오세요",
  selected_index: null,
};

const completedEntry: StateLogEntry = {
  ...startEntry,
  selected_index: 0,
};

describe("DebugPanel", () => {
  it("renders nothing notable when state_log is empty", () => {
    const { container } = render(<DebugPanel stateLog={[]} />);

    expect(container.querySelectorAll("[data-block]").length).toBe(0);
  });

  it("renders one block per state_log entry", () => {
    render(<DebugPanel stateLog={[startEntry, completedEntry]} />);

    const blocks = screen.getAllByTestId("debug-block");
    expect(blocks).toHaveLength(2);
  });

  it("shows all step-info fields in a block", () => {
    render(<DebugPanel stateLog={[startEntry]} />);

    const block = screen.getByTestId("debug-block");
    expect(block).toHaveTextContent("1. 인사");
    expect(block).toHaveTextContent("주문");
    expect(block).toHaveTextContent("메뉴 질문");
    expect(block).toHaveTextContent("2. 결제");
    expect(block).toHaveTextContent("1. 안내");
    expect(block).toHaveTextContent("어서오세요");
  });

  it("shows selected_index when filled", () => {
    render(<DebugPanel stateLog={[completedEntry]} />);

    const block = screen.getByTestId("debug-block");
    expect(block).toHaveTextContent("선택 인덱스");
    expect(block).toHaveTextContent("0");
  });

  it("indicates pending state when selected_index is null", () => {
    render(<DebugPanel stateLog={[startEntry]} />);

    const block = screen.getByTestId("debug-block");
    expect(block).toHaveTextContent("대기 중");
  });
});

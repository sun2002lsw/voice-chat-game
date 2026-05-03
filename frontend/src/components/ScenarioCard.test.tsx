import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import type { ScenarioSummary } from "../types";

import { ScenarioCard } from "./ScenarioCard";

const baseScenario: ScenarioSummary = {
  name: "test_cafe",
  profile_url: "/api/scenarios/test_cafe/profile",
  has_progress: false,
};

describe("ScenarioCard", () => {
  it("renders scenario name", () => {
    render(<ScenarioCard scenario={baseScenario} onClick={() => {}} />);

    expect(screen.getByText("test_cafe")).toBeInTheDocument();
  });

  it("renders profile image with profile_url as src", () => {
    render(<ScenarioCard scenario={baseScenario} onClick={() => {}} />);

    const img = screen.getByRole("img");
    expect(img).toHaveAttribute("src", "/api/scenarios/test_cafe/profile");
  });

  it("calls onClick when the card is clicked", async () => {
    const onClick = vi.fn();
    const user = userEvent.setup();
    render(<ScenarioCard scenario={baseScenario} onClick={onClick} />);

    await user.click(screen.getByRole("button"));

    expect(onClick).toHaveBeenCalledOnce();
  });

  it("shows a progress badge when has_progress is true", () => {
    render(
      <ScenarioCard
        scenario={{ ...baseScenario, has_progress: true }}
        onClick={() => {}}
      />,
    );

    expect(screen.getByText("진행 중")).toBeInTheDocument();
  });

  it("does not show a progress badge when has_progress is false", () => {
    render(<ScenarioCard scenario={baseScenario} onClick={() => {}} />);

    expect(screen.queryByText("진행 중")).not.toBeInTheDocument();
  });
});

import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { MemoryRouter, Route, Routes, useLocation } from "react-router-dom";
import { describe, expect, it } from "vitest";

import { sampleStep } from "../../test/mocks/handlers";
import { server } from "../../test/mocks/server";

import { Play } from "./Play";

function LocationProbe() {
  const location = useLocation();
  return <div data-testid="location">{location.pathname}</div>;
}

function renderPlay(name: string, firstStepName: string) {
  return render(
    <MemoryRouter
      initialEntries={[{ pathname: `/play/${encodeURIComponent(name)}`, state: { firstStepName } }]}
    >
      <Routes>
        <Route path="/play/:name" element={<Play />} />
        <Route path="/" element={<LocationProbe />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("Play", () => {
  it("fetches first step on mount and shows script", async () => {
    renderPlay("test_cafe", "1. 인사");

    const matches = await screen.findAllByText("어서오세요");
    expect(matches.length).toBeGreaterThan(0);
  });

  it("redirects to lobby when no navigation state", async () => {
    render(
      <MemoryRouter initialEntries={["/play/test_cafe"]}>
        <Routes>
          <Route path="/play/:name" element={<Play />} />
          <Route path="/" element={<LocationProbe />} />
        </Routes>
      </MemoryRouter>,
    );

    await waitFor(() => {
      expect(screen.getByTestId("location")).toHaveTextContent("/");
    });
  });

  it("navigates to next step on number key press", async () => {
    const nextStep = {
      ...sampleStep,
      step_name: "2. 결제",
      script: "결제 도와드릴게요",
      is_terminal: true,
      conditions: [],
      next_step_names: [],
    };
    server.use(
      http.get("/api/scenarios/:name/steps/2.%20%EA%B2%B0%EC%A0%9C", () =>
        HttpResponse.json(nextStep),
      ),
    );

    const user = userEvent.setup();
    renderPlay("test_cafe", "1. 인사");

    await screen.findAllByText("어서오세요");
    await user.keyboard("0");

    await screen.findAllByText("결제 도와드릴게요");
  });

  it("shows 종료 when step is terminal", async () => {
    server.use(
      http.get("/api/scenarios/:name/steps/:step", () =>
        HttpResponse.json({ ...sampleStep, is_terminal: true, next_step_names: [] }),
      ),
    );
    renderPlay("test_cafe", "1. 인사");
    expect(await screen.findByText("종료")).toBeInTheDocument();
  });
});

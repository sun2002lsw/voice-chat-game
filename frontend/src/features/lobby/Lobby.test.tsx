import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { MemoryRouter, Route, Routes, useLocation } from "react-router-dom";
import { describe, expect, it } from "vitest";

import { server } from "../../test/mocks/server";

import { Lobby } from "./Lobby";

function LocationProbe() {
  const location = useLocation();
  return <div data-testid="location">{location.pathname}</div>;
}

function renderLobby() {
  return render(
    <MemoryRouter initialEntries={["/"]}>
      <Routes>
        <Route path="/" element={<Lobby />} />
        <Route path="*" element={<LocationProbe />} />
      </Routes>
    </MemoryRouter>,
  );
}

const scenarios = [
  { name: "cafe", profile_url: "/api/scenarios/cafe/profile", first_step_name: "1. 인사" },
];

function mockScenarios() {
  server.use(http.get("/api/scenarios", () => HttpResponse.json(scenarios)));
}

describe("Lobby", () => {
  it("renders a card for each scenario", async () => {
    mockScenarios();
    renderLobby();
    expect(await screen.findByText("cafe")).toBeInTheDocument();
  });

  it("clicking a card navigates to play", async () => {
    mockScenarios();
    const user = userEvent.setup();
    renderLobby();
    await user.click(await screen.findByRole("button", { name: /cafe/ }));

    await waitFor(() => {
      expect(screen.getByTestId("location")).toHaveTextContent("/play/cafe");
    });
  });

  it("shows an alert when fetchScenarios fails", async () => {
    server.use(
      http.get("/api/scenarios", () =>
        HttpResponse.json({ detail: "boom" }, { status: 500 }),
      ),
    );
    renderLobby();
    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent("시나리오 목록을 불러오지 못했습니다.");
  });
});

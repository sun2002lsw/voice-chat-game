import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import {
  MemoryRouter,
  Route,
  Routes,
  useLocation,
} from "react-router-dom";
import { describe, expect, it } from "vitest";

import { sampleState } from "../../test/mocks/handlers";
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
  {
    name: "cafe",
    profile_url: "/api/scenarios/cafe/profile",
  },
  {
    name: "interview",
    profile_url: "/api/scenarios/interview/profile",
  },
];

function mockScenarios() {
  server.use(
    http.get("/api/scenarios", () => HttpResponse.json(scenarios)),
  );
}

describe("Lobby", () => {
  it("renders a card for each scenario", async () => {
    mockScenarios();
    renderLobby();

    expect(await screen.findByText("cafe")).toBeInTheDocument();
    expect(screen.getByText("interview")).toBeInTheDocument();
  });

  it("clicking a card starts a new game and navigates", async () => {
    mockScenarios();
    server.use(
      http.post("/api/scenarios/:name/new", () =>
        HttpResponse.json(sampleState),
      ),
    );

    const user = userEvent.setup();
    renderLobby();
    const card = await screen.findByRole("button", { name: /cafe/ });

    await user.click(card);

    await waitFor(() => {
      expect(screen.getByTestId("location")).toHaveTextContent("/play/cafe");
    });
  });

  it("shows an alert when fetchScenarios fails with 5xx", async () => {
    server.use(
      http.get("/api/scenarios", () =>
        HttpResponse.json({ detail: "boom" }, { status: 500 }),
      ),
    );

    renderLobby();

    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent("시나리오 목록을 불러오지 못했습니다.");
  });

  it("shows an alert when startNew fails", async () => {
    mockScenarios();
    server.use(
      http.post("/api/scenarios/:name/new", () =>
        HttpResponse.json({ detail: "boom" }, { status: 500 }),
      ),
    );

    const user = userEvent.setup();
    renderLobby();
    await user.click(await screen.findByRole("button", { name: /cafe/ }));

    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent("새 게임을 시작하지 못했습니다.");
  });
});

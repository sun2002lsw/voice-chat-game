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
    name: "no_progress_cafe",
    profile_url: "/api/scenarios/no_progress_cafe/profile",
    has_progress: false,
  },
  {
    name: "with_progress_interview",
    profile_url: "/api/scenarios/with_progress_interview/profile",
    has_progress: true,
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

    expect(await screen.findByText("no_progress_cafe")).toBeInTheDocument();
    expect(screen.getByText("with_progress_interview")).toBeInTheDocument();
  });

  it("clicking a card without progress starts a new game and navigates", async () => {
    mockScenarios();
    server.use(
      http.post("/api/scenarios/:name/new", () =>
        HttpResponse.json(sampleState),
      ),
    );

    const user = userEvent.setup();
    renderLobby();
    const card = await screen.findByRole("button", { name: /no_progress_cafe/ });

    await user.click(card);

    await waitFor(() => {
      expect(screen.getByTestId("location")).toHaveTextContent(
        "/play/no_progress_cafe",
      );
    });
  });

  it("clicking a card with progress opens the modal", async () => {
    mockScenarios();
    const user = userEvent.setup();
    renderLobby();
    const card = await screen.findByRole("button", {
      name: /with_progress_interview/,
    });

    await user.click(card);

    expect(screen.getByRole("dialog")).toBeInTheDocument();
  });

  it("modal '이어하기' resumes the session and navigates", async () => {
    mockScenarios();
    server.use(
      http.post("/api/scenarios/:name/continue", () =>
        HttpResponse.json(sampleState),
      ),
    );

    const user = userEvent.setup();
    renderLobby();
    await user.click(
      await screen.findByRole("button", { name: /with_progress_interview/ }),
    );
    await user.click(screen.getByRole("button", { name: "이어하기" }));

    await waitFor(() => {
      expect(screen.getByTestId("location")).toHaveTextContent(
        "/play/with_progress_interview",
      );
    });
  });

  it("modal '새로하기' starts a new game and navigates", async () => {
    mockScenarios();
    server.use(
      http.post("/api/scenarios/:name/new", () =>
        HttpResponse.json(sampleState),
      ),
    );

    const user = userEvent.setup();
    renderLobby();
    await user.click(
      await screen.findByRole("button", { name: /with_progress_interview/ }),
    );
    await user.click(screen.getByRole("button", { name: "새로하기" }));

    await waitFor(() => {
      expect(screen.getByTestId("location")).toHaveTextContent(
        "/play/with_progress_interview",
      );
    });
  });

  it("modal '닫기' closes the modal", async () => {
    mockScenarios();
    const user = userEvent.setup();
    renderLobby();
    await user.click(
      await screen.findByRole("button", { name: /with_progress_interview/ }),
    );
    await user.click(screen.getByRole("button", { name: "닫기" }));

    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
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
});

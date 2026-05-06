import { fireEvent, render, screen, waitFor } from "@testing-library/react";
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

import { Play } from "./Play";

function LocationProbe() {
  const location = useLocation();
  return <div data-testid="location">{location.pathname}</div>;
}

function renderPlay(name: string) {
  return render(
    <MemoryRouter initialEntries={[`/play/${encodeURIComponent(name)}`]}>
      <Routes>
        <Route path="/play/:name" element={<Play />} />
        <Route path="/" element={<LocationProbe />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("Play", () => {
  it("fetches state on mount and shows the character dialog", async () => {
    server.use(
      http.get("/api/scenarios/:name/state", () =>
        HttpResponse.json(sampleState),
      ),
    );

    renderPlay("test_cafe");

    const matches = await screen.findAllByText("어서오세요");
    expect(matches.length).toBeGreaterThan(0);
  });

  it("redirects to lobby when fetchState 404s", async () => {
    server.use(
      http.get("/api/scenarios/:name/state", () =>
        HttpResponse.json({ detail: "not found" }, { status: 404 }),
      ),
    );

    renderPlay("test_cafe");

    await waitFor(() => {
      expect(screen.getByTestId("location")).toHaveTextContent("/");
    });
  });

  it("submits input and renders the new state", async () => {
    const updatedState = {
      ...sampleState,
      current_step_name: "2. 결제",
      dialog: [
        ...sampleState.dialog,
        {
          role: "user" as const,
          text: "주문할게요",
          created_at: "2026-05-03T14:01:00Z",
        },
        {
          role: "character" as const,
          text: "결제 도와드릴게요",
          created_at: "2026-05-03T14:01:01Z",
        },
      ],
    };
    server.use(
      http.get("/api/scenarios/:name/state", () =>
        HttpResponse.json(sampleState),
      ),
      http.post("/api/scenarios/:name/input", () =>
        HttpResponse.json(updatedState),
      ),
    );

    const user = userEvent.setup();
    renderPlay("test_cafe");

    await screen.findAllByText("어서오세요");
    await user.type(screen.getByRole("textbox"), "주문할게요{Enter}");

    const updated = await screen.findAllByText("결제 도와드릴게요");
    expect(updated.length).toBeGreaterThan(0);
  });

  it("disables input when is_terminal is true", async () => {
    server.use(
      http.get("/api/scenarios/:name/state", () =>
        HttpResponse.json({ ...sampleState, is_terminal: true }),
      ),
    );

    renderPlay("test_cafe");

    await screen.findAllByText("어서오세요");
    expect(screen.getByRole("textbox")).toBeDisabled();
  });

  it("shows an alert (and does not redirect) when fetchState 5xx", async () => {
    server.use(
      http.get("/api/scenarios/:name/state", () =>
        HttpResponse.json({ detail: "boom" }, { status: 500 }),
      ),
    );

    renderPlay("test_cafe");

    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent("진행 상태를 불러오지 못했습니다.");
    // LocationProbe renders only on path "/", so its absence confirms no redirect
    expect(screen.queryByTestId("location")).toBeNull();
  });

  it("auto-advances when audio ends and is_auto_advance is true", async () => {
    const autoAdvanceState = { ...sampleState, is_auto_advance: true };
    const advancedState = {
      ...sampleState,
      is_auto_advance: false,
      current_step_name: "2. 안내",
      dialog: [
        ...sampleState.dialog,
        {
          role: "character" as const,
          text: "안내드립니다",
          created_at: "2026-05-03T14:01:00Z",
        },
      ],
    };
    let advanceCalled = false;
    server.use(
      http.get("/api/scenarios/:name/state", () =>
        HttpResponse.json(autoAdvanceState),
      ),
      http.post("/api/scenarios/:name/advance", () => {
        advanceCalled = true;
        return HttpResponse.json(advancedState);
      }),
    );

    const { container } = renderPlay("test_cafe");

    await screen.findAllByText("어서오세요");
    const audio = container.querySelector("audio");
    expect(audio).not.toBeNull();
    fireEvent.ended(audio!);

    await screen.findAllByText("안내드립니다");
    expect(advanceCalled).toBe(true);
  });

  it("does not auto-advance when is_auto_advance is false", async () => {
    let advanceCalled = false;
    server.use(
      http.get("/api/scenarios/:name/state", () =>
        HttpResponse.json(sampleState),
      ),
      http.post("/api/scenarios/:name/advance", () => {
        advanceCalled = true;
        return HttpResponse.json(sampleState);
      }),
    );

    const { container } = renderPlay("test_cafe");

    await screen.findAllByText("어서오세요");
    const audio = container.querySelector("audio");
    fireEvent.ended(audio!);

    // give pending advance a chance to fire (it shouldn't)
    await new Promise((r) => setTimeout(r, 50));
    expect(advanceCalled).toBe(false);
  });

  it("shows an alert when submitInput fails", async () => {
    server.use(
      http.get("/api/scenarios/:name/state", () =>
        HttpResponse.json(sampleState),
      ),
      http.post("/api/scenarios/:name/input", () =>
        HttpResponse.json({ detail: "boom" }, { status: 500 }),
      ),
    );

    const user = userEvent.setup();
    renderPlay("test_cafe");

    await screen.findAllByText("어서오세요");
    await user.type(screen.getByRole("textbox"), "주문할게요{Enter}");

    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent("전송에 실패했습니다.");
  });
});

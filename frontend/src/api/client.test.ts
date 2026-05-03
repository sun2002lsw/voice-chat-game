import { http, HttpResponse } from "msw";
import { describe, expect, it } from "vitest";

import { sampleScenario, sampleState } from "../test/mocks/handlers";
import { server } from "../test/mocks/server";

import {
  fetchScenarios,
  fetchState,
  resumeSession,
  startNew,
  submitInput,
} from "./client";

describe("fetchScenarios", () => {
  it("returns the scenario list from /api/scenarios", async () => {
    const result = await fetchScenarios();

    expect(result).toEqual([sampleScenario]);
  });
});

describe("startNew", () => {
  it("returns SessionState from POST /api/scenarios/{name}/new", async () => {
    const result = await startNew("test_cafe");

    expect(result).toEqual(sampleState);
  });

  it("URL-encodes a Korean scenario name", async () => {
    let receivedPath = "";
    server.use(
      http.post("/api/scenarios/:name/new", ({ request }) => {
        receivedPath = new URL(request.url).pathname;
        return HttpResponse.json(sampleState);
      }),
    );

    await startNew("회사 면접");

    expect(receivedPath).toBe(
      "/api/scenarios/%ED%9A%8C%EC%82%AC%20%EB%A9%B4%EC%A0%91/new",
    );
  });
});

describe("resumeSession", () => {
  it("returns SessionState from POST /api/scenarios/{name}/continue", async () => {
    const result = await resumeSession("test_cafe");

    expect(result).toEqual(sampleState);
  });

  it("throws when backend responds 404", async () => {
    server.use(
      http.post("/api/scenarios/:name/continue", () =>
        HttpResponse.json({ detail: "not found" }, { status: 404 }),
      ),
    );

    await expect(resumeSession("test_cafe")).rejects.toThrow();
  });
});

describe("fetchState", () => {
  it("returns SessionState from GET /api/scenarios/{name}/state", async () => {
    const result = await fetchState("test_cafe");

    expect(result).toEqual(sampleState);
  });

  it("throws when backend responds 404", async () => {
    server.use(
      http.get("/api/scenarios/:name/state", () =>
        HttpResponse.json({ detail: "not found" }, { status: 404 }),
      ),
    );

    await expect(fetchState("test_cafe")).rejects.toThrow();
  });
});

describe("submitInput", () => {
  it("posts {text} body and returns SessionState", async () => {
    let receivedBody: unknown;
    server.use(
      http.post("/api/scenarios/:name/input", async ({ request }) => {
        receivedBody = await request.json();
        return HttpResponse.json(sampleState);
      }),
    );

    const result = await submitInput("test_cafe", "안녕하세요");

    expect(receivedBody).toEqual({ text: "안녕하세요" });
    expect(result).toEqual(sampleState);
  });
});

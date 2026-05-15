import { http, HttpResponse } from "msw";
import { describe, expect, it } from "vitest";

import { sampleScenario, sampleStep } from "../test/mocks/handlers";
import { server } from "../test/mocks/server";

import { fetchScenarios, fetchStep } from "./client";

describe("fetchScenarios", () => {
  it("returns the scenario list from /api/scenarios", async () => {
    const result = await fetchScenarios();
    expect(result).toEqual([sampleScenario]);
  });
});

describe("fetchStep", () => {
  it("returns StepInfo from /api/scenarios/{name}/steps/{step}", async () => {
    const result = await fetchStep("test_cafe", "1. 인사");
    expect(result).toEqual(sampleStep);
  });

  it("URL-encodes the step name", async () => {
    let receivedPath = "";
    server.use(
      http.get("/api/scenarios/:name/steps/:step", ({ request }) => {
        receivedPath = new URL(request.url).pathname;
        return HttpResponse.json(sampleStep);
      }),
    );

    await fetchStep("test_cafe", "1. 인사");

    expect(receivedPath).toContain("1.%20%EC%9D%B8%EC%82%AC");
  });

  it("throws when backend responds 404", async () => {
    server.use(
      http.get("/api/scenarios/:name/steps/:step", () =>
        HttpResponse.json({ detail: "not found" }, { status: 404 }),
      ),
    );

    await expect(fetchStep("test_cafe", "ghost")).rejects.toThrow();
  });
});

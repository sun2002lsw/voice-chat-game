import type { HttpHandler } from "msw";
import { http, HttpResponse } from "msw";

import type { ScenarioSummary, StepInfo } from "../../types";

export const sampleScenario: ScenarioSummary = {
  name: "test_cafe",
  profile_url: "/api/scenarios/test_cafe/profile",
  first_step_name: "1. 인사",
};

export const sampleStep: StepInfo = {
  step_name: "1. 인사",
  is_terminal: false,
  loop: false,
  picture_url: "/api/scenarios/test_cafe/steps/1.%20%EC%9D%B8%EC%82%AC/picture",
  script: "어서오세요",
  voice_url: "/api/scenarios/test_cafe/steps/1.%20%EC%9D%B8%EC%82%AC/voice",
  conditions: ["주문"],
  next_step_names: ["2. 결제"],
};

export const handlers: HttpHandler[] = [
  http.get("/api/scenarios", () => HttpResponse.json([sampleScenario])),
  http.get("/api/scenarios/:name/steps/:step", () => HttpResponse.json(sampleStep)),
];

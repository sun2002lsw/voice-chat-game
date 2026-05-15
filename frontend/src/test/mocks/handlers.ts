import type { HttpHandler } from "msw";
import { http, HttpResponse } from "msw";

import type { ScenarioSummary, SessionState } from "../../types";


export const sampleScenario: ScenarioSummary = {
  name: "test_cafe",
  profile_url: "/api/scenarios/test_cafe/profile",
};

export const sampleState: SessionState = {
  scenario_name: "test_cafe",
  current_step_name: "1. 인사",
  is_terminal: false,
  profile_url: "/api/scenarios/test_cafe/profile",
  picture_url: "/api/scenarios/test_cafe/picture",
  scripts: ["어서오세요"],
  voice_urls: ["/api/scenarios/test_cafe/voice/0"],
  dialog: ["어서오세요"],
  state_log: [
    {
      step_name: "1. 인사",
      conditions: ["주문"],
      next_step_names: ["2. 결제"],
      character_script: "어서오세요",
      selected_index: null,
    },
  ],
};

export const handlers: HttpHandler[] = [
  http.get("/api/scenarios", () => HttpResponse.json([sampleScenario])),
  http.post("/api/scenarios/:name/new", () => HttpResponse.json(sampleState)),
  http.get("/api/scenarios/:name/state", () => HttpResponse.json(sampleState)),
  http.post("/api/scenarios/:name/input", () => HttpResponse.json(sampleState)),
];

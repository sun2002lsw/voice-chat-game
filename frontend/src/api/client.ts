import type { ScenarioSummary, StepInfo } from "../types";

const BASE = "";

export class HttpError extends Error {
  readonly status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "HttpError";
    this.status = status;
  }
}

export async function fetchScenarios(): Promise<ScenarioSummary[]> {
  return getJson<ScenarioSummary[]>("/api/scenarios");
}

export async function fetchStep(
  scenarioName: string,
  stepName: string,
): Promise<StepInfo> {
  return getJson<StepInfo>(
    `/api/scenarios/${encodeURIComponent(scenarioName)}/steps/${encodeURIComponent(stepName)}`,
  );
}

async function getJson<T>(path: string): Promise<T> {
  const resp = await fetch(`${BASE}${path}`);
  if (!resp.ok) {
    const detail = await safeReadText(resp);
    throw new HttpError(`GET ${path} failed: ${resp.status} ${detail}`, resp.status);
  }
  return resp.json() as Promise<T>;
}

async function safeReadText(resp: Response): Promise<string> {
  try {
    return await resp.text();
  } catch {
    return "";
  }
}

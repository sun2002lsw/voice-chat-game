import type { ScenarioSummary, SessionState } from "../types";

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

export async function startNew(name: string): Promise<SessionState> {
  return postJson<SessionState>(scenarioPath(name, "/new"));
}

export async function fetchState(name: string): Promise<SessionState> {
  return getJson<SessionState>(scenarioPath(name, "/state"));
}

export async function submitInput(
  name: string,
  index: number,
): Promise<SessionState> {
  return postJson<SessionState>(scenarioPath(name, "/input"), { index });
}

async function getJson<T>(path: string): Promise<T> {
  const resp = await fetch(`${BASE}${path}`);
  if (!resp.ok) {
    const detail = await safeReadText(resp);
    throw new HttpError(
      `GET ${path} failed: ${resp.status} ${detail}`,
      resp.status,
    );
  }

  return resp.json() as Promise<T>;
}

async function postJson<T>(path: string, body?: unknown): Promise<T> {
  const init: RequestInit = {
    method: "POST",
    headers: { "content-type": "application/json" },
  };
  if (body !== undefined) {
    init.body = JSON.stringify(body);
  }

  const resp = await fetch(`${BASE}${path}`, init);
  if (!resp.ok) {
    const detail = await safeReadText(resp);
    throw new HttpError(
      `POST ${path} failed: ${resp.status} ${detail}`,
      resp.status,
    );
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

function scenarioPath(name: string, suffix: string): string {
  return `/api/scenarios/${encodeURIComponent(name)}${suffix}`;
}

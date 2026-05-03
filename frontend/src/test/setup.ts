import "@testing-library/jest-dom";

import { afterAll, afterEach, beforeAll, vi } from "vitest";

import { server } from "./mocks/server";

beforeAll(() => server.listen({ onUnhandledRequest: "error" }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

// jsdom 미지원 API mock
Element.prototype.scrollIntoView = vi.fn();

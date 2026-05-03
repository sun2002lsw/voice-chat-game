import type { HttpHandler } from "msw";

// 기본 핸들러 모음. 각 테스트가 server.use() 로 덮어쓰는 패턴.
export const handlers: HttpHandler[] = [];

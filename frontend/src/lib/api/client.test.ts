import { afterEach, describe, expect, it, vi } from "vitest";

import { request } from "./client";

describe("request auth header", () => {
  afterEach(() => {
    vi.unstubAllEnvs();
    vi.restoreAllMocks();
  });

  it("sends Authorization when VITE_API_TOKEN is set", async () => {
    vi.stubEnv("VITE_API_TOKEN", "frontend-test-token");
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      headers: new Headers({ "content-type": "application/json" }),
      json: async () => ({ ok: true }),
    });
    vi.stubGlobal("fetch", fetchMock);

    await request("/api/health");

    expect(fetchMock).toHaveBeenCalledOnce();
    const init = fetchMock.mock.calls[0][1] as RequestInit;
    expect(init.headers).toMatchObject({
      Authorization: "Bearer frontend-test-token",
    });
  });
});

import { describe, expect, it, vi } from "vitest";
import { api } from "./api";

describe("API client", () => {
  it("sends idempotency key when creating incidents", async () => {
    global.fetch = vi.fn().mockResolvedValue({ ok: true, text: async () => JSON.stringify({ id: "INC-1" }) });
    await api.createIncident({ summary: "synthetic" }, "key-12345678");
    expect(fetch.mock.calls[0][1].headers["Idempotency-Key"]).toBe("key-12345678");
  });
  it("preserves structured API errors", async () => {
    global.fetch = vi.fn().mockResolvedValue({ ok: false, status: 400, text: async () => JSON.stringify({ error: { code: "INVALID_INPUT", message: "bad" }, request_id: "req-1" }) });
    await expect(api.health()).rejects.toMatchObject({ code: "INVALID_INPUT", requestId: "req-1" });
  });
});

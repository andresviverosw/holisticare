import { describe, expect, it } from "vitest";
import { buildInviteRedeemPath, inviteTokenFromSearch } from "./inviteUrl";

describe("inviteUrl", () => {
  it("builds login redeem path with encoded token", () => {
    expect(buildInviteRedeemPath("abc+/=")).toBe("/login?invite=abc%2B%2F%3D");
    expect(buildInviteRedeemPath("")).toBe("/login");
  });

  it("parses invite token from search string", () => {
    expect(inviteTokenFromSearch("?invite=secret-token")).toBe("secret-token");
    expect(inviteTokenFromSearch("invite=secret-token")).toBe("secret-token");
    expect(inviteTokenFromSearch("")).toBe("");
    expect(inviteTokenFromSearch("?foo=1")).toBe("");
  });
});

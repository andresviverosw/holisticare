/**
 * US-DIARY-AUTH-PROD — build Login redeem URLs from invite tokens.
 */

export function buildInviteRedeemPath(token) {
  const raw = String(token || "").trim();
  if (!raw) return "/login";
  return `/login?invite=${encodeURIComponent(raw)}`;
}

export function inviteTokenFromSearch(search) {
  const params = new URLSearchParams(
    typeof search === "string" ? search.replace(/^\?/, "") : String(search || ""),
  );
  const token = params.get("invite");
  return token ? token.trim() : "";
}

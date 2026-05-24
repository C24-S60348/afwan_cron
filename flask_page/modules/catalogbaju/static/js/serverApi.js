/**
 * Server API helpers for shared catalog data.
 */

const CATALOG_API_PATH = "api/catalog";
const ASK_OWNER_API_PATH = "api/ask-owner";
const GUEST_CARTS_API_PATH = "api/guest-carts";

export async function loadServerCatalog() {
  try {
    const res = await fetch(CATALOG_API_PATH, { cache: "no-store" });
    if (!res.ok) return null;
    const data = await res.json();
    return Array.isArray(data?.items) ? data.items : null;
  } catch (_) {
    return null;
  }
}

export async function saveServerCatalog(items) {
  if (!Array.isArray(items)) return false;
  try {
    const res = await fetch(CATALOG_API_PATH, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ items }),
    });
    return res.ok;
  } catch (_) {
    return false;
  }
}

export async function loadServerAskOwnerRequests() {
  try {
    const res = await fetch(ASK_OWNER_API_PATH, { cache: "no-store" });
    if (!res.ok) return null;
    const data = await res.json();
    return Array.isArray(data?.items) ? data.items : null;
  } catch (_) {
    return null;
  }
}

export async function saveServerAskOwnerRequests(items) {
  if (!Array.isArray(items)) return false;
  try {
    const res = await fetch(ASK_OWNER_API_PATH, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ items }),
    });
    return res.ok;
  } catch (_) {
    return false;
  }
}

export async function loadServerGuestCarts() {
  try {
    const res = await fetch(GUEST_CARTS_API_PATH, { cache: "no-store" });
    if (!res.ok) return null;
    const data = await res.json();
    return data?.items && typeof data.items === "object" ? data.items : null;
  } catch (_) {
    return null;
  }
}

export async function saveServerGuestCarts(items) {
  if (!items || typeof items !== "object") return false;
  try {
    const res = await fetch(GUEST_CARTS_API_PATH, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ items }),
    });
    return res.ok;
  } catch (_) {
    return false;
  }
}

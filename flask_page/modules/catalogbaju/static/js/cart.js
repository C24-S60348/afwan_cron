/**
 * Cart, guest carts, sync, render cart modal, send to owner, guest cart modal.
 */
import { state } from "./state.js";
import { STORAGE_KEY_GUEST_ID, STORAGE_KEY_GUEST_CARTS } from "./config.js";
import { escapeHtml, escapeAttr } from "./utils.js";
import { getItemImage } from "./catalog.js";
import { saveServerGuestCarts } from "./serverApi.js";

export function getGuestId() {
  if (state.guestId) return state.guestId;
  try {
    state.guestId = localStorage.getItem(STORAGE_KEY_GUEST_ID);
    if (!state.guestId) {
      state.guestId = "guest_" + Date.now() + "_" + Math.random().toString(36).slice(2, 9);
      localStorage.setItem(STORAGE_KEY_GUEST_ID, state.guestId);
    }
  } catch (_) {
    state.guestId = "guest_" + Date.now();
  }
  return state.guestId;
}

export function loadGuestCarts() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY_GUEST_CARTS);
    state.guestCarts = raw ? JSON.parse(raw) : {};
  } catch (_) {
    state.guestCarts = {};
  }
}

export function saveGuestCarts() {
  try {
    localStorage.setItem(STORAGE_KEY_GUEST_CARTS, JSON.stringify(state.guestCarts));
  } catch (_) {}
  void saveServerGuestCarts(state.guestCarts);
}

export function syncCartToGuest() {
  const gid = getGuestId();
  const label = "Guest";
  if (!state.guestCarts[gid]) state.guestCarts[gid] = { guestLabel: label, cart: [], submittedToOwner: false, updatedAt: "" };
  state.guestCarts[gid].cart = state.cart.slice();
  state.guestCarts[gid].updatedAt = new Date().toISOString();
  saveGuestCarts();
}

export function updateCartCount() {
  const el = document.getElementById("cartCount");
  if (el) el.textContent = state.cart.length;
}

export function renderCartModal(openItemModalByItem) {
  syncCartToGuest();
  const list = document.getElementById("cartList");
  const empty = document.getElementById("cartEmpty");
  const footer = document.querySelector(".cart-modal__footer");
  const sendBtn = document.getElementById("cartSendToOwner");
  if (!list || !empty) return;
  list.innerHTML = "";
  if (state.cart.length === 0) {
    empty.style.display = "block";
    if (footer) footer.style.display = "none";
    return;
  }
  empty.style.display = "none";
  if (footer) footer.style.display = "block";
  const gid = getGuestId();
  const submitted = state.guestCarts[gid]?.submittedToOwner;
  if (sendBtn) {
    sendBtn.disabled = submitted;
    sendBtn.textContent = submitted ? "Sent to owner" : "Send to owner";
  }
  state.cart.forEach((entry, index) => {
    const item = state.allItems.find((i) => String(i.id) === String(entry.id));
    const imgSrc = item ? getItemImage(item) : "";
    const li = document.createElement("li");
    li.className = "cart-modal__item";
    li.innerHTML = `
      <div class="cart-modal__item-img-wrap">
        <img class="cart-modal__item-img" src="${escapeAttr(imgSrc)}" alt="" />
      </div>
      <div class="cart-modal__item-info">
        <span class="cart-modal__item-name">${escapeHtml(entry.name)}</span>
        <span class="cart-modal__item-meta">${escapeHtml(entry.size)} · ${escapeHtml(entry.price)}</span>
        <div class="cart-modal__item-actions">
          <button type="button" class="cart-modal__item-details" data-index="${index}">Details</button>
        </div>
      </div>
      <button type="button" class="cart-modal__item-remove" data-index="${index}" aria-label="Remove">×</button>
    `;
    const removeBtn = li.querySelector(".cart-modal__item-remove");
    const detailsBtn = li.querySelector(".cart-modal__item-details");
    removeBtn.addEventListener("click", () => {
      state.cart.splice(index, 1);
      syncCartToGuest();
      renderCartModal(openItemModalByItem);
      updateCartCount();
    });
    if (detailsBtn && item) {
      detailsBtn.addEventListener("click", () => {
        document.getElementById("cartModal")?.classList.remove("cart-modal--open");
        document.getElementById("cartModal")?.setAttribute("aria-hidden", "true");
        state.openedItemModalFromCart = true;
        openItemModalByItem(item);
      });
    }
    list.appendChild(li);
  });
}

export function openGuestCartModal(guestIdKey, data) {
  const modal = document.getElementById("guestCartModal");
  const titleEl = document.getElementById("guestCartModalTitle");
  const listEl = document.getElementById("guestCartModalList");
  const emptyEl = document.getElementById("guestCartModalEmpty");
  if (!modal || !listEl || !emptyEl) return;
  const label = data.guestLabel || "Guest";
  if (titleEl) titleEl.textContent = label + "'s cart" + (data.submittedToOwner ? " (sent)" : "");
  listEl.innerHTML = "";
  if (!data.cart || data.cart.length === 0) {
    emptyEl.style.display = "block";
  } else {
    emptyEl.style.display = "none";
    data.cart.forEach((entry) => {
      const li = document.createElement("li");
      const item = state.allItems.find((i) => String(i.id) === String(entry.id));
      const imgSrc = item ? getItemImage(item) : "";
      li.innerHTML = `
        <div style="width:48px;height:48px;border-radius:8px;overflow:hidden;flex-shrink:0;"><img src="${escapeAttr(imgSrc)}" alt="" style="width:100%;height:100%;object-fit:cover;" /></div>
        <div><strong>${escapeHtml(entry.name)}</strong><br><span style="color:var(--text-soft);font-size:0.85rem">${escapeHtml(entry.size)} · ${escapeHtml(entry.price)}</span></div>
      `;
      listEl.appendChild(li);
    });
  }
  modal.classList.add("guest-cart-modal--open");
  modal.setAttribute("aria-hidden", "false");
}

export function initCartModal(openItemModalByItem, renderCartModalFn) {
  const modal = document.getElementById("cartModal");
  const openBtn = document.getElementById("cartButton");
  const closeBtn = modal?.querySelector(".cart-modal__close");
  const backdrop = modal?.querySelector(".cart-modal__backdrop");
  const sendBtn = document.getElementById("cartSendToOwner");
  if (!modal || !openBtn) return;
  openBtn.addEventListener("click", () => {
    renderCartModalFn(openItemModalByItem);
    modal.classList.add("cart-modal--open");
    modal.setAttribute("aria-hidden", "false");
  });
  function close() {
    modal.classList.remove("cart-modal--open");
    modal.setAttribute("aria-hidden", "true");
  }
  closeBtn?.addEventListener("click", close);
  backdrop?.addEventListener("click", close);
  sendBtn?.addEventListener("click", () => {
    const gid = getGuestId();
    if (!state.guestCarts[gid]) state.guestCarts[gid] = { guestLabel: "Guest", cart: [], submittedToOwner: false, updatedAt: "" };
    state.guestCarts[gid].cart = state.cart.slice();
    state.guestCarts[gid].submittedToOwner = true;
    state.guestCarts[gid].updatedAt = new Date().toISOString();
    saveGuestCarts();
    sendBtn.disabled = true;
    sendBtn.textContent = "Sent to owner";
  });
}

export function initGuestCartModal() {
  const modal = document.getElementById("guestCartModal");
  const closeBtn = modal?.querySelector(".guest-cart-modal__close");
  const backdrop = modal?.querySelector(".guest-cart-modal__backdrop");
  if (!modal) return;
  function close() {
    modal.classList.remove("guest-cart-modal--open");
    modal.setAttribute("aria-hidden", "true");
  }
  closeBtn?.addEventListener("click", close);
  backdrop?.addEventListener("click", close);
}

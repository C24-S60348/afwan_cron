/**
 * Item detail modal: open, close, size buttons, image carousel, add to cart, ask owner.
 */
import { state } from "./state.js";
import { ALL_SIZES } from "./config.js";
import { getItemImage, getItemImages, getPriceDisplay, getTagColor } from "./catalog.js";
import { updateCartCount, syncCartToGuest } from "./cart.js";

export function renderSizeButtons(item) {
  const container = document.getElementById("itemModalSizeBtns");
  if (!container) return;
  container.innerHTML = "";
  const available = Array.isArray(item.sizes) ? item.sizes : ALL_SIZES;
  const firstAvailable = available[0];
  ALL_SIZES.forEach((size) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "item-modal__size-btn";
    btn.textContent = size;
    if (available.includes(size)) {
      btn.classList.add("item-modal__size-btn--available");
      if (size === firstAvailable) {
        btn.classList.add("item-modal__size-btn--selected");
        state.selectedSizeForModal = size;
      }
      btn.addEventListener("click", () => {
        container.querySelectorAll(".item-modal__size-btn").forEach((b) => b.classList.remove("item-modal__size-btn--selected"));
        btn.classList.add("item-modal__size-btn--selected");
        state.selectedSizeForModal = size;
      });
    } else {
      btn.classList.add("item-modal__size-btn--unavailable");
      btn.setAttribute("data-tooltip", "Sold out");
      btn.disabled = true;
      btn.title = "Sold out";
    }
    container.appendChild(btn);
  });
}

export function updateItemModalImageNav(total) {
  const prev = document.getElementById("itemModalImgPrev");
  const next = document.getElementById("itemModalImgNext");
  const counter = document.getElementById("itemModalImgCounter");
  const showNav = total > 1;
  if (prev) prev.style.display = showNav ? "" : "none";
  if (next) next.style.display = showNav ? "" : "none";
  if (counter) { counter.textContent = showNav ? `${state.itemModalImageIndex + 1} / ${total}` : ""; counter.style.display = showNav ? "" : "none"; }
}

export function cycleItemModalImage(delta, images) {
  if (!images || images.length === 0) return;
  state.itemModalImageIndex = (state.itemModalImageIndex + delta + images.length) % images.length;
  const imageEl = document.getElementById("itemModalImage");
  if (imageEl) imageEl.src = images[state.itemModalImageIndex] || "";
  updateItemModalImageNav(images.length);
}

function _populateModal(modal, item) {
  state.selectedItemForModal = item;
  state.selectedSizeForModal = null;
  const images = getItemImages(item);
  state.itemModalImageIndex = 0;
  modal.querySelector("#itemModalTitle").textContent = item.name;
  modal.querySelector("#itemModalPrice").textContent = getPriceDisplay(item);
  const tagEl = modal.querySelector("#itemModalTag");
  tagEl.textContent = item.category;
  const tagColor = getTagColor(item.category);
  tagEl.style.background = tagColor ? `${tagColor}20` : "";
  tagEl.style.borderColor = tagColor || "";
  tagEl.style.color = tagColor || "";
  const imageEl = document.getElementById("itemModalImage");
  if (imageEl) { imageEl.src = images[0] || ""; imageEl.alt = item.name; }
  updateItemModalImageNav(images.length);
  modal.querySelector("#itemModalDescription").textContent = item.description || "No additional description for this item.";
  renderSizeButtons(item);
  const askBtn = document.getElementById("itemModalAskOwner");
  if (askBtn) askBtn.textContent = state.catalogData?.contactLabel || "Ask owner";
  const imgPrev = document.getElementById("itemModalImgPrev");
  const imgNext = document.getElementById("itemModalImgNext");
  if (imgPrev) imgPrev.onclick = () => cycleItemModalImage(-1, images);
  if (imgNext) imgNext.onclick = () => cycleItemModalImage(1, images);
  return images;
}

export function openItemModal(catalogItemEl) {
  const modal = document.getElementById("itemModal");
  if (!modal) return;
  const item = state.allItems.find((i) => String(i.id) === String(catalogItemEl.dataset.itemId));
  if (!item) return;
  _populateModal(modal, item);
  modal.classList.add("item-modal--open");
  modal.setAttribute("aria-hidden", "false");
}

export function openItemModalByItem(item) {
  if (!item) return;
  const modal = document.getElementById("itemModal");
  if (!modal) return;
  _populateModal(modal, item);
  modal.classList.add("item-modal--open");
  modal.setAttribute("aria-hidden", "false");
}

export function initItemModal(saveAskOwnerRequests) {
  const modal = document.getElementById("itemModal");
  if (!modal) return;
  const backdrop = modal.querySelector(".item-modal__backdrop");
  const closeBtn = modal.querySelector(".item-modal__close");
  const addToCartBtn = document.getElementById("itemModalAddToCart");
  const askOwnerBtn = document.getElementById("itemModalAskOwner");

  function close() {
    modal.classList.remove("item-modal--open");
    modal.setAttribute("aria-hidden", "true");
    state.selectedItemForModal = null;
    state.selectedSizeForModal = null;
    if (state.openedItemModalFromCart) {
      state.openedItemModalFromCart = false;
      document.getElementById("cartModal")?.classList.add("cart-modal--open");
      document.getElementById("cartModal")?.setAttribute("aria-hidden", "false");
    }
  }
  closeBtn?.addEventListener("click", close);
  backdrop?.addEventListener("click", close);

  addToCartBtn?.addEventListener("click", () => {
    if (!state.selectedItemForModal) return;
    const size = state.selectedSizeForModal
      || (Array.isArray(state.selectedItemForModal.sizes) && state.selectedItemForModal.sizes[0])
      || "M";
    state.cart.push({ id: state.selectedItemForModal.id, name: state.selectedItemForModal.name, price: state.selectedItemForModal.price, size });
    updateCartCount();
    syncCartToGuest();
    addToCartBtn.textContent = "Added!";
    setTimeout(() => { addToCartBtn.textContent = "Add to cart"; }, 1500);
  });

  askOwnerBtn?.addEventListener("click", (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (state.selectedItemForModal) {
      state.askOwnerRequests.push({ itemId: state.selectedItemForModal.id, name: state.selectedItemForModal.name, image: getItemImage(state.selectedItemForModal), timestamp: new Date().toISOString() });
      if (typeof saveAskOwnerRequests === "function") saveAskOwnerRequests();
    }
    const tel = state.catalogData?.contactTel;
    const url = state.catalogData?.contactUrl;
    if (tel) { window.location.href = `tel:${tel.replace(/\s/g, "")}`; }
    else if (url) { window.open(url, "_blank"); }
    else { askOwnerBtn.textContent = "Request sent"; setTimeout(() => { askOwnerBtn.textContent = state.catalogData?.contactLabel || "Ask owner"; }, 2000); }
  });
}

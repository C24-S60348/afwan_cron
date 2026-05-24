/**
 * App entry: load catalog, init all modules, wire state.onCatalogChange.
 */
import { state } from "./state.js";
import {
  buildCatalogFromData,
  createDots,
  updateDots,
  loadCatalogFromStorage,
  renderOwnerCatalogList,
  getTagColor,
} from "./catalog.js";
import {
  initSlider,
  initTabs,
  initSliderAndBuildCatalog,
  updateSlidePosition,
  bindItemClicks,
  goToPage,
} from "./slider.js";
import {
  getGuestId,
  loadGuestCarts,
  updateCartCount,
  renderCartModal,
  initCartModal,
} from "./cart.js";
import {
  openItemModal,
  openItemModalByItem,
  initItemModal,
} from "./itemModal.js";
import { setOwnerView, initOwnerPanel, saveAskOwnerRequests } from "./owner.js";
import { initTemplates } from "./templates.js";
import { loadServerCatalog } from "./serverApi.js";

function initYear() {
  const yearSpan = document.getElementById("year");
  if (yearSpan) yearSpan.textContent = String(new Date().getFullYear());
}

function applyBrand() {
  const shortEl = document.getElementById("brandShort");
  const nameEl = document.getElementById("brandName");
  const footerName = document.getElementById("footerBrandName");
  const name = state.brand?.name || "Catalog Baju";
  const short = state.brand?.short || "CB";
  if (shortEl) shortEl.textContent = short;
  if (nameEl) nameEl.textContent = name;
  if (footerName) footerName.textContent = name;
  document.title = name + " – Catalog";
}

function applyTabColors() {
  const tabButtons = Array.from(document.querySelectorAll(".catalog-tab"));
  tabButtons.forEach((tab) => {
    const category = tab.dataset.category || "";
    if (category === "all") return;
    const color = getTagColor(category);
    if (color) {
      tab.style.background = `${color}20`;
      tab.style.borderColor = color;
      tab.style.color = color;
    }
    tab.classList.toggle("catalog-tab--colored", !!color);
  });
}

function initInfoModal() {
  const modal = document.getElementById("infoModal");
  const openBtn = document.getElementById("infoBtn");
  const closeBtn = modal?.querySelector(".info-modal__close");
  const backdrop = modal?.querySelector(".info-modal__backdrop");

  if (!modal || !openBtn) return;

  function open() {
    const seasonTitle = document.getElementById("infoModalSeasonTitle");
    const seasonText = document.getElementById("infoModalSeasonText");
    const aboutText = document.getElementById("infoModalAboutText");
    if (state.catalogData) {
      if (seasonTitle) seasonTitle.textContent = state.catalogData.collectionTitle || "New Season Collection";
      if (seasonText) seasonText.textContent = state.catalogData.collectionSubtitle || "Quick view of all baju in the shop.";
    }
    if (aboutText && state.appData?.aboutText) aboutText.textContent = state.appData.aboutText;
    modal.classList.add("info-modal--open");
    modal.setAttribute("aria-hidden", "false");
  }

  function close() {
    modal.classList.remove("info-modal--open");
    modal.setAttribute("aria-hidden", "true");
  }

  openBtn.addEventListener("click", open);
  closeBtn?.addEventListener("click", close);
  backdrop?.addEventListener("click", close);
}

function initCatalog() {
  if (!state.catalogData?.items?.length) return;
  state.allItems = state.catalogData.items;
  initSliderAndBuildCatalog(openItemModal);
  initSlider(openItemModal);
  initTabs(openItemModal);
  initItemModal(saveAskOwnerRequests);
  applyBrand();
  applyTabColors();
}

async function loadCatalog() {
  const track = document.getElementById("sliderTrack");
  try {
    const res = await fetch("appsettings.json");
    const data = await res.json();
    state.appData = data;
    state.brand = data.brand || null;
    state.catalogData = data.catalog || null;
    state.defaultCatalogItems = Array.isArray(data?.catalog?.items)
      ? JSON.parse(JSON.stringify(data.catalog.items))
      : [];
    state.resetPassword = String(
      data?.catalog?.resetPassword || data?.resetPassword || "catalogbaju-reset"
    );
    const serverItems = await loadServerCatalog();
    if (serverItems && serverItems.length > 0) {
      if (state.catalogData) state.catalogData.items = serverItems;
      else state.catalogData = { items: serverItems };
    } else {
      const stored = loadCatalogFromStorage();
      if (stored && stored.length > 0) {
        if (state.catalogData) state.catalogData.items = stored;
        else state.catalogData = { items: stored };
      }
    }
    const aboutEl = document.getElementById("infoModalAboutText");
    if (aboutEl && data.aboutText) aboutEl.textContent = data.aboutText;
    if (state.catalogData?.items?.length) {
      initCatalog();
    } else {
      if (track) track.innerHTML = "<p style='padding:2rem;color:var(--text-soft)'>No catalog data. Check appsettings.json.</p>";
    }
    updateCartCount();
    applyBrand();
  } catch (err) {
    console.error("Failed to load appsettings.json", err);
    if (track) {
      track.innerHTML = "<p style='padding:2rem;color:var(--text-soft)'>Failed to load catalog. Ensure appsettings.json exists.</p>";
    }
  }
}

document.addEventListener("DOMContentLoaded", () => {
  initYear();
  getGuestId();
  loadGuestCarts();
  initInfoModal();
  initCartModal(openItemModalByItem, renderCartModal);
  initOwnerPanel(setOwnerView);
  setOwnerView(false);

  state.onCatalogChange = () => {
    buildCatalogFromData(() => bindItemClicks(openItemModal));
    createDots(goToPage);
    updateDots();
    updateSlidePosition();
    renderOwnerCatalogList();
  };

  initTemplates();
  loadCatalog();
});

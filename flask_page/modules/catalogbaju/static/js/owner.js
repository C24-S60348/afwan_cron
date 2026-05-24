/**
 * Owner panel: guest carts grid, ask owner requests, catalog list, tabs, CSV import/export.
 */
import { state } from "./state.js";
import { STORAGE_KEY_ASK_OWNER, STORAGE_KEY_GUEST_CARTS } from "./config.js";
import { escapeHtml, escapeAttr, parseCsvLine } from "./utils.js";
import {
  getItemImage,
  getPriceDisplay,
  buildCatalogFromData,
  saveCatalogToStorage,
  loadCatalogFromStorage,
  renderOwnerCatalogList,
} from "./catalog.js";
import { loadGuestCarts, saveGuestCarts, openGuestCartModal, initGuestCartModal } from "./cart.js";
import {
  loadServerAskOwnerRequests,
  saveServerAskOwnerRequests,
  loadServerGuestCarts,
} from "./serverApi.js";

export function loadAskOwnerRequests() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY_ASK_OWNER);
    if (raw) {
      const data = JSON.parse(raw);
      state.askOwnerRequests = Array.isArray(data) ? data : [];
    }
  } catch (_) {
    state.askOwnerRequests = [];
  }
}

export function saveAskOwnerRequests() {
  try {
    localStorage.setItem(STORAGE_KEY_ASK_OWNER, JSON.stringify(state.askOwnerRequests));
  } catch (_) {}
  void saveServerAskOwnerRequests(state.askOwnerRequests);
}

async function refreshOwnerSignalsFromServer() {
  const [serverRequests, serverGuestCarts] = await Promise.all([
    loadServerAskOwnerRequests(),
    loadServerGuestCarts(),
  ]);
  let changed = false;
  if (Array.isArray(serverRequests)) {
    state.askOwnerRequests = serverRequests;
    changed = true;
  }
  if (serverGuestCarts && typeof serverGuestCarts === "object") {
    state.guestCarts = serverGuestCarts;
    changed = true;
  }
  if (changed && state.isOwnerView) {
    renderOwnerPanel();
    renderOwnerGuestsGrid();
  }
}

export function renderOwnerPanel() {
  const list = document.getElementById("ownerPanelList");
  const empty = document.getElementById("ownerPanelEmpty");
  if (!list || !empty) return;
  list.innerHTML = "";
  if (state.askOwnerRequests.length === 0) {
    empty.style.display = "block";
    return;
  }
  empty.style.display = "none";
  state.askOwnerRequests.forEach((req, index) => {
    const li = document.createElement("li");
    li.className = "owner-panel__item";
    li.innerHTML = `
      <div class="owner-panel__item-img-wrap">
        <img class="owner-panel__item-img" src="${escapeAttr(req.image)}" alt="" />
      </div>
      <div class="owner-panel__item-info">
        <strong class="owner-panel__item-title">${escapeHtml(req.name)}</strong>
        <span class="owner-panel__item-time">${escapeHtml(new Date(req.timestamp).toLocaleString())}</span>
        <div class="owner-panel__item-actions">
          <button type="button" class="owner-panel__item-edit" data-index="${index}">Edit</button>
          <button type="button" class="owner-panel__item-remove" data-index="${index}">Remove</button>
        </div>
      </div>
    `;
    const removeBtn = li.querySelector(".owner-panel__item-remove");
    const editBtn = li.querySelector(".owner-panel__item-edit");
    removeBtn?.addEventListener("click", () => {
      state.askOwnerRequests.splice(index, 1);
      saveAskOwnerRequests();
      renderOwnerPanel();
    });
    editBtn?.addEventListener("click", () => {
      const newName = prompt("Edit name", req.name);
      if (newName != null && newName.trim()) {
        req.name = newName.trim();
        saveAskOwnerRequests();
        renderOwnerPanel();
      }
      const newImage = prompt("Edit image URL or filename (leave blank to keep)", req.image);
      if (newImage != null && newImage.trim()) {
        req.image = newImage.trim();
        saveAskOwnerRequests();
        renderOwnerPanel();
      }
    });
    list.appendChild(li);
  });
}

export function setOwnerView(on) {
  state.isOwnerView = on;
  const catalog = document.getElementById("catalog");
  const panel = document.getElementById("ownerPanel");
  const toggle = document.getElementById("ownerToggle");
  if (catalog) catalog.style.display = on ? "none" : "";
  if (panel) {
    panel.style.display = on ? "block" : "none";
    panel.setAttribute("aria-hidden", on ? "false" : "true");
  }
  if (toggle) toggle.classList.toggle("owner-toggle--active", on);
  if (on) {
    loadGuestCarts();
    renderOwnerGuestsGrid();
    renderOwnerPanel();
    renderOwnerCatalogList();
    void refreshOwnerSignalsFromServer();
  }
}

export function renderOwnerGuestsGrid() {
  const grid = document.getElementById("ownerGuestsGrid");
  const empty = document.getElementById("ownerGuestsEmpty");
  if (!grid || !empty) return;
  grid.innerHTML = "";
  const entries = Object.entries(state.guestCarts).filter(([, data]) => data.cart && data.cart.length > 0);
  if (entries.length === 0) {
    empty.style.display = "block";
    return;
  }
  empty.style.display = "none";
  entries.forEach(([gid, data]) => {
    const circle = document.createElement("button");
    circle.type = "button";
    circle.className = "owner-guest-circle" + (data.submittedToOwner ? " owner-guest-circle--submitted" : "");
    circle.title = data.submittedToOwner ? "Submitted – view cart" : "View cart";
    circle.innerHTML = '<span class="owner-guest-circle__icon" aria-hidden="true">👤</span>';
    circle.addEventListener("click", () => openGuestCartModal(gid, data));
    grid.appendChild(circle);
  });
}

export function initOwnerPanel(setOwnerViewFn) {
  loadAskOwnerRequests();
  loadGuestCarts();
  void refreshOwnerSignalsFromServer();
  setInterval(() => {
    if (state.isOwnerView) void refreshOwnerSignalsFromServer();
  }, 3000);
  window.addEventListener("storage", (e) => {
    if (e.key === STORAGE_KEY_ASK_OWNER && e.newValue) {
      try {
        state.askOwnerRequests = JSON.parse(e.newValue);
        if (state.isOwnerView) renderOwnerPanel();
      } catch (_) {}
    }
    if (e.key === STORAGE_KEY_GUEST_CARTS && e.newValue) {
      try {
        state.guestCarts = JSON.parse(e.newValue);
        if (state.isOwnerView) renderOwnerGuestsGrid();
      } catch (_) {}
    }
  });

  const toggle = document.getElementById("ownerToggle");
  const back = document.getElementById("ownerPanelBack");
  const addBtn = document.getElementById("ownerPanelAdd");
  const exportBtn = document.getElementById("ownerPanelExport");
  const importInput = document.getElementById("ownerPanelImport");

  if (toggle) toggle.addEventListener("click", () => setOwnerViewFn(!state.isOwnerView));
  if (back) back.addEventListener("click", () => setOwnerViewFn(false));

  document.querySelectorAll(".owner-tab").forEach((tab) => {
    tab.addEventListener("click", () => {
      const panel = tab.dataset.panel || "";
      document.querySelectorAll(".owner-tab").forEach((t) => t.classList.remove("owner-tab--active"));
      document.querySelectorAll(".owner-panel__content").forEach((c) => c.classList.add("owner-panel__content--hidden"));
      tab.classList.add("owner-tab--active");
      const id = "ownerPanel" + (panel.charAt(0).toUpperCase() + panel.slice(1));
      const content = document.getElementById(id);
      if (content) content.classList.remove("owner-panel__content--hidden");
    });
  });

  addBtn?.addEventListener("click", () => {
    const name = prompt("Item name");
    if (name == null || !name.trim()) return;
    const image = prompt("Image URL or filename (e.g. https://... or mybaju.png)", "mybaju.png");
    state.askOwnerRequests.push({
      itemId: "",
      name: name.trim(),
      image: (image && image.trim()) || "mybaju.png",
      timestamp: new Date().toISOString(),
    });
    saveAskOwnerRequests();
    renderOwnerPanel();
  });

  exportBtn?.addEventListener("click", () => {
    const headers = ["name", "image", "timestamp"];
    const rows = state.askOwnerRequests.map((r) => [r.name, r.image, r.timestamp]);
    const csv = [headers.join(","), ...rows.map((r) => r.map((c) => `"${String(c).replace(/"/g, '""')}"`).join(","))].join("\n");
    const blob = new Blob(["﻿" + csv], { type: "text/csv;charset=utf-8" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "ask-owner-requests.csv";
    a.click();
    URL.revokeObjectURL(a.href);
  });

  importInput?.addEventListener("change", (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      const text = reader.result || "";
      const lines = text.split(/\r?\n/).filter((l) => l.trim());
      if (lines.length < 2) return;
      const parsed = [];
      for (let i = 1; i < lines.length; i++) {
        const values = parseCsvLine(lines[i]);
        if (values.length >= 2) {
          parsed.push({
            itemId: "",
            name: values[0] || "",
            image: values[1] || "mybaju.png",
            timestamp: values[2] ? values[2].replace(/^"|"$/g, "") : new Date().toISOString(),
          });
        }
      }
      state.askOwnerRequests = parsed;
      saveAskOwnerRequests();
      renderOwnerPanel();
    };
    reader.readAsText(file);
    e.target.value = "";
  });

  const catalogAddBtn = document.getElementById("catalogAddItem");
  const catalogImportCsv = document.getElementById("catalogImportCsv");
  const catalogExportCsv = document.getElementById("catalogExportCsv");
  const catalogResetDefaults = document.getElementById("catalogResetDefaults");

  catalogAddBtn?.addEventListener("click", () => {
    const id = state.allItems.length ? Math.max(...state.allItems.map((i) => Number(i.id) || 0)) + 1 : 1;
    const name = prompt("Item name");
    if (name == null || !name.trim()) return;
    const imagesInput = prompt(
      "Up to 3 image URLs/filenames (comma-separated)",
      "mybaju.png"
    );
    const images = (imagesInput || "mybaju.png")
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean)
      .slice(0, 3);
    const item = {
      id,
      name: name.trim(),
      price: prompt("Price", "RM 0") || "RM 0",
      category: prompt("Category (men/women/kids/unisex)", "unisex") || "unisex",
      description: prompt("Description", "") || "",
      image: images[0] || "mybaju.png",
      images,
      sizes: ["S", "M", "L", "XL", "XXL"],
    };
    state.allItems.push(item);
    if (state.catalogData) state.catalogData.items = state.allItems;
    saveCatalogToStorage();
    state.onCatalogChange?.();
  });

  catalogExportCsv?.addEventListener("click", () => {
    const headers = ["id", "name", "price", "category", "description", "image", "sizes"];
    const rows = state.allItems.map((i) => [
      i.id,
      i.name,
      i.price || "",
      i.category || "",
      i.description || "",
      i.image || "",
      Array.isArray(i.sizes) ? i.sizes.join(";") : "",
    ]);
    const csv = [headers.join(","), ...rows.map((r) => r.map((c) => `"${String(c).replace(/"/g, '""')}"`).join(","))].join("\n");
    const blob = new Blob(["﻿" + csv], { type: "text/csv;charset=utf-8" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "catalog-items.csv";
    a.click();
    URL.revokeObjectURL(a.href);
  });

  catalogImportCsv?.addEventListener("change", (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      const text = reader.result || "";
      const lines = text.split(/\r?\n/).filter((l) => l.trim());
      if (lines.length < 2) return;
      const parsed = [];
      for (let i = 1; i < lines.length; i++) {
        const values = parseCsvLine(lines[i]);
        if (values.length >= 2) {
          const id = parseInt(values[0], 10) || parsed.length + 1;
          parsed.push({
            id,
            name: values[1] || "",
            price: values[2] || "RM 0",
            category: values[3] || "unisex",
            description: values[4] || "",
            image: values[5] || "mybaju.png",
            sizes: values[6] ? values[6].split(";").map((s) => s.trim()).filter(Boolean) : ["S", "M", "L", "XL", "XXL"],
          });
        }
      }
      if (parsed.length) {
        state.allItems = parsed;
        if (state.catalogData) state.catalogData.items = state.allItems;
        saveCatalogToStorage();
        state.onCatalogChange?.();
      }
    };
    reader.readAsText(file);
    e.target.value = "";
  });

  catalogResetDefaults?.addEventListener("click", async () => {
    let defaults = Array.isArray(state.defaultCatalogItems)
      ? state.defaultCatalogItems
      : [];
    let resetPassword = state.resetPassword || "catalogbaju-reset";

    try {
      const res = await fetch("appsettings.json", { cache: "no-store" });
      if (res.ok) {
        const data = await res.json();
        const fromFile = data?.catalog?.items;
        if (Array.isArray(fromFile) && fromFile.length > 0) defaults = fromFile;
        resetPassword = String(
          data?.catalog?.resetPassword || data?.resetPassword || resetPassword
        );
      }
    } catch (_) {}

    if (!Array.isArray(defaults) || defaults.length === 0) {
      alert("No default catalog found in appsettings.json");
      return;
    }
    const pw = prompt("Enter reset password");
    if (pw == null) return;
    if (pw !== resetPassword) {
      alert("Wrong password.");
      return;
    }
    const ok = confirm("Reset all catalog items to default data? This replaces current catalog.");
    if (!ok) return;
    state.defaultCatalogItems = JSON.parse(JSON.stringify(defaults));
    state.resetPassword = resetPassword;
    state.allItems = JSON.parse(JSON.stringify(defaults));
    if (state.catalogData) state.catalogData.items = state.allItems;
    saveCatalogToStorage();
    state.onCatalogChange?.();
    alert("Catalog reset to default.");
  });

  initGuestCartModal();
}

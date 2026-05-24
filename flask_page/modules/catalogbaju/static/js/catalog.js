/**
 * Catalog data, filtering, building grid, storage, owner catalog list.
 */
import { state } from "./state.js";
import { ITEMS_PER_PAGE, STORAGE_KEY_CATALOG_ITEMS } from "./config.js";
import { escapeHtml, escapeAttr } from "./utils.js";
import { saveServerCatalog } from "./serverApi.js";

export function getPriceDisplay(item) {
  const min = item.priceMin || item.price;
  const max = item.priceMax || item.price;
  if (min === max || !item.priceMax) return min;
  return `${min} – ${max}`;
}

export function getItemImages(item) {
  const list = Array.isArray(item?.images)
    ? item.images.map((src) => String(src || "").trim()).filter(Boolean)
    : [];
  const single = String(item?.image || "").trim();
  if (single) {
    if (!list.includes(single)) list.unshift(single);
    else {
      const idx = list.indexOf(single);
      if (idx > 0) {
        list.splice(idx, 1);
        list.unshift(single);
      }
    }
  }
  if (list.length > 0) return list;
  return [state.catalogData?.defaultImage || "mybaju.png"];
}

export function getItemImage(item) {
  const imgs = getItemImages(item);
  return imgs[0] || state.catalogData?.defaultImage || "mybaju.png";
}

export function getTagColor(category) {
  if (!state.appData?.tags || !category) return "";
  const key = category.toLowerCase();
  return state.appData.tags[key] || "";
}

export function getFilteredItems() {
  if (state.activeCategory === "all") return state.allItems.slice();
  return state.allItems.filter(
    (item) => item.category.toLowerCase() === state.activeCategory.toLowerCase()
  );
}

export function chunkPages(items) {
  const pages = [];
  for (let i = 0; i < items.length; i += ITEMS_PER_PAGE) {
    pages.push(items.slice(i, i + ITEMS_PER_PAGE));
  }
  return pages;
}

function createEmptyCell() {
  const el = document.createElement("div");
  el.className = "grid-cell grid-cell--empty";
  return el;
}

export function createCatalogItemElement(item) {
  const el = document.createElement("article");
  el.className = "catalog-item";
  el.dataset.itemId = item.id;
  el.dataset.description = item.description || "";
  el.dataset.price = item.price || "";
  el.dataset.tag = item.category || "";
  el.dataset.name = item.name || "";
  const imgSrc = getItemImage(item);
  const priceDisplay = getPriceDisplay(item);
  const tagColor = getTagColor(item.category);
  const tagStyle = tagColor ? ` style="background:${escapeAttr(tagColor)}20; border-color:${escapeAttr(tagColor)}; color:${escapeAttr(tagColor)};"` : "";
  el.innerHTML = `
    <div class="catalog-item__image">
      <img class="catalog-item__img" src="${escapeAttr(imgSrc)}" alt="" loading="lazy" />
    </div>
    <div class="catalog-item__content">
      <div class="catalog-item__meta">
        <span class="price">${escapeHtml(priceDisplay)}</span>
        <span class="tag tag--custom"${tagStyle}>${escapeHtml(item.category)}</span>
      </div>
      <h2 class="catalog-item__title">${escapeHtml(item.name)}</h2>
    </div>
  `;
  return el;
}

export function loadCatalogFromStorage() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY_CATALOG_ITEMS);
    if (raw) {
      const items = JSON.parse(raw);
      if (Array.isArray(items) && items.length > 0) return items;
    }
  } catch (_) {}
  return null;
}

export function saveCatalogToStorage() {
  try {
    localStorage.setItem(STORAGE_KEY_CATALOG_ITEMS, JSON.stringify(state.allItems));
  } catch (_) {}
  void saveServerCatalog(state.allItems);
}

export function buildCatalogFromData(bindItemClicks) {
  const items = getFilteredItems();
  const pages = chunkPages(items);
  const track = document.getElementById("sliderTrack");
  const dotsContainer = document.querySelector(".slider-dots");
  if (!track) return;

  track.innerHTML = "";

  for (const pageItems of pages) {
    const slidePage = document.createElement("div");
    slidePage.className = "slide-page";
    for (let i = 0; i < ITEMS_PER_PAGE; i += 1) {
      const cell = document.createElement("div");
      cell.className = "grid-cell";
      if (i < pageItems.length) {
        cell.appendChild(createCatalogItemElement(pageItems[i]));
      } else {
        cell.classList.add("grid-cell--empty");
      }
      slidePage.appendChild(cell);
    }
    track.appendChild(slidePage);
  }

  state.totalPages = Math.max(1, pages.length);
  state.currentPage = 0;
  if (typeof bindItemClicks === "function") bindItemClicks();
}

export function createDots(goToPage) {
  const dotsContainer = document.querySelector(".slider-dots");
  if (!dotsContainer) return;
  dotsContainer.innerHTML = "";
  for (let i = 0; i < state.totalPages; i += 1) {
    const dot = document.createElement("button");
    dot.className = "slider-dot";
    dot.type = "button";
    dot.setAttribute("aria-label", `Go to page ${i + 1}`);
    dot.addEventListener("click", () => goToPage(i));
    dotsContainer.appendChild(dot);
  }
}

export function updateDots() {
  const dotsContainer = document.querySelector(".slider-dots");
  if (!dotsContainer) return;
  const dots = dotsContainer.querySelectorAll(".slider-dot");
  dots.forEach((dot, index) => {
    dot.classList.toggle("slider-dot--active", index === state.currentPage);
  });
}

export function renderOwnerCatalogList() {
  const list = document.getElementById("ownerCatalogList");
  if (!list) return;
  list.innerHTML = "";
  state.allItems.forEach((item, index) => {
    const li = document.createElement("li");
    const imgSrc = getItemImage(item);
    const sizes = (item.sizes && item.sizes.length) ? item.sizes.join(", ") : "S, M, L, XL, XXL";
    li.innerHTML = `
      <img src="${escapeAttr(imgSrc)}" alt="" />
      <div style="flex:1;min-width:0;">
        <strong>${escapeHtml(item.name)}</strong>
        <span style="display:block;font-size:0.8rem;color:var(--text-soft)">${escapeHtml(getPriceDisplay(item))} · ${escapeHtml(item.category)} · ${escapeHtml(sizes)}</span>
        <div class="owner-panel__item-actions" style="margin-top:0.25rem">
          <button type="button" class="owner-panel__item-edit" data-index="${index}">Edit</button>
          <button type="button" class="owner-panel__item-remove" data-index="${index}">Remove</button>
        </div>
      </div>
    `;
    const removeBtn = li.querySelector(".owner-panel__item-remove");
    const editBtn = li.querySelector(".owner-panel__item-edit");
    removeBtn?.addEventListener("click", () => {
      state.allItems.splice(index, 1);
      if (state.catalogData) state.catalogData.items = state.allItems;
      saveCatalogToStorage();
      state.onCatalogChange?.();
    });
    editBtn?.addEventListener("click", () => {
      const name = prompt("Name", item.name);
      if (name != null && name.trim()) item.name = name.trim();
      const price = prompt("Price", item.price);
      if (price != null) item.price = price.trim();
      const category = prompt("Category (men/women/kids/unisex)", item.category);
      if (category != null && category.trim()) item.category = category.trim();
      const desc = prompt("Description", item.description || "");
      if (desc != null) item.description = desc.trim();
      const currentImages = getItemImages(item).slice(0, 3);
      const imagesInput = prompt(
        "Up to 3 image URLs/filenames (comma-separated)",
        currentImages.join(", ")
      );
      if (imagesInput != null) {
        const nextImages = imagesInput
          .split(",")
          .map((s) => s.trim())
          .filter(Boolean)
          .slice(0, 3);
        if (nextImages.length > 0) {
          item.images = nextImages;
          item.image = nextImages[0];
        }
      }
      const sizesStr = prompt("Sizes (comma-separated)", (item.sizes || []).join(", "));
      if (sizesStr != null) item.sizes = sizesStr.split(",").map((s) => s.trim()).filter(Boolean);
      if (state.catalogData) state.catalogData.items = state.allItems;
      saveCatalogToStorage();
      state.onCatalogChange?.();
    });
    list.appendChild(li);
  });
}

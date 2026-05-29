/**
 * Slider: pages, dots, arrows, swipe, category filter.
 */
import { state } from "./state.js";
import {
  getTagColor,
  buildCatalogFromData,
  createDots,
  updateDots,
} from "./catalog.js";
import { ITEMS_PER_PAGE } from "./config.js";

let startX = 0;
let isDragging = false;

function getTrack() {
  return document.getElementById("sliderTrack");
}

export function updateSlidePosition() {
  const track = getTrack();
  if (!track) return;
  const offset = -state.currentPage * 100;
  track.style.transform = `translateX(${offset}%)`;
}

export function goToPage(index) {
  state.currentPage = Math.max(0, Math.min(index, state.totalPages - 1));
  updateSlidePosition();
  updateDots();
}

export function nextSlide() {
  const next = state.currentPage === state.totalPages - 1 ? 0 : state.currentPage + 1;
  goToPage(next);
}

export function prevSlide() {
  const prev = state.currentPage === 0 ? state.totalPages - 1 : state.currentPage - 1;
  goToPage(prev);
}

export function applyCategoryFilter(category, openItemModal) {
  state.activeCategory = category;
  const tabButtons = Array.from(document.querySelectorAll(".catalog-tab"));
  tabButtons.forEach((tab) => {
    const tabCat = tab.dataset.category || "all";
    const isActive = tabCat === category;
    tab.classList.toggle("catalog-tab--active", isActive);
    const color = getTagColor(tabCat);
    if (color && isActive) {
      tab.style.background = color;
      tab.style.borderColor = color;
      tab.style.color = "#fff";
    } else if (color) {
      tab.style.background = `${color}20`;
      tab.style.borderColor = color;
      tab.style.color = color;
    }
  });
  buildCatalogFromData(() => bindItemClicks(openItemModal));
  createDots(goToPage);
  updateDots();
  updateSlidePosition();
}

export function bindItemClicks(openItemModal) {
  const track = getTrack();
  if (!track || typeof openItemModal !== "function") return;
  track.querySelectorAll(".catalog-item").forEach((el) => {
    el.addEventListener("click", () => openItemModal(el));
  });
}

function onPointerDown(e) {
  isDragging = true;
  startX = e.clientX ?? e.touches?.[0]?.clientX ?? 0;
}

function onPointerMove(e) {
  if (!isDragging) return;
  const currentX = e.clientX ?? e.touches?.[0]?.clientX ?? 0;
  const deltaX = currentX - startX;
  if (Math.abs(deltaX) > 50) {
    isDragging = false;
    if (deltaX < 0) nextSlide();
    else prevSlide();
  }
}

function onPointerUp() {
  isDragging = false;
}

function attachSwipeHandlers() {
  const windowEl = document.querySelector(".slider-window");
  if (!windowEl) return;
  windowEl.addEventListener("mousedown", onPointerDown);
  windowEl.addEventListener("mousemove", onPointerMove);
  windowEl.addEventListener("mouseup", onPointerUp);
  windowEl.addEventListener("mouseleave", onPointerUp);
  windowEl.addEventListener("touchstart", onPointerDown, { passive: true });
  windowEl.addEventListener("touchmove", onPointerMove, { passive: true });
  windowEl.addEventListener("touchend", onPointerUp);
}

export function initSlider(openItemModal) {
  const prevButton = document.querySelector(".slider-arrow--prev");
  const nextButton = document.querySelector(".slider-arrow--next");
  prevButton?.addEventListener("click", prevSlide);
  nextButton?.addEventListener("click", nextSlide);
  attachSwipeHandlers();
}

export function initTabs(openItemModal) {
  const tabButtons = Array.from(document.querySelectorAll(".catalog-tab"));
  tabButtons.forEach((tab) => {
    tab.addEventListener("click", () => {
      const category = tab.dataset.category || "all";
      applyCategoryFilter(category, openItemModal);
    });
  });
}

export function initSliderAndBuildCatalog(openItemModal) {
  buildCatalogFromData(() => bindItemClicks(openItemModal));
  createDots(goToPage);
  updateDots();
  updateSlidePosition();
}

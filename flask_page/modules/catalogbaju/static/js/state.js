/**
 * Shared application state.
 */
export const state = {
  appData: null,
  catalogData: null,
  defaultCatalogItems: [],
  resetPassword: "",
  brand: null,
  currentPage: 0,
  totalPages: 1,
  activeCategory: "all",
  allItems: [],
  cart: [],
  selectedItemForModal: null,
  selectedSizeForModal: null,
  askOwnerRequests: [],
  isOwnerView: false,
  itemModalImageIndex: 0,
  openedItemModalFromCart: false,
  guestId: null,
  guestCarts: {},
  currentTemplateType: null,
  currentTemplateData: null,
  templateSelectedItems: [],
  /** Set by main.js: () => { buildCatalogFromData(); updateSlidePosition(); updateDots(); renderOwnerCatalogList(); } */
  onCatalogChange: null,
};

/**
 * Catalog templates: picker, preview, export PNG/PDF.
 */
import { state } from "./state.js";
import { escapeHtml, escapeAttr } from "./utils.js";
import { getItemImage } from "./catalog.js";

export function initTemplates() {
  const wrap = document.getElementById("templatePreviewWrap");
  const pickerWrap = document.getElementById("templatePickerWrap");
  const pickerGrid = document.getElementById("templatePickerGrid");
  const pickerLabel = document.getElementById("templatePickerLabel");
  const templateSelectedEl = document.getElementById("templateSelected");
  const buildPreviewBtn = document.getElementById("templateBuildPreview");
  const preview = document.getElementById("templatePreview");
  const bookBtn = document.getElementById("templateBookPage");
  const coverBtn = document.getElementById("templateCover");
  const pngBtn = document.getElementById("templateExportPng");
  const pdfBtn = document.getElementById("templateExportPdf");

  function renderPickerGrid() {
    if (!pickerGrid) return;
    pickerGrid.innerHTML = "";
    const maxSel = 3;
    state.allItems.forEach((item) => {
      const card = document.createElement("div");
      card.className = "template-picker-item";
      const isSel = state.templateSelectedItems.some((s) => s.id === item.id);
      if (isSel) card.classList.add("template-picker--selected");
      const imgSrc = getItemImage(item);
      card.innerHTML = `<img src="${escapeAttr(imgSrc)}" alt="" /><span>${escapeHtml(item.name)}</span>`;
      card.addEventListener("click", () => {
        const idx = state.templateSelectedItems.findIndex((s) => s.id === item.id);
        if (idx >= 0) state.templateSelectedItems.splice(idx, 1);
        else if (state.templateSelectedItems.length < maxSel) state.templateSelectedItems.push(item);
        card.classList.toggle("template-picker--selected", state.templateSelectedItems.some((s) => s.id === item.id));
        renderSelectedSummary();
      });
      pickerGrid.appendChild(card);
    });
  }

  function renderSelectedSummary() {
    if (!templateSelectedEl) return;
    templateSelectedEl.innerHTML = state.templateSelectedItems.length
      ? state.templateSelectedItems.map((it) => {
          const sizes = (it.sizes && it.sizes.length) ? it.sizes.join(", ") : "S, M, L, XL, XXL";
          return `<strong>${escapeHtml(it.name)}</strong> — Sizes: ${escapeHtml(sizes)}`;
        }).join("<br>")
      : "No items selected.";
  }

  function renderTemplatePreview() {
    if (!preview) return;
    if (state.currentTemplateType === "book" && state.currentTemplateData) {
      preview.innerHTML = state.currentTemplateData.map((d) => `
        <div class="template-slot">
          <img src="${escapeAttr(d.image)}" alt="" />
          <strong>${escapeHtml(d.name)}</strong>
          ${d.sizes ? `<span class="template-slot-sizes">${escapeHtml(d.sizes)}</span>` : ""}
          <p>${escapeHtml(d.description || "")}</p>
        </div>
      `).join("");
      preview.className = "template-preview template-preview--book";
    } else if (state.currentTemplateType === "cover" && state.currentTemplateData) {
      const imgs = state.currentTemplateData.images.map((src) => `<img src="${escapeAttr(src)}" alt="" />`).join("");
      preview.innerHTML = `
        <h2 class="template-cover-title">${escapeHtml(state.currentTemplateData.title)}</h2>
        <div class="template-cover-images">${imgs}</div>
        <p class="template-cover-bottom">${escapeHtml(state.currentTemplateData.bottomText)}</p>
      `;
      preview.className = "template-preview template-preview--cover";
    }
  }

  function exportTemplatePng() {
    if (!preview || !state.currentTemplateData) return;
    const w = 800;
    const h = state.currentTemplateType === "book" ? 600 : 500;
    const canvas = document.createElement("canvas");
    canvas.width = w;
    canvas.height = h;
    const ctx = canvas.getContext("2d");
    ctx.fillStyle = "#0f172a";
    ctx.fillRect(0, 0, w, h);
    const imagesToLoad = state.currentTemplateType === "book"
      ? state.currentTemplateData.flatMap((d) => [d.image])
      : state.currentTemplateData.images;
    let loaded = 0;
    const imgEls = [];
    function tryDraw() {
      loaded++;
      if (loaded < imagesToLoad.length) return;
      if (state.currentTemplateType === "book") {
        const slotW = w / 3;
        state.currentTemplateData.forEach((d, i) => {
          const x = i * slotW + 20;
          const img = imgEls[i];
          if (img && img.complete) {
            const scale = Math.min((slotW - 40) / img.width, 180 / img.height);
            ctx.drawImage(img, x, 20, img.width * scale, img.height * scale);
          }
          ctx.fillStyle = "#e5e7eb";
          ctx.font = "16px sans-serif";
          ctx.fillText(d.name.substring(0, 25), x, 220);
          if (d.sizes) {
            ctx.fillStyle = "#94a3b8";
            ctx.font = "11px sans-serif";
            ctx.fillText(("Sizes: " + d.sizes).substring(0, 35), x, 238);
          }
          ctx.fillStyle = "#9ca3af";
          ctx.font = "12px sans-serif";
          ctx.fillText((d.description || "").substring(0, 40), x, d.sizes ? 256 : 240);
        });
      } else {
        ctx.fillStyle = "#e5f6ff";
        ctx.font = "bold 28px sans-serif";
        ctx.textAlign = "center";
        ctx.fillText(state.currentTemplateData.title, w / 2, 50);
        const imgs = state.currentTemplateData.images || [];
        const n = Math.min(imgs.length, 3);
        const imgW = n > 0 ? (w - 40) / n - 10 : 0;
        const maxH = 280;
        for (let i = 0; i < n; i++) {
          const img = imgEls[i];
          if (img && img.complete && img.naturalWidth) {
            const scale = Math.min(imgW / img.width, maxH / img.height);
            const dw = img.width * scale;
            const dh = img.height * scale;
            const x = 20 + i * (imgW + 10) + (imgW - dw) / 2;
            ctx.drawImage(img, x, 80, dw, dh);
          }
        }
        ctx.fillStyle = "#9ca3af";
        ctx.font = "14px sans-serif";
        ctx.fillText(state.currentTemplateData.bottomText, w / 2, h - 30);
      }
      const a = document.createElement("a");
      a.href = canvas.toDataURL("image/png");
      a.download = `catalog-${state.currentTemplateType}-${Date.now()}.png`;
      a.click();
    }
    imagesToLoad.forEach((src, i) => {
      const img = new Image();
      img.crossOrigin = "anonymous";
      img.onload = tryDraw;
      img.onerror = tryDraw;
      img.src = src;
      imgEls[i] = img;
    });
    if (imagesToLoad.length === 0) tryDraw();
  }

  function exportTemplatePdf() {
    if (!preview || !state.currentTemplateData) return;
    const w = 800;
    const h = state.currentTemplateType === "book" ? 600 : 500;
    const canvas = document.createElement("canvas");
    canvas.width = w;
    canvas.height = h;
    const ctx = canvas.getContext("2d");
    ctx.fillStyle = "#0f172a";
    ctx.fillRect(0, 0, w, h);
    const imagesToLoad = state.currentTemplateType === "book"
      ? state.currentTemplateData.flatMap((d) => [d.image])
      : state.currentTemplateData.images;
    const imgEls = [];
    let loaded = 0;
    function tryDraw() {
      loaded++;
      if (loaded < imagesToLoad.length) return;
      if (state.currentTemplateType === "book") {
        const slotW = w / 3;
        state.currentTemplateData.forEach((d, i) => {
          const x = i * slotW + 20;
          const img = imgEls[i];
          if (img && img.complete && img.naturalWidth) {
            const scale = Math.min((slotW - 40) / img.width, 180 / img.height);
            ctx.drawImage(img, x, 20, img.width * scale, img.height * scale);
          }
          ctx.fillStyle = "#e5e7eb";
          ctx.font = "16px sans-serif";
          ctx.fillText(d.name.substring(0, 25), x, 220);
          if (d.sizes) {
            ctx.fillStyle = "#94a3b8";
            ctx.font = "11px sans-serif";
            ctx.fillText(("Sizes: " + d.sizes).substring(0, 35), x, 238);
          }
          ctx.fillStyle = "#9ca3af";
          ctx.font = "12px sans-serif";
          ctx.fillText((d.description || "").substring(0, 40), x, d.sizes ? 256 : 240);
        });
      } else {
        ctx.fillStyle = "#e5f6ff";
        ctx.font = "bold 28px sans-serif";
        ctx.textAlign = "center";
        ctx.fillText(state.currentTemplateData.title, w / 2, 50);
        const imgs = state.currentTemplateData.images || [];
        const n = Math.min(imgs.length, 3);
        const imgW = n > 0 ? (w - 40) / n - 10 : 0;
        const maxH = 280;
        for (let i = 0; i < n; i++) {
          const img = imgEls[i];
          if (img && img.complete && img.naturalWidth) {
            const scale = Math.min(imgW / img.width, maxH / img.height);
            const dw = img.width * scale;
            const dh = img.height * scale;
            const x = 20 + i * (imgW + 10) + (imgW - dw) / 2;
            ctx.drawImage(img, x, 80, dw, dh);
          }
        }
        ctx.fillStyle = "#9ca3af";
        ctx.font = "14px sans-serif";
        ctx.fillText(state.currentTemplateData.bottomText, w / 2, h - 30);
      }
      try {
        const { jsPDF } = window.jspdf || {};
        if (jsPDF) {
          const pdf = new jsPDF({ orientation: w > h ? "landscape" : "portrait", unit: "px", format: [w, h] });
          pdf.addImage(canvas.toDataURL("image/png"), "PNG", 0, 0, w, h);
          pdf.save(`catalog-${state.currentTemplateType}-${Date.now()}.pdf`);
        } else {
          const win = window.open("", "_blank");
          win.document.write(`<img src="${canvas.toDataURL("image/png")}" style="max-width:100%;height:auto;" />`);
          win.document.close();
          win.print();
        }
      } catch (err) {
        const win = window.open("", "_blank");
        win.document.write(`<img src="${canvas.toDataURL("image/png")}" style="max-width:100%;height:auto;" />`);
        win.document.close();
        win.print();
      }
    }
    imagesToLoad.forEach((src, i) => {
      const img = new Image();
      img.crossOrigin = "anonymous";
      img.onload = tryDraw;
      img.onerror = tryDraw;
      img.src = src;
      imgEls[i] = img;
    });
    if (imagesToLoad.length === 0) tryDraw();
  }

  bookBtn?.addEventListener("click", () => {
    state.currentTemplateType = "book";
    state.templateSelectedItems = [];
    if (pickerLabel) pickerLabel.textContent = "Select up to 3 items (click to add):";
    if (pickerWrap) pickerWrap.style.display = "block";
    if (wrap) wrap.style.display = "none";
    renderPickerGrid();
    renderSelectedSummary();
  });

  coverBtn?.addEventListener("click", () => {
    state.currentTemplateType = "cover";
    state.templateSelectedItems = [];
    if (pickerLabel) pickerLabel.textContent = "Select 1–3 items for cover (click to add):";
    if (pickerWrap) pickerWrap.style.display = "block";
    if (wrap) wrap.style.display = "none";
    renderPickerGrid();
    renderSelectedSummary();
  });

  buildPreviewBtn?.addEventListener("click", () => {
    if (state.currentTemplateType === "book") {
      const items = state.templateSelectedItems.slice(0, 3);
      if (items.length === 0) return;
      state.currentTemplateData = items.map((it) => ({
        name: it.name,
        description: it.description || "",
        image: getItemImage(it),
        sizes: (it.sizes && it.sizes.length) ? it.sizes.join(", ") : "S, M, L, XL, XXL",
      }));
    } else if (state.currentTemplateType === "cover") {
      const items = state.templateSelectedItems.slice(0, 3);
      state.currentTemplateData = {
        title: state.brand?.name || "Catalog Baju",
        bottomText: state.catalogData?.contactTel ? `For ask, please call ${state.catalogData.contactTel}` : (state.catalogData?.contactLabel || "Ask owner"),
        images: items.length ? items.map((it) => getItemImage(it)) : ["mybaju.png"],
      };
    }
    if (pickerWrap) pickerWrap.style.display = "none";
    if (wrap) wrap.style.display = "block";
    renderTemplatePreview();
  });

  pngBtn?.addEventListener("click", () => exportTemplatePng());
  pdfBtn?.addEventListener("click", () => exportTemplatePdf());
}

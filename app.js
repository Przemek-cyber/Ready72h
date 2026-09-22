(function () {
  "use strict";

  var UI = {
    pl: {
      tagline: "Twój dom gotowy na pierwsze 72 godziny kryzysu.",
      apartment: "Mieszkanie", house: "Dom z ogrodem",
      progress: "wykonane", reset: "Wyczyść wszystkie zaznaczenia",
      tabChecklist: "Zapasy", tabFamily: "Plan", tabBag: "Plecak", tabVariant: "Wariant", tabSources: "Info",
      offline: "⚡ Tryb offline — treść działa bez internetu",
      confirmReset: "Wyczyścić wszystkie zaznaczone pozycje?"
    },
    en: {
      tagline: "Get your household ready for the first 72 hours of any crisis.",
      apartment: "Apartment", house: "House with garden",
      progress: "done", reset: "Clear all checkmarks",
      tabChecklist: "Supplies", tabFamily: "Plan", tabBag: "Go-bag", tabVariant: "Variant", tabSources: "Info",
      offline: "⚡ Offline mode — content works without internet",
      confirmReset: "Clear all checked items?"
    },
    de: {
      tagline: "Mach deinen Haushalt bereit für die ersten 72 Stunden jeder Krise.",
      apartment: "Wohnung", house: "Haus mit Garten",
      progress: "erledigt", reset: "Alle Häkchen zurücksetzen",
      tabChecklist: "Vorrat", tabFamily: "Plan", tabBag: "Rucksack", tabVariant: "Variante", tabSources: "Info",
      offline: "⚡ Offline-Modus — Inhalte funktionieren ohne Internet",
      confirmReset: "Alle markierten Punkte zurücksetzen?"
    },
    es: {
      tagline: "Prepara tu hogar para las primeras 72 horas de cualquier crisis.",
      apartment: "Piso", house: "Casa con jardín",
      progress: "hecho", reset: "Borrar todas las marcas",
      tabChecklist: "Suministros", tabFamily: "Plan", tabBag: "Mochila", tabVariant: "Versión", tabSources: "Info",
      offline: "⚡ Modo sin conexión — el contenido funciona sin internet",
      confirmReset: "¿Borrar todos los elementos marcados?"
    }
  };

  var state = {
    lang: localStorage.getItem("g72_lang") || "pl",
    variant: localStorage.getItem("g72_variant") || "apartment",
    view: "checklist",
    data: null,
    checks: JSON.parse(localStorage.getItem("g72_checks") || "{}")
  };

  var cache = {};

  function el(id) { return document.getElementById(id); }

  function saveChecks() {
    localStorage.setItem("g72_checks", JSON.stringify(state.checks));
  }

  function loadData(lang, cb) {
    if (cache[lang]) { cb(cache[lang]); return; }
    fetch("data/content." + lang + ".json")
      .then(function (r) { return r.json(); })
      .then(function (d) { cache[lang] = d; cb(d); })
      .catch(function (err) {
        console.error("Failed to load content", err);
      });
  }

  function checklistItem(idKey, text) {
    var li = document.createElement("li");
    var checked = !!state.checks[idKey];
    if (checked) li.className = "done";
    var cb = document.createElement("input");
    cb.type = "checkbox";
    cb.id = "chk-" + idKey;
    cb.checked = checked;
    cb.addEventListener("change", function () {
      state.checks[idKey] = cb.checked;
      li.className = cb.checked ? "done" : "";
      saveChecks();
      updateProgress();
    });
    var label = document.createElement("label");
    label.setAttribute("for", cb.id);
    label.textContent = text;
    li.appendChild(cb);
    li.appendChild(label);
    return li;
  }

  function renderSupplies(data) {
    var wrap = el("suppliesCards");
    wrap.innerHTML = "";
    data.supplies.categories.forEach(function (cat, ci) {
      var card = document.createElement("div");
      card.className = "cat-card" + (ci % 2 ? " alt" : "");
      var h3 = document.createElement("h3");
      h3.textContent = cat.title;
      var note = document.createElement("div");
      note.className = "note";
      note.textContent = cat.note;
      var ul = document.createElement("ul");
      ul.className = "check-list";
      cat.items.forEach(function (item, ii) {
        ul.appendChild(checklistItem("s-" + ci + "-" + ii, item));
      });
      card.appendChild(h3);
      card.appendChild(note);
      card.appendChild(ul);
      wrap.appendChild(card);
    });
  }

  function renderFamily(data) {
    var wrap = el("familyCards");
    wrap.innerHTML = "";
    data.family_plan.sections.forEach(function (s, si) {
      var card = document.createElement("div");
      card.className = "plan-card";
      var h3 = document.createElement("h3");
      h3.textContent = s.title;
      var ul = document.createElement("ul");
      s.points.forEach(function (pt) {
        var li = document.createElement("li");
        li.textContent = pt;
        ul.appendChild(li);
      });
      card.appendChild(h3);
      card.appendChild(ul);
      wrap.appendChild(card);
    });
  }

  function renderBag(data) {
    var wrap = el("bagCards");
    wrap.innerHTML = "";
    data.grab_bag.categories.forEach(function (cat, ci) {
      var card = document.createElement("div");
      card.className = "cat-card";
      var h3 = document.createElement("h3");
      h3.textContent = cat.title;
      var ul = document.createElement("ul");
      ul.className = "check-list";
      cat.items.forEach(function (item, ii) {
        ul.appendChild(checklistItem("b-" + ci + "-" + ii, item));
      });
      card.appendChild(h3);
      card.appendChild(ul);
      wrap.appendChild(card);
    });
  }

  function renderVariant(data) {
    var vd = state.variant === "apartment" ? data.variant_apartment : data.variant_house;
    el("variantHeading").textContent = vd.heading;
    el("variantIntro").textContent = vd.intro;
    var wrap = el("variantCards");
    wrap.innerHTML = "";
    vd.adaptations.forEach(function (a, i) {
      var card = document.createElement("div");
      card.className = "adapt-card";
      var h3 = document.createElement("h3");
      var num = document.createElement("span");
      num.className = "num";
      num.textContent = i + 1;
      h3.appendChild(num);
      h3.appendChild(document.createTextNode(a.title));
      var p = document.createElement("p");
      p.textContent = a.text;
      card.appendChild(h3);
      card.appendChild(p);
      wrap.appendChild(card);
    });
  }

  function renderSources(data) {
    el("sourcesHeading").textContent = data.sources.heading;
    var ul = el("sourcesList");
    ul.innerHTML = "";
    data.sources.items.forEach(function (s) {
      var li = document.createElement("li");
      li.textContent = s;
      ul.appendChild(li);
    });
    el("sourcesDisclaimer").textContent = data.sources.disclaimer;
  }

  function updateProgress() {
    var total = 0, done = 0;
    Object.keys(state.checks).forEach(function () {});
    // count based on currently rendered checkboxes in DOM across all views for accuracy
    var boxes = document.querySelectorAll('input[type=checkbox][id^="chk-"]');
    // total should reflect full dataset, not just currently visible tab; recompute from data
    if (state.data) {
      state.data.supplies.categories.forEach(function (c, ci) {
        c.items.forEach(function (it, ii) {
          total++; if (state.checks["s-" + ci + "-" + ii]) done++;
        });
      });
      state.data.grab_bag.categories.forEach(function (c, ci) {
        c.items.forEach(function (it, ii) {
          total++; if (state.checks["b-" + ci + "-" + ii]) done++;
        });
      });
    }
    var pct = total ? Math.round((done / total) * 100) : 0;
    el("progressPct").textContent = pct + "%";
    el("progressLabel").textContent = UI[state.lang].progress + " (" + done + "/" + total + ")";
    var circle = el("progressCircle");
    var circumference = 113;
    circle.setAttribute("stroke-dashoffset", circumference - (circumference * pct / 100));
  }

  function applyUIStrings() {
    var t = UI[state.lang];
    el("tagline").textContent = t.tagline;
    el("btnApartment").textContent = t.apartment;
    el("btnHouse").textContent = t.house;
    el("resetLabel").textContent = t.reset;
    el("tabChecklist").textContent = t.tabChecklist;
    el("tabFamily").textContent = t.tabFamily;
    el("tabBag").textContent = t.tabBag;
    el("tabVariant").textContent = t.tabVariant;
    el("tabSources").textContent = t.tabSources;
    el("offlineBanner").textContent = t.offline;
    document.documentElement.lang = state.lang;
  }

  function applyVariantButtons() {
    el("btnApartment").className = state.variant === "apartment" ? "active" : "";
    el("btnHouse").className = state.variant === "house" ? "active" : "";
  }

  function renderAll(data) {
    state.data = data;
    el("introHeading").textContent = data.intro.heading;
    el("introPara0").textContent = data.intro.paragraphs[0];
    el("suppliesHeading").textContent = data.supplies.heading;
    el("familyHeading").textContent = data.family_plan.heading;
    el("familyIntro").textContent = data.family_plan.intro;
    el("bagHeading").textContent = data.grab_bag.heading;
    el("bagIntro").textContent = data.grab_bag.intro;

    renderSupplies(data);
    renderFamily(data);
    renderBag(data);
    renderVariant(data);
    renderSources(data);
    updateProgress();
  }

  function switchView(view) {
    state.view = view;
    ["checklist", "family", "bag", "variant", "sources"].forEach(function (v) {
      el("view-" + v).hidden = v !== view;
    });
    document.querySelectorAll("nav.tabbar button").forEach(function (b) {
      b.classList.toggle("active", b.dataset.view === view);
    });
  }

  function init() {
    el("langSelect").value = state.lang;
    applyUIStrings();
    applyVariantButtons();

    el("langSelect").addEventListener("change", function () {
      state.lang = el("langSelect").value;
      localStorage.setItem("g72_lang", state.lang);
      applyUIStrings();
      loadData(state.lang, renderAll);
    });

    el("btnApartment").addEventListener("click", function () {
      state.variant = "apartment";
      localStorage.setItem("g72_variant", "apartment");
      applyVariantButtons();
      if (state.data) renderVariant(state.data);
    });
    el("btnHouse").addEventListener("click", function () {
      state.variant = "house";
      localStorage.setItem("g72_variant", "house");
      applyVariantButtons();
      if (state.data) renderVariant(state.data);
    });

    document.querySelectorAll("nav.tabbar button").forEach(function (b) {
      b.addEventListener("click", function () { switchView(b.dataset.view); });
    });

    el("resetBtn").addEventListener("click", function () {
      if (confirm(UI[state.lang].confirmReset)) {
        state.checks = {};
        saveChecks();
        if (state.data) renderAll(state.data);
      }
    });

    window.addEventListener("online", function () { el("offlineBanner").classList.remove("show"); });
    window.addEventListener("offline", function () { el("offlineBanner").classList.add("show"); });
    if (!navigator.onLine) el("offlineBanner").classList.add("show");

    loadData(state.lang, renderAll);

    if ("serviceWorker" in navigator) {
      navigator.serviceWorker.register("sw.js").catch(function (e) {
        console.warn("SW registration failed", e);
      });
    }
  }

  document.addEventListener("DOMContentLoaded", init);
})();

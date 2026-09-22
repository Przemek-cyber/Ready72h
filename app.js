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

  // Calls Lemon Squeezy's License API directly from the browser (no proxy) —
  // same approach as bikepackpilot.com. Optionally set EXPECTED_PRODUCT_NAME
  // to reject a key that belongs to a different Lemon Squeezy product.
  var LICENSE_API = "https://api.lemonsqueezy.com/v1/licenses";
  var EXPECTED_PRODUCT_NAME = ""; // e.g. "Ready72h" — leave empty to skip the check

  var GATE_UI = {
    pl: {
      heading: "Odblokuj Ready72h",
      intro: "Wpisz klucz licencyjny, który dostałeś po zakupie (e-mail od Lemon Squeezy).",
      placeholder: "np. XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX",
      submit: "Odblokuj", submitting: "Sprawdzam…",
      hint: "Klucz aktywujesz raz na urządzenie — potem apka działa offline.",
      errGeneric: "Nie udało się zweryfikować klucza. Spróbuj ponownie.",
      errInvalid: "Ten klucz jest nieprawidłowy albo już wykorzystany na maksymalnej liczbie urządzeń.",
      errNetwork: "Brak internetu — pierwsza aktywacja wymaga połączenia. Spróbuj ponownie, gdy będziesz online.",
      errEmpty: "Wpisz swój klucz licencyjny."
    },
    en: {
      heading: "Unlock Ready72h",
      intro: "Enter the license key you received after purchase (email from Lemon Squeezy).",
      placeholder: "e.g. XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX",
      submit: "Unlock", submitting: "Checking…",
      hint: "You activate your key once per device — after that the app works offline.",
      errGeneric: "Couldn't verify this key. Please try again.",
      errInvalid: "This key is invalid or already used on the maximum number of devices.",
      errNetwork: "No internet connection — the first activation needs one. Try again once you're online.",
      errEmpty: "Enter your license key."
    },
    de: {
      heading: "Ready72h freischalten",
      intro: "Gib den Lizenzschlüssel ein, den du nach dem Kauf erhalten hast (E-Mail von Lemon Squeezy).",
      placeholder: "z. B. XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX",
      submit: "Freischalten", submitting: "Wird geprüft…",
      hint: "Du aktivierst deinen Schlüssel einmal pro Gerät — danach funktioniert die App offline.",
      errGeneric: "Der Schlüssel konnte nicht überprüft werden. Bitte versuche es erneut.",
      errInvalid: "Dieser Schlüssel ist ungültig oder bereits auf der maximalen Anzahl Geräte aktiviert.",
      errNetwork: "Keine Internetverbindung — die erste Aktivierung braucht eine. Versuch es erneut, sobald du online bist.",
      errEmpty: "Gib deinen Lizenzschlüssel ein."
    },
    es: {
      heading: "Desbloquea Ready72h",
      intro: "Introduce la clave de licencia que recibiste al comprar (correo de Lemon Squeezy).",
      placeholder: "p. ej. XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX",
      submit: "Desbloquear", submitting: "Comprobando…",
      hint: "Activas tu clave una vez por dispositivo — después la app funciona sin conexión.",
      errGeneric: "No se pudo verificar esta clave. Inténtalo de nuevo.",
      errInvalid: "Esta clave no es válida o ya se usó en el número máximo de dispositivos.",
      errNetwork: "Sin conexión a internet — la primera activación necesita una. Vuelve a intentarlo cuando tengas conexión.",
      errEmpty: "Introduce tu clave de licencia."
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

  function deviceId() {
    var id = localStorage.getItem("g72_device_id");
    if (!id) {
      id = "dev-" + Math.random().toString(36).slice(2, 10) + Date.now().toString(36);
      localStorage.setItem("g72_device_id", id);
    }
    return id;
  }

  function isActivated() {
    return localStorage.getItem("g72_license_ok") === "1";
  }

  function setActivated(key, instanceId) {
    localStorage.setItem("g72_license_ok", "1");
    localStorage.setItem("g72_license_key", key);
    if (instanceId) localStorage.setItem("g72_license_instance", instanceId);
  }

  function applyGateStrings() {
    var t = GATE_UI[state.lang];
    el("gateHeading").textContent = t.heading;
    el("gateIntro").textContent = t.intro;
    el("gateInput").placeholder = t.placeholder;
    el("gateSubmit").textContent = t.submit;
    el("gateHint").textContent = t.hint;
  }

  function showGate() {
    el("gateScreen").hidden = false;
    el("appHeader").hidden = true;
    el("app").hidden = true;
    el("appNav").hidden = true;
  }

  function showApp() {
    el("gateScreen").hidden = true;
    el("appHeader").hidden = false;
    el("app").hidden = false;
    el("appNav").hidden = false;
  }

  function gateError(msg) {
    var e = el("gateError");
    e.textContent = msg || "";
    e.hidden = !msg;
  }

  function submitLicense() {
    var t = GATE_UI[state.lang];
    var key = el("gateInput").value.trim();
    gateError("");
    if (!key) { gateError(t.errEmpty); return; }

    var btn = el("gateSubmit");
    btn.disabled = true;
    btn.textContent = t.submitting;

    var body = "license_key=" + encodeURIComponent(key) +
      "&instance_name=" + encodeURIComponent("Ready72h-" + deviceId());

    fetch(LICENSE_API + "/activate", {
      method: "POST",
      headers: {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
      },
      body: body
    })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (data && data.activated) {
          if (EXPECTED_PRODUCT_NAME && data.meta && data.meta.product_name !== EXPECTED_PRODUCT_NAME) {
            gateError(t.errInvalid);
            return;
          }
          setActivated(key, data.instance && data.instance.id);
          showApp();
          initApp();
        } else {
          gateError((data && data.error) ? data.error : t.errInvalid);
        }
      })
      .catch(function () {
        gateError(navigator.onLine ? t.errGeneric : t.errNetwork);
      })
      .then(function () {
        btn.disabled = false;
        btn.textContent = t.submit;
      });
  }

  function initGate() {
    applyGateStrings();
    el("gateLangSelect").value = state.lang;
    el("gateLangSelect").addEventListener("change", function () {
      state.lang = el("gateLangSelect").value;
      localStorage.setItem("g72_lang", state.lang);
      applyGateStrings();
    });
    el("gateSubmit").addEventListener("click", submitLicense);
    el("gateInput").addEventListener("keydown", function (e) {
      if (e.key === "Enter") submitLicense();
    });
    el("gateInput").focus();
  }

  function initApp() {
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
  }

  function boot() {
    if ("serviceWorker" in navigator) {
      navigator.serviceWorker.register("sw.js").catch(function (e) {
        console.warn("SW registration failed", e);
      });
    }
    if (isActivated()) {
      showApp();
      initApp();
    } else {
      showGate();
      initGate();
    }
  }

  document.addEventListener("DOMContentLoaded", boot);
})();

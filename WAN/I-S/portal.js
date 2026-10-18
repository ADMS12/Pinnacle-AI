/*
  Shahawi Family Planning Portal — shared module bar.
  Every portal page includes:  <script src="portal.js" data-module="KEY"></script>
  as the first element inside <body>.

  To add a planning module later:
    1. Build the page (for example Retirement_Planning_HomePage.html) and include this script
       with its key, e.g. data-module="retirement".
    2. Change that module's status below from "planned" to "live".
  Nothing else needs to change; every page picks up the new link.
*/
(function () {
  var MODULES = [
    { key: "overview",   label: "Overview",            href: "Ihab_Shahawi_Intro.html",                  status: "live" },
    { key: "trust",      label: "Trust Planning",      href: "Estate_Trust_Info_Live_HomePage.html",     status: "live" },
    { key: "asset",      label: "Asset Protection",    href: "Ihab_Shahawi_Intro.html#s-ap-1",           status: "live",
      note: "Currently the asset protection section of the Overview; Asset_Protection_HomePage.html is planned" },
    { key: "retirement", label: "Retirement Planning", href: "Retirement_Planning_HomePage.html",        status: "planned" },
    { key: "tax",        label: "Tax Planning",        href: "Tax_Strategy_HomePage.html",               status: "planned" },
    { key: "succession", label: "Business Succession", href: "Business_Succession_HomePage.html",        status: "planned" },
    { key: "charity",    label: "Charitable Planning", href: "Charitable_Planning_HomePage.html",        status: "planned" }
  ];
  var me = document.currentScript;
  var current = me ? me.getAttribute("data-module") : "";

  var css = document.createElement("style");
  css.textContent =
    ":root{--portal-h:40px}" +
    "#portalbar{position:fixed;top:0;left:0;right:0;height:var(--portal-h);z-index:30;background:#081f3f;color:#cde2fb;" +
    "display:flex;align-items:center;gap:4px;padding:0 18px;font:13px/1 system-ui,-apple-system,'Segoe UI',sans-serif;box-shadow:0 1px 0 rgba(255,255,255,.08)}" +
    "#portalbar .pb-brand{font-weight:700;color:#fff;margin-right:14px;white-space:nowrap}" +
    "#portalbar a,#portalbar span.pb-mod{padding:6px 11px;border-radius:999px;text-decoration:none;color:#cde2fb;white-space:nowrap}" +
    "#portalbar a:hover{background:rgba(255,255,255,.12);color:#fff}" +
    "#portalbar a.pb-on{background:#2a78d6;color:#fff;font-weight:600}" +
    "#portalbar span.pb-mod{color:#6f8fb8;cursor:default}" +
    "#portalbar span.pb-mod em{font-style:normal;font-size:10px;letter-spacing:.06em;text-transform:uppercase;margin-left:5px;padding:1px 6px;border-radius:999px;background:rgba(255,255,255,.08)}" +
    "@media screen{body{padding-top:var(--portal-h)}}" +
    "@media print{#portalbar{display:none}}" +
    "@media (max-width:900px){#portalbar{overflow-x:auto}#portalbar .pb-brand{display:none}}";
  document.head.appendChild(css);

  var bar = document.createElement("nav");
  bar.id = "portalbar";
  bar.setAttribute("aria-label", "Planning modules");
  var brand = document.createElement("span");
  brand.className = "pb-brand";
  brand.textContent = "Shahawi Family Planning Portal";
  bar.appendChild(brand);
  MODULES.forEach(function (m) {
    var el;
    if (m.status === "live") {
      el = document.createElement("a");
      el.href = m.href;
      if (m.key === current) el.className = "pb-on";
      if (m.note) el.title = m.note;
    } else {
      el = document.createElement("span");
      el.className = "pb-mod";
      el.title = m.href + " · in preparation";
    }
    el.appendChild(document.createTextNode(m.label));
    if (m.status !== "live") {
      var b = document.createElement("em");
      b.textContent = "soon";
      el.appendChild(b);
    }
    bar.appendChild(el);
  });
  document.body.insertBefore(bar, document.body.firstChild);
  window.SHAHAWI_PORTAL = { modules: MODULES, current: current };

  /*
    Casual-copy deterrents. A browser must receive the page source to display it, so this cannot
    stop a determined user (or anyone who disables JavaScript); real access control is the Vercel
    password gate. What it does: blocks the right-click menu, image dragging, and the shortcuts for
    view-source (Ctrl/Cmd+U), save-page (Ctrl/Cmd+S) and developer tools (F12, Ctrl/Cmd+Shift+I/J/C,
    Cmd+Option+I/J/C). Printing (Ctrl/Cmd+P) is left alone so the deck can still be saved as PDF.
    To turn it off for a page, include the script with data-protect="off".
  */
  if (!me || me.getAttribute("data-protect") !== "off") {
    document.addEventListener("contextmenu", function (e) { e.preventDefault(); });
    document.addEventListener("dragstart", function (e) {
      if (e.target && (e.target.tagName === "IMG" || e.target.tagName === "svg" || e.target.closest && e.target.closest("svg"))) e.preventDefault();
    });
    document.addEventListener("keydown", function (e) {
      var k = (e.key || "").toLowerCase();
      var mod = e.ctrlKey || e.metaKey;
      var block =
        e.key === "F12" ||
        (mod && (k === "u" || k === "s")) ||
        (mod && e.shiftKey && (k === "i" || k === "j" || k === "c")) ||
        (e.metaKey && e.altKey && (k === "i" || k === "j" || k === "c"));
      if (block) { e.preventDefault(); e.stopPropagation(); }
    }, true);
  }
})();

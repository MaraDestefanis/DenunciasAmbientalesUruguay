
(function () {
  var BG      = '#161b22';
  var TEXT    = '#e6edf3';
  var MUTED   = '#8b949e';
  var BORDER  = '#30363d';
  var HOVER   = '#21262d';
  var SEL_BG  = 'rgba(26,188,156,0.15)';
  var SEL_FG  = '#1abc9c';

  function applyStyle(el, props) {
    Object.entries(props).forEach(function (kv) {
      el.style.setProperty(kv[0], kv[1], 'important');
    });
  }

  function fixAll() {
    /* ── control / contenedor principal ── */
    document.querySelectorAll(
      '.Select-control, [class$="__control"], [class*="__control "]'
    ).forEach(function (el) {
      applyStyle(el, {
        'background-color': BG,
        'border-color'    : BORDER,
        'box-shadow'      : 'none',
        'color'           : TEXT
      });
    });

    /* ── valor seleccionado ── */
    document.querySelectorAll(
      '.Select-value, .Select-value-label, ' +
      '[class$="__single-value"], [class*="__single-value "], ' +
      '[class$="__value-container"], [class*="__value-container "]'
    ).forEach(function (el) {
      applyStyle(el, {
        'background-color': 'transparent',
        'color'           : TEXT
      });
    });

    /* ── placeholder ── */
    document.querySelectorAll(
      '.Select-placeholder, ' +
      '[class$="__placeholder"], [class*="__placeholder "]'
    ).forEach(function (el) {
      applyStyle(el, {
        'color'           : MUTED,
        'background-color': 'transparent'
      });
    });

    /* ── input interno ── */
    document.querySelectorAll(
      '.Select-input, .Select-input input, ' +
      '[class$="__input-container"], [class*="__input-container "], ' +
      '[class$="__input-container"] input'
    ).forEach(function (el) {
      applyStyle(el, {
        'background-color': 'transparent',
        'color'           : TEXT
      });
    });

    /* ── menú desplegable ── */
    document.querySelectorAll(
      '.Select-menu-outer, .Select-menu, ' +
      '[class$="__menu"], [class*="__menu "], ' +
      '[class$="__menu-list"], [class*="__menu-list "]'
    ).forEach(function (el) {
      applyStyle(el, {
        'background-color': BG,
        'border-color'    : BORDER
      });
    });

    /* ── opciones ── */
    document.querySelectorAll(
      '.Select-option, .VirtualizedSelectOption, ' +
      '[class$="__option"], [class*="__option "]'
    ).forEach(function (el) {
      var isSelected = el.classList.toString().indexOf('is-selected') !== -1 ||
                       el.classList.toString().indexOf('--is-selected') !== -1;
      var isFocused  = el.classList.toString().indexOf('is-focused') !== -1 ||
                       el.classList.toString().indexOf('--is-focused') !== -1;
      if (isSelected) {
        applyStyle(el, { 'background-color': SEL_BG, 'color': SEL_FG });
      } else if (isFocused) {
        applyStyle(el, { 'background-color': HOVER, 'color': TEXT });
      } else {
        applyStyle(el, { 'background-color': BG, 'color': TEXT });
      }
    });

    /* ── indicadores (flecha, ×) ── */
    document.querySelectorAll(
      '.Select-arrow, ' +
      '[class$="__indicator"] svg, [class*="__indicator"] svg, ' +
      '[class$="__indicator-separator"], [class*="__indicator-separator"]'
    ).forEach(function (el) {
      applyStyle(el, { 'color': MUTED, 'border-top-color': MUTED, 'background-color': 'transparent' });
      if (el.tagName === 'svg' || el.tagName === 'path') {
        el.style.setProperty('fill', MUTED, 'important');
      }
    });
  }

  /* Corre al cargar */
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', fixAll);
  } else {
    fixAll();
  }

  /* Observer: re-aplica cuando Dash renderiza nuevos componentes */
  var observer = new MutationObserver(function (mutations) {
    var relevant = mutations.some(function (m) { return m.addedNodes.length > 0; });
    if (relevant) fixAll();
  });
  observer.observe(document.documentElement, { childList: true, subtree: true });

  /* Pases de seguridad extra al iniciar */
  setTimeout(fixAll, 300);
  setTimeout(fixAll, 800);
  setTimeout(fixAll, 2000);
})();

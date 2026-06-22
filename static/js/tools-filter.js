/* ============================================================================
   MBON tools filter — vanilla JS. Filter cards by faceted tags.
   Each [data-tool] card carries data-tags="place.Global tool.Portal".
   Each .filter-btn carries data-facet + data-value. AND across facets,
   OR within a facet. URL param ?tool=Portal pre-activates that filter.
   ========================================================================== */
(function () {
  function init() {
    var bar = document.querySelector('[data-tool-filter]');
    if (!bar) return;
    var cards = Array.prototype.slice.call(document.querySelectorAll('[data-tool]'));
    var btns = Array.prototype.slice.call(bar.querySelectorAll('.filter-btn'));
    var countEl = document.querySelector('[data-tool-count]');
    var clearEl = document.querySelector('[data-tool-clear]');
    var sel = {}; // facet -> Set(values)

    function apply() {
      var active = 0;
      Object.keys(sel).forEach(function (k) { active += sel[k].size; });
      var shown = 0;
      cards.forEach(function (card) {
        var tags = (card.getAttribute('data-tags') || '').split(/\s+/);
        var ok = Object.keys(sel).every(function (facet) {
          if (!sel[facet] || sel[facet].size === 0) return true;
          var matched = false;
          sel[facet].forEach(function (val) {
            if (tags.indexOf(facet + '.' + val) !== -1) matched = true;
          });
          return matched;
        });
        card.style.display = ok ? '' : 'none';
        if (ok) shown++;
      });
      if (countEl) countEl.textContent = shown + ' OF ' + cards.length + ' TOOLS' + (active ? ' \u00b7 ' + active + ' FILTERS' : '');
      if (clearEl) clearEl.style.display = active ? '' : 'none';
      var empty = document.querySelector('[data-tool-empty]');
      if (empty) empty.style.display = shown === 0 ? '' : 'none';
    }

    btns.forEach(function (btn) {
      btn.addEventListener('click', function () {
        var facet = btn.getAttribute('data-facet'), val = btn.getAttribute('data-value');
        if (!sel[facet]) sel[facet] = new Set();
        if (sel[facet].has(val)) { sel[facet].delete(val); btn.classList.remove('is-active'); }
        else { sel[facet].add(val); btn.classList.add('is-active'); }
        apply();
      });
    });
    if (clearEl) clearEl.addEventListener('click', function () {
      sel = {}; btns.forEach(function (b) { b.classList.remove('is-active'); }); apply();
    });

    // Pre-activate from URL param: ?tool=Portal
    var urlTool = new URLSearchParams(window.location.search).get('tool');
    if (urlTool) {
      var preBtn = bar.querySelector('[data-facet="tool"][data-value="' + urlTool + '"]');
      if (preBtn) {
        if (!sel['tool']) sel['tool'] = new Set();
        sel['tool'].add(urlTool);
        preBtn.classList.add('is-active');
      }
    }
    apply();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();

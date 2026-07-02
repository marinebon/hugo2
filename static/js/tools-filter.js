/* ============================================================================
   MBON tools filter — vanilla JS. Filter cards by faceted tags.
   Each [data-tool] card carries data-tags="place.Global tool.Portal".
   Each .filter-btn carries data-facet + data-value. AND across facets,
   OR within a facet. URL params pre-activate any facet, e.g.
   ?tool=Portal or ?method=Remote-Sensing (comma-separated for multiple).
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

    // Pre-activate from URL params for any facet with buttons, e.g.
    // ?tool=Portal, ?method=Remote-Sensing, ?place=US (comma-separated for multiple).
    var params = new URLSearchParams(window.location.search);
    var facetsPresent = {};
    btns.forEach(function (b) { facetsPresent[b.getAttribute('data-facet')] = true; });
    Object.keys(facetsPresent).forEach(function (facet) {
      var raw = params.get(facet);
      if (!raw) return;
      raw.split(',').forEach(function (val) {
        val = val.trim();
        if (!val) return;
        var preBtn = bar.querySelector('[data-facet="' + facet + '"][data-value="' + val + '"]');
        if (!preBtn) return;
        if (!sel[facet]) sel[facet] = new Set();
        sel[facet].add(val);
        preBtn.classList.add('is-active');
      });
    });
    apply();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();

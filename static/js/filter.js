/* ============================================================================
   MBON generic faceted filter — vanilla JS. Filters cards by faceted tags.
   Mirrors tools-filter.js but parameterized so any grid can reuse it:
     [data-filter]        container; data-noun="DATASETS" data-param="portal"
     [data-filter-item]   each card, carrying data-tags="portal.OBIS place.US"
     .filter-btn          data-facet + data-value (AND across facets, OR within)
     [data-filter-count]  "N OF M DATASETS · K FILTERS" readout
     [data-filter-clear]  reset button   ·   [data-filter-empty]  empty state
   URL param (?<data-param>=Value) pre-activates the matching facet button.
   ========================================================================== */
(function () {
  function init() {
    var bar = document.querySelector('[data-filter]');
    if (!bar) return;
    var noun = (bar.getAttribute('data-noun') || 'ITEMS').toUpperCase();
    var param = bar.getAttribute('data-param') || '';
    var cards = Array.prototype.slice.call(document.querySelectorAll('[data-filter-item]'));
    var btns = Array.prototype.slice.call(bar.querySelectorAll('.filter-btn'));
    var countEl = document.querySelector('[data-filter-count]');
    var clearEl = document.querySelector('[data-filter-clear]');
    var emptyEl = document.querySelector('[data-filter-empty]');
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
      if (countEl) countEl.textContent = shown + ' OF ' + cards.length + ' ' + noun + (active ? ' · ' + active + ' FILTERS' : '');
      if (clearEl) clearEl.style.display = active ? '' : 'none';
      if (emptyEl) emptyEl.style.display = shown === 0 ? '' : 'none';
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

    // Pre-activate from URL param, e.g. ?portal=OBIS
    if (param) {
      var want = new URLSearchParams(window.location.search).get(param);
      if (want) {
        var preBtn = bar.querySelector('[data-facet="' + param + '"][data-value="' + want + '"]');
        if (preBtn) {
          if (!sel[param]) sel[param] = new Set();
          sel[param].add(want);
          preBtn.classList.add('is-active');
        }
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

/* ============================================================================
   MBON papers filter — vanilla JS. Filter cards by faceted tags.
   Each [data-paper] card carries data-tags="method.Genomics type.Paper".
   Each .filter-btn carries data-facet + data-value. AND across facets,
   OR within a facet. 
   ========================================================================== */
(function () {
  document.addEventListener('DOMContentLoaded', function () {
    var bar = document.querySelector('[data-paper-filter]');
    if (!bar) return;
    var cards = Array.prototype.slice.call(document.querySelectorAll('[data-paper]'));
    var btns = Array.prototype.slice.call(bar.querySelectorAll('.filter-btn'));
    var countEl = document.querySelector('[data-paper-count]');
    var clearEl = document.querySelector('[data-paper-clear]');
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
      if (countEl) countEl.textContent = shown + ' OF ' + cards.length + ' PAPERS' + (active ? ' \u00b7 ' + active + ' FILTERS' : '');
      if (clearEl) clearEl.style.display = active ? '' : 'none';
      var empty = document.querySelector('[data-paper-empty]');
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
    apply();
  });
})();

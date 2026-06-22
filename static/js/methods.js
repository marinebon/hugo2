/* methods.js — hotspot interactivity for the methods-band illustration */
(function () {
  'use strict';

  function init() {
    const spots = Array.from(document.querySelectorAll('.method-spot'));
    if (!spots.length) return;

    function closeAll(except) {
      spots.forEach(function (s) {
        if (s === except) return;
        const tip = s.querySelector('.method-spot__tip');
        const btn = s.querySelector('.method-spot__pin');
        if (tip) tip.hidden = true;
        if (btn) btn.setAttribute('aria-expanded', 'false');
      });
    }

    spots.forEach(function (spot) {
      const pin = spot.querySelector('.method-spot__pin');
      const tip = spot.querySelector('.method-spot__tip');
      if (!pin || !tip) return;

      pin.addEventListener('click', function (e) {
        e.stopPropagation();
        const isOpen = !tip.hidden;
        closeAll(isOpen ? null : spot);
        tip.hidden = isOpen;
        pin.setAttribute('aria-expanded', String(!isOpen));
      });

      pin.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
          tip.hidden = true;
          pin.setAttribute('aria-expanded', 'false');
          pin.focus();
        }
      });
    });

    document.addEventListener('click', function () { closeAll(null); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') closeAll(null);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();

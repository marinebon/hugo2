/* methods.js — hotspot interactivity for the methods-band illustration.
   Desktop: CSS :hover handles show/hide. JS only needed for mobile click-toggle. */
(function () {
  'use strict';

  function init() {
    const spots = Array.from(document.querySelectorAll('.method-spot'));
    if (!spots.length) return;

    function closeAll(except) {
      spots.forEach(function (s) {
        if (s === except) return;
        s.classList.remove('is-active');
        const btn = s.querySelector('.method-spot__pin');
        if (btn) btn.setAttribute('aria-expanded', 'false');
      });
    }

    spots.forEach(function (spot) {
      const pin = spot.querySelector('.method-spot__pin');
      if (!pin) return;

      pin.addEventListener('click', function (e) {
        e.stopPropagation();
        const isOpen = spot.classList.contains('is-active');
        closeAll(isOpen ? null : spot);
        spot.classList.toggle('is-active', !isOpen);
        pin.setAttribute('aria-expanded', String(!isOpen));
      });

      pin.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
          spot.classList.remove('is-active');
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

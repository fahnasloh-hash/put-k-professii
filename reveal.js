(function () {
  'use strict';

  function initScrollReveal() {
    if (window.__PKP_SCROLL_REVEAL_INIT) return;
    window.__PKP_SCROLL_REVEAL_INIT = true;
    if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    var selectors = [
      '.hero__copy',
      '.hero__visual',
      '.stats',
      '.section > .section-header',
      '.section > .eyebrow',
      '.section > h1',
      '.section > h2',
      '.section > .lede',
      '.section > .two-col',
      '.section > .two-col--60-40',
      '.section > .two-col--40-60',
      '.dirs > *',
      '.featured-grid > *',
      '.choice-grid > *',
      '.steps > *',
      '.testimonials > *',
      '.faq-list > *',
      '.link-grid > *',
      '.ic-grid > *',
      '.card-grid > *',
      '.college-grid > *',
      '.blog-grid > *',
      '.hstats > *',
      '.dhero',
      '.mini-stats > *',
      '.lead-form',
      '.footer__inner > *'
    ];

    var items = Array.prototype.slice.call(document.querySelectorAll(selectors.join(',')))
      .filter(function (el) {
        return !el.closest('.modal') && !el.closest('.nav') && !el.closest('.nav__mobile') && !el.closest('.sticky-cta');
      });

    var seen = [];
    items.forEach(function (el) {
      if (seen.indexOf(el) !== -1) return;
      seen.push(el);
    });
    items = seen;
    if (!items.length) return;

    items.forEach(function (el) {
      el.setAttribute('data-reveal', '');
      if (el.getBoundingClientRect().top < window.innerHeight * 0.88) {
        el.classList.add('is-revealed');
      }
    });

    if (!('IntersectionObserver' in window)) {
      items.forEach(function (el) { el.classList.add('is-revealed'); });
      return;
    }

    var groupMap = typeof WeakMap !== 'undefined' ? new WeakMap() : null;
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var el = entry.target;
        var parent = el.parentElement;
        var index = 0;
        if (groupMap && parent) {
          index = groupMap.get(parent) || 0;
          groupMap.set(parent, index + 1);
        }
        el.style.setProperty('--reveal-delay', Math.min(index * 55, 330) + 'ms');
        el.classList.add('is-revealed');
        observer.unobserve(el);
      });
    }, { rootMargin: '0px 0px -12% 0px', threshold: 0.14 });

    items.forEach(function (el) {
      if (!el.classList.contains('is-revealed')) observer.observe(el);
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initScrollReveal);
  else initScrollReveal();
})();

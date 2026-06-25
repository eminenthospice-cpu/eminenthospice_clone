/**
 * Reveal on scroll - IntersectionObserver-driven entrance animations.
 * Drives `.reveal` and `.scale-in` classes defined in global.css.
 * Respects prefers-reduced-motion (does nothing if set).
 *
 * Import this script into BaseLayout.astro via:
 *   <script src="/motion/reveal.js" type="module"></script>
 * or inline it as a <script> block in the layout.
 */

const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

if (!prefersReduced) {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target); // animate once, then stop watching
        }
      });
    },
    {
      threshold: 0.12,
      rootMargin: '0px 0px -40px 0px',
    }
  );

  // Watch all reveal and scale-in elements
  document.querySelectorAll<HTMLElement>('.reveal, .scale-in').forEach((el) => {
    observer.observe(el);
  });
} else {
  // Reduced motion: make everything visible immediately
  document.querySelectorAll<HTMLElement>('.reveal, .scale-in').forEach((el) => {
    el.classList.add('is-visible');
  });
}

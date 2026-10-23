// Mobile menu, the "projects" dropdown, and hiding images that fail to load
// (their frame then shows a placeholder).

const nav = document.querySelector('.site-nav');
const toggle = nav.querySelector('.nav-toggle');
const menu = nav.querySelector('.has-menu');
const menuBtn = menu.querySelector('.menu-btn');

toggle.addEventListener('click', () => {
  const open = nav.classList.toggle('open');
  toggle.setAttribute('aria-expanded', String(open));
});

const setMenu = (open) => {
  menu.classList.toggle('open', open);
  menuBtn.setAttribute('aria-expanded', String(open));
};

menuBtn.addEventListener('click', () => setMenu(!menu.classList.contains('open')));

document.addEventListener('click', (e) => {
  if (!menu.contains(e.target)) setMenu(false);
});

document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') { setMenu(false); menuBtn.blur(); }
});

// Close the mobile menu after jumping to a project on the same page.
nav.querySelectorAll('.submenu a').forEach((a) => a.addEventListener('click', () => {
  nav.classList.remove('open');
  toggle.setAttribute('aria-expanded', 'false');
  setMenu(false);
}));

// Fade elements in as they scroll into view; ones entering together are staggered.
const els = document.querySelectorAll('.el');
if ('IntersectionObserver' in window) {
  const revealer = new IntersectionObserver((entries) => {
    entries.filter((e) => e.isIntersecting).forEach((e, i) => {
      e.target.style.transitionDelay = `${Math.min(i, 6) * 70}ms`;
      e.target.classList.add('in');
      revealer.unobserve(e.target);
    });
  }, { rootMargin: '0px 0px -8% 0px' });
  els.forEach((el) => revealer.observe(el));
} else {
  els.forEach((el) => el.classList.add('in'));
}

// Projects page: highlight the project in view in the right-hand list.
const indexLinks = [...document.querySelectorAll('.project-index a')];
if (indexLinks.length) {
  const tracker = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (!e.isIntersecting) return;
      indexLinks.forEach((a) => {
        if (a.hash === `#${e.target.id}`) a.setAttribute('aria-current', 'true');
        else a.removeAttribute('aria-current');
      });
    });
  }, { rootMargin: '-45% 0px -50% 0px' });
  document.querySelectorAll('section.project').forEach((s) => tracker.observe(s));
}

// Projects page: the ornament bands slide upward as the page scrolls; the
// background repeats, so the line of ornaments never ends.
if (document.querySelector('.ornament') && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
  let ticking = false;
  const update = () => {
    document.documentElement.style.setProperty('--ornament-shift', `${-scrollY * 0.6}px`);
    ticking = false;
  };
  addEventListener('scroll', () => {
    if (!ticking) { ticking = true; requestAnimationFrame(update); }
  }, { passive: true });
  update();
}

document.querySelectorAll('.img img').forEach((img) => {
  const hide = () => { img.style.visibility = 'hidden'; };
  if (img.complete && img.naturalWidth === 0) hide();
  img.addEventListener('error', hide);
});

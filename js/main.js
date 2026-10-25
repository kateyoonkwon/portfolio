// Kate Kwon portfolio: behaviour for both pages.
//
//  1. Navigation        phone menu button and the "projects" dropdown
//  2. Scroll reveal     elements fade up as they come into view
//  3. Project links     links to a project centre its cover; side list highlights the one in view
//  4. Carousels         slide strips with one slide shown large
//  5. Media fallbacks   reduced motion and images that fail to load

const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;

// 1. Navigation -------------------------------------------------------------

const nav = document.querySelector('.site-nav');
const toggle = nav.querySelector('.nav-toggle');
const menu = nav.querySelector('.has-menu');
const menuBtn = menu.querySelector('.menu-btn');

const setMenu = (open) => {
  menu.classList.toggle('open', open);
  menuBtn.setAttribute('aria-expanded', String(open));
};
const setPhoneMenu = (open) => {
  nav.classList.toggle('open', open);
  toggle.setAttribute('aria-expanded', String(open));
};

toggle.addEventListener('click', () => setPhoneMenu(!nav.classList.contains('open')));
menuBtn.addEventListener('click', () => setMenu(!menu.classList.contains('open')));

// Close the dropdown on an outside click or Escape.
document.addEventListener('click', (e) => { if (!menu.contains(e.target)) setMenu(false); });
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') { setMenu(false); menuBtn.blur(); }
});

// Close both menus after jumping to a project.
nav.querySelectorAll('.submenu a').forEach((a) => a.addEventListener('click', () => {
  setPhoneMenu(false);
  setMenu(false);
}));

// 2. Scroll reveal ----------------------------------------------------------
// The page's <head> adds html.reveal; CSS hides .el until it gets .in. Elements
// entering together are staggered.

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

// 3. Project links ----------------------------------------------------------
// Any link to a project (side list, "projects" dropdown, the home page's list)
// lands with that project's cover centred on screen. The cover's position is
// measured without its fade-in offset (section 2).

const centreCover = (hash, behavior) => {
  const cover = document.getElementById(hash.slice(1))?.querySelector('.cover');
  if (!cover) return false;
  const box = cover.getBoundingClientRect();
  const fade = new DOMMatrixReadOnly(getComputedStyle(cover).transform).m42;
  scrollTo({ top: scrollY + box.top - fade + box.height / 2 - innerHeight / 2, behavior });
  return true;
};

// Links within this page glide there (smoothly, unless reduced motion is on: see
// html's scroll-behavior). Links from the home page arrive at the top of the
// project (the browser's own jump); centre it once the page and fonts have loaded.
const page = (path) => path.replace(/(\/index)?\.html$/, '').replace(/\/$/, '');
document.querySelectorAll('a[href*="#"]').forEach((a) => a.addEventListener('click', (e) => {
  if (page(a.pathname) !== page(location.pathname) || !centreCover(a.hash)) return;
  e.preventDefault();
  history.pushState(null, '', a.hash);
}));
addEventListener('hashchange', () => centreCover(location.hash));   // a hash typed into the address bar
if (location.hash) {
  addEventListener('load', () => document.fonts.ready.then(() => {
    requestAnimationFrame(() => centreCover(location.hash, 'instant'));
  }));
}

// Highlight the project in view in the side list.
const indexLinks = [...document.querySelectorAll('.project-index a')];
if (indexLinks.length) {
  const tracker = new IntersectionObserver((entries) => {
    entries.filter((e) => e.isIntersecting).forEach((e) => {
      indexLinks.forEach((a) => {
        if (a.hash === `#${e.target.id}`) a.setAttribute('aria-current', 'true');
        else a.removeAttribute('aria-current');
      });
    });
  }, { rootMargin: '-45% 0px -50% 0px' });
  document.querySelectorAll('section.project').forEach((s) => tracker.observe(s));
}

// 4. Carousels --------------------------------------------------------------
// Arrows, clicking a slide, or the arrow keys move between slides. A carousel
// advances on its own (while visible and not hovered) until the visitor uses it.

const pad = (n) => String(n).padStart(2, '0');

document.querySelectorAll('.carousel').forEach((car) => {
  const slides = [...car.querySelectorAll('.slide')];
  const count = car.querySelector('.count');
  let i = 0;
  let auto = !reduceMotion;
  let hovering = false;
  let visible = false;

  const show = (n) => {
    i = (n + slides.length) % slides.length;
    car.style.setProperty('--i', i);
    slides.forEach((s, k) => (k === i ? s.setAttribute('aria-current', 'true') : s.removeAttribute('aria-current')));
    count.textContent = `${pad(i + 1)} / ${pad(slides.length)}`;
  };
  const go = (n) => { auto = false; show(n); };

  car.querySelector('.prev').addEventListener('click', () => go(i - 1));
  car.querySelector('.next').addEventListener('click', () => go(i + 1));
  slides.forEach((s, k) => s.addEventListener('click', () => go(k)));
  car.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowRight') go(i + 1);
    if (e.key === 'ArrowLeft') go(i - 1);
  });
  car.addEventListener('pointerenter', () => { hovering = true; });
  car.addEventListener('pointerleave', () => { hovering = false; });
  new IntersectionObserver(([e]) => { visible = e.isIntersecting; }).observe(car);
  setInterval(() => { if (auto && visible && !hovering && !document.hidden) show(i + 1); }, 3500);
});

// 5. Media fallbacks --------------------------------------------------------

// Looping videos stay paused on their poster for visitors who prefer reduced motion.
if (reduceMotion) {
  document.querySelectorAll('video[autoplay]').forEach((v) => { v.removeAttribute('autoplay'); v.pause(); });
}

// A missing image is hidden so its frame shows the striped placeholder instead.
document.querySelectorAll('.img img').forEach((img) => {
  const hide = () => { img.style.visibility = 'hidden'; };
  if (img.complete && img.naturalWidth === 0) hide();
  img.addEventListener('error', hide);
});

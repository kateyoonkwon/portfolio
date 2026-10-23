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

document.querySelectorAll('.img img').forEach((img) => {
  const hide = () => { img.style.visibility = 'hidden'; };
  if (img.complete && img.naturalWidth === 0) hide();
  img.addEventListener('error', hide);
});

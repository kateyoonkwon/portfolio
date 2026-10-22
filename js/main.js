// Highlight the nav link for the section in view, toggle the mobile menu,
// and hide images that have not been supplied yet (their frame shows a placeholder).

const nav = document.querySelector('.site-nav');
const links = [...nav.querySelectorAll('a')];
const toggle = nav.querySelector('.nav-toggle');

toggle.addEventListener('click', () => {
  const open = nav.classList.toggle('open');
  toggle.setAttribute('aria-expanded', String(open));
});

links.forEach((a) => a.addEventListener('click', () => {
  nav.classList.remove('open');
  toggle.setAttribute('aria-expanded', 'false');
}));

const setCurrent = (id) => {
  links.forEach((a) => a.setAttribute('aria-current', String(a.hash === `#${id}`)));
};

const observer = new IntersectionObserver((entries) => {
  entries.forEach((e) => { if (e.isIntersecting) setCurrent(e.target.id); });
}, { rootMargin: '-45% 0px -50% 0px' });

document.querySelectorAll('section[data-nav]').forEach((s) => observer.observe(s));
setCurrent('home');

document.querySelectorAll('.img img').forEach((img) => {
  const hide = () => { img.style.visibility = 'hidden'; };
  if (img.complete && img.naturalWidth === 0) hide();
  img.addEventListener('error', hide);
});

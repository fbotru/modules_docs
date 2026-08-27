const header = document.querySelector('.site-header');
const navToggle = document.querySelector('.nav-toggle');
const siteNav = document.querySelector('.site-nav');

const setNavigation = (open) => {
  header.classList.toggle('nav-open', open);
  navToggle.setAttribute('aria-expanded', String(open));
  document.body.classList.toggle('nav-locked', open);
};

navToggle.addEventListener('click', () => {
  setNavigation(!header.classList.contains('nav-open'));
});

siteNav.addEventListener('click', (event) => {
  if (event.target.closest('a')) setNavigation(false);
});

document.addEventListener('click', (event) => {
  if (header.classList.contains('nav-open') && !header.contains(event.target)) {
    setNavigation(false);
  }
});

document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape' && header.classList.contains('nav-open')) {
    setNavigation(false);
    navToggle.focus();
  }
});

window.addEventListener('resize', () => {
  if (window.innerWidth > 900) setNavigation(false);
});

const updateHeader = () => {
  header.classList.toggle('is-scrolled', window.scrollY > 24);
};

updateHeader();
window.addEventListener('scroll', updateHeader, { passive: true });

const dialog = document.querySelector('.lightbox');
const dialogImage = dialog.querySelector('img');
const dialogTitle = dialog.querySelector('#lightbox-title');
const closeButton = dialog.querySelector('.lightbox__close');
let dialogOpener = null;

document.querySelectorAll('.smm-card, .style-card').forEach((card) => {
  card.addEventListener('click', () => {
    dialogOpener = card;
    dialogImage.src = card.dataset.image;
    dialogImage.alt = card.querySelector('img').alt;
    dialogImage.width = Number(card.dataset.width);
    dialogImage.height = Number(card.dataset.height);
    dialogTitle.textContent = card.dataset.title;

    if (typeof dialog.showModal === 'function') {
      dialog.showModal();
    } else {
      window.location.assign(card.dataset.image);
    }
  });
});

closeButton.addEventListener('click', () => dialog.close());

dialog.addEventListener('click', (event) => {
  const bounds = dialog.getBoundingClientRect();
  const outside =
    event.clientX < bounds.left ||
    event.clientX > bounds.right ||
    event.clientY < bounds.top ||
    event.clientY > bounds.bottom;
  if (outside) dialog.close();
});

dialog.addEventListener('close', () => {
  if (dialogOpener) dialogOpener.focus();
});

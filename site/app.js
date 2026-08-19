const dialog = document.querySelector('.lightbox');
const dialogImage = dialog.querySelector('img');
const dialogTitle = dialog.querySelector('p');

document.querySelectorAll('.gallery-card').forEach((card) => {
  card.addEventListener('click', () => {
    dialogImage.src = card.dataset.image;
    dialogImage.alt = `Визуальный стиль ${card.dataset.title}`;
    dialogTitle.textContent = card.dataset.title;
    dialog.showModal();
  });
});

dialog.querySelector('.lightbox__close').addEventListener('click', () => {
  dialog.close();
});

dialog.addEventListener('click', (event) => {
  if (event.target === dialog) dialog.close();
});

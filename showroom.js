'use strict';
const filterButtons = document.querySelectorAll('[data-filter]');
filterButtons.forEach(button => button.addEventListener('click', () => {
    const filter = button.dataset.filter;
    filterButtons.forEach(item => item.setAttribute('aria-pressed', String(item === button)));
    let count = 0;
    document.querySelectorAll('.app-card').forEach(card => {
        card.hidden = filter !== 'all' && card.dataset.platform !== filter;
        if (!card.hidden) count++;
    });
    document.getElementById('filter-status').textContent = document.documentElement.lang === 'ko' ? `앱 ${count}개 표시 중` : `Showing ${count} apps`;
}));
const deviceButtons = document.querySelectorAll('[data-device]');
deviceButtons.forEach(button => button.addEventListener('click', () => {
    deviceButtons.forEach(item => item.setAttribute('aria-pressed', String(item === button)));
    document.querySelectorAll('[data-gallery]').forEach(gallery => {
        gallery.hidden = gallery.dataset.gallery !== button.dataset.device;
    });
}));
const dialog = document.querySelector('.lightbox');
if (dialog) {
    let images = [], current = 0, opener;
    const image = dialog.querySelector('img');
    const show = () => {
        image.src = images[current].src;
        image.alt = images[current].alt;
        dialog.querySelector('.image-count').textContent = `${current + 1} / ${images.length}`;
    };
    const next = direction => { current = (current + direction + images.length) % images.length; show(); };
    document.querySelectorAll('.screenshot').forEach(button => button.addEventListener('click', () => {
        opener = button;
        images = [...button.closest('.screenshots').querySelectorAll('img')];
        current = images.indexOf(button.querySelector('img'));
        show(); dialog.showModal(); document.body.style.overflow = 'hidden';
    }));
    dialog.querySelector('.close').addEventListener('click', () => dialog.close());
    dialog.querySelector('.previous').addEventListener('click', () => next(-1));
    dialog.querySelector('.next').addEventListener('click', () => next(1));
    dialog.addEventListener('click', event => { if (event.target === dialog) dialog.close(); });
    dialog.addEventListener('keydown', event => {
        if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') { event.preventDefault(); next(event.key === 'ArrowLeft' ? -1 : 1); }
    });
    dialog.addEventListener('close', () => { document.body.style.overflow = ''; opener?.focus(); });
}

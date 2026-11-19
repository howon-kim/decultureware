'use strict';
const collection = document.getElementById('apps');

if (collection) {
    const platforms = collection.querySelectorAll('[data-filter-platform]');
    const purposes = collection.querySelectorAll('[data-filter-purpose]');
    const cards = collection.querySelectorAll('.app-card');
    const empty = collection.querySelector('.empty-apps');
    const status = collection.querySelector('#filter-status');
    const countLabels = {
        en: count => `${count} ${count === 1 ? 'app' : 'apps'} shown`,
        ko: count => `앱 ${count}개 표시 중`,
        ja: count => `${count}件のアプリを表示中`
    };
    const countLabel = countLabels[document.documentElement.lang] || countLabels.en;
    let platform = 'all';
    let purpose = 'all';

    function updateApps() {
        let count = 0;
        cards.forEach(card => {
            const matchesPlatform = platform === 'all' || card.dataset.platform === platform;
            const matchesPurpose = purpose === 'all' || card.dataset.category === purpose;
            card.hidden = !matchesPlatform || !matchesPurpose;
            if (!card.hidden) count++;
        });
        platforms.forEach(button => {
            button.setAttribute('aria-pressed', String(button.dataset.filterPlatform === platform));
        });
        purposes.forEach(button => {
            button.setAttribute('aria-pressed', String(button.dataset.filterPurpose === purpose));
        });
        empty.hidden = count !== 0;
        status.textContent = countLabel(count);
    }

    platforms.forEach(button => button.addEventListener('click', () => {
        platform = button.dataset.filterPlatform;
        updateApps();
    }));
    purposes.forEach(button => button.addEventListener('click', () => {
        purpose = button.dataset.filterPurpose;
        updateApps();
    }));
    collection.querySelector('[data-clear-filters]').addEventListener('click', () => {
        platform = purpose = 'all';
        updateApps();
        platforms[0].focus();
    });
    collection.querySelectorAll('[data-app-filters]').forEach(group => { group.hidden = false; });
}

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

(() => {
    'use strict';
    const root = document.documentElement;
    const system = window.matchMedia('(prefers-color-scheme: dark)');
    let button;

    function apply(dark) {
        root.dataset.theme = dark ? 'dark' : 'light';
        for (const meta of document.querySelectorAll('meta[name="theme-color"]')) {
            meta.content = dark ? '#191c19' : '#f7f6f2';
        }
        if (button) button.setAttribute('aria-pressed', String(dark));
    }

    function followSystem() {
        apply(system.matches);
    }

    followSystem();
    system.addEventListener('change', followSystem);
    window.addEventListener('pageshow', event => {
        if (event.persisted) followSystem();
    });

    document.addEventListener('DOMContentLoaded', () => {
        const header = document.querySelector('.header');
        if (!header) return;
        button = document.createElement('button');
        button.type = 'button';
        button.className = 'theme-toggle';
        const labels = {en: 'Dark mode', ko: '다크 모드', ja: 'ダークモード'};
        button.setAttribute('aria-label', labels[root.lang] || labels.en);
        button.setAttribute('aria-pressed', String(root.dataset.theme === 'dark'));
        button.addEventListener('click', () => apply(root.dataset.theme !== 'dark'));
        (header.querySelector('nav') || header).append(button);
    }, {once: true});
})();

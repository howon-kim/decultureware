'use strict';

const typeLens = document.querySelector('.type-lens');
if (typeLens && window.PointerEvent && window.CSS?.supports('clip-path', 'circle(1px at 0 0)')) {
    let x, y, frame = 0, pointer;

    function place(nextX, nextY) {
        x = Math.max(0, Math.min(1, nextX));
        y = Math.max(0, Math.min(1, nextY));
        typeLens.style.setProperty('--lens-x', `${x * 100}%`);
        typeLens.style.setProperty('--lens-y', `${y * 100}%`);
    }

    function park() {
        cancelAnimationFrame(frame);
        frame = 0;
        place(.5, .5);
    }

    function follow(event) {
        if (!event.isPrimary) return;
        pointer = event;
        if (frame) return;
        frame = requestAnimationFrame(() => {
            frame = 0;
            const bounds = typeLens.getBoundingClientRect();
            place((pointer.clientX - bounds.left) / bounds.width,
                  (pointer.clientY - bounds.top) / bounds.height);
        });
    }

    typeLens.addEventListener('pointerdown', follow);
    typeLens.addEventListener('pointermove', follow);
    typeLens.addEventListener('pointerleave', event => {
        if (event.pointerType === 'mouse') park();
    });

    const steps = { ArrowLeft: [-.06, 0], ArrowRight: [.06, 0], ArrowUp: [0, -.12], ArrowDown: [0, .12] };
    typeLens.addEventListener('keydown', event => {
        const step = steps[event.key];
        if (!step || event.altKey || event.ctrlKey || event.metaKey) return;
        event.preventDefault();
        cancelAnimationFrame(frame);
        frame = 0;
        place(x + step[0], y + step[1]);
    });

    park();
    typeLens.tabIndex = 0;
    typeLens.setAttribute('aria-keyshortcuts', 'ArrowLeft ArrowRight ArrowUp ArrowDown');
}

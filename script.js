document.querySelectorAll('.word').forEach(word => {
    word.addEventListener('mouseenter', function() {
        this.textContent = this.dataset.hover;
    });

    word.addEventListener('mouseleave', function() {
        this.textContent = this.dataset.original;
    });
});

// Button navigation
document.getElementById('habitplate').addEventListener('click', function() {
    window.location.href = '/habitplate/index.html';
});

document.getElementById('baytransit').addEventListener('click', function() {
    // Add navigation when page is ready
    console.log('BayTransit clicked');
});

document.getElementById('workone').addEventListener('click', function() {
    // Add navigation when page is ready
    console.log('WorkOne clicked');
});

// Create multiple star layers for warp effect
function createStarLayer() {
    const star = document.createElement('div');
    star.className = 'star';
    star.style.left = Math.random() * 100 + 'vw';
    star.style.top = Math.random() * 100 + 'vh';
    star.style.animationDelay = Math.random() * 5 + 's';
    document.body.appendChild(star);
}

for (let i = 0; i < 1000; i++) {
    createStarLayer();
}

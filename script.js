// Lightbox
var lbImages = [];
var lbIndex = 0;
var lbTouchStartX = 0;

(function () {
    var lb = document.createElement('div');
    lb.id = 'lightbox';

    var prev = document.createElement('button');
    prev.id = 'lightbox-prev';
    prev.innerHTML = '&#8249;';
    prev.addEventListener('click', function (e) { e.stopPropagation(); lbNavigate(-1); });

    var lbImg = document.createElement('img');
    lbImg.id = 'lightbox-img';
    lbImg.addEventListener('click', function (e) { e.stopPropagation(); });

    var next = document.createElement('button');
    next.id = 'lightbox-next';
    next.innerHTML = '&#8250;';
    next.addEventListener('click', function (e) { e.stopPropagation(); lbNavigate(1); });

    lb.appendChild(prev);
    lb.appendChild(lbImg);
    lb.appendChild(next);
    document.body.appendChild(lb);

    lb.addEventListener('click', closeLightbox);

    lb.addEventListener('touchstart', function (e) {
        lbTouchStartX = e.touches[0].clientX;
    }, { passive: true });

    lb.addEventListener('touchend', function (e) {
        var diff = lbTouchStartX - e.changedTouches[0].clientX;
        if (Math.abs(diff) > 50) lbNavigate(diff > 0 ? 1 : -1);
    });

    document.addEventListener('keydown', function (e) {
        var lb = document.getElementById('lightbox');
        if (!lb.classList.contains('active')) return;
        if (e.key === 'Escape') closeLightbox();
        else if (e.key === 'ArrowLeft') lbNavigate(-1);
        else if (e.key === 'ArrowRight') lbNavigate(1);
    });
})();

function lbNavigate(dir) {
    lbIndex = (lbIndex + dir + lbImages.length) % lbImages.length;
    var img = document.getElementById('lightbox-img');
    img.src = lbImages[lbIndex].src;
    img.alt = lbImages[lbIndex].alt || '';
}

function openLightbox(galleryImgs, index) {
    lbImages = galleryImgs;
    lbIndex = index;
    var img = document.getElementById('lightbox-img');
    img.src = lbImages[lbIndex].src;
    img.alt = lbImages[lbIndex].alt || '';
    var show = lbImages.length > 1;
    document.getElementById('lightbox-prev').style.display = show ? '' : 'none';
    document.getElementById('lightbox-next').style.display = show ? '' : 'none';
    document.getElementById('lightbox').classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeLightbox() {
    document.getElementById('lightbox').classList.remove('active');
    document.body.style.overflow = '';
}

document.querySelectorAll('.gallery-img').forEach(function (img) {
    img.addEventListener('click', function () {
        var track = this.closest('.gallery-track');
        var imgs = Array.from(track.querySelectorAll('img'));
        openLightbox(imgs, imgs.indexOf(this));
    });
});

// Word hover effect
document.querySelectorAll('.word').forEach(word => {
    word.addEventListener('mouseenter', function() {
        this.textContent = this.dataset.hover;
    });

    word.addEventListener('mouseleave', function() {
        this.textContent = this.dataset.original;
    });
});

// Gallery scroll function
const baytransitImages = {
    iphone: ['AppStore-1.jpg','AppStore-2.jpg','AppStore-3.jpg','AppStore-4.jpg','AppStore-5.jpg','AppStore-6.jpg'],
    ipad:   ['AppStore-iPad-1.jpg','AppStore-iPad-2.jpg','AppStore-iPad-3.jpg','AppStore-iPad-4.jpg','AppStore-iPad-5.jpg','AppStore-iPad-6.jpg']
};

function switchBayTransitView(device) {
    const gallery = document.getElementById('baytransit-gallery');
    const imgs = gallery.querySelectorAll('img');
    imgs.forEach((img, i) => {
        img.src = 'baytransit/images/' + baytransitImages[device][i];
    });
    gallery.scrollLeft = 0;
    document.getElementById('bt-iphone-btn').classList.toggle('active', device === 'iphone');
    document.getElementById('bt-ipad-btn').classList.toggle('active', device === 'ipad');

}

function scrollGallery(galleryId, direction) {
    const gallery = document.getElementById(galleryId);
    if (gallery) {
        const scrollAmount = 200;
        gallery.scrollBy({
            left: direction * scrollAmount,
            behavior: 'smooth'
        });
    }
}

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            const navHeight = document.querySelector('.floating-nav').offsetHeight;
            const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - navHeight - 20;
            window.scrollTo({
                top: targetPosition,
                behavior: 'smooth'
            });
        }
    });
});

// Intersection Observer for fade-in animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Apply fade-in animation to app sections
document.querySelectorAll('.app-section .row').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(30px)';
    el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(el);
});

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

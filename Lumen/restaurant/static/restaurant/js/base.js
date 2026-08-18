document.addEventListener('DOMContentLoaded', function () {
    const preloader = document.getElementById('lmPreloader');
    if (preloader) {
        window.addEventListener('load', function () {
            preloader.classList.add('lm-preloader-hidden');
            setTimeout(() => preloader.remove(), 600);
        });
    }


    const animatedEls = document.querySelectorAll('.lm-animate');
    if (animatedEls.length && 'IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('lm-visible');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.15, rootMargin: '0px 0px -40px 0px' });

        animatedEls.forEach(el => observer.observe(el));
    } else {
        animatedEls.forEach(el => el.classList.add('lm-visible'));
    }
});
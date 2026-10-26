(() => {
    const body = document.body;
    const root = document.documentElement;
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
    const finePointer = window.matchMedia('(hover: hover) and (pointer: fine)');
    const storageKey = 'kaijing-motion';
    const activeAnimations = new Set();
    let storedPreference;
    try { storedPreference = localStorage.getItem(storageKey); } catch (_) { /* Storage is optional. */ }
    let enabled = !reduced.matches && storedPreference !== 'off';
    let pointerFrame = 0;
    let lastPointer;

    const nav = document.querySelector('.quick-nav');
    let indicator = nav?.querySelector('.nav-indicator');
    if (nav && !indicator) {
        indicator = document.createElement('span');
        indicator.className = 'nav-indicator';
        indicator.setAttribute('aria-hidden', 'true');
        nav.append(indicator);
    }

    let toggle = document.getElementById('motion-toggle');
    if (!toggle && document.querySelector('.site-header')) {
        toggle = document.createElement('button');
        toggle.id = 'motion-toggle';
        toggle.type = 'button';
        document.querySelector('.site-header').append(toggle);
    }

    const dust = document.createElement('div');
    dust.className = 'cosmic-dust';
    dust.setAttribute('aria-hidden', 'true');
    for (let i = 0; i < 22; i++) {
        const star = document.createElement('span');
        star.style.left = `${(i * 43 + 7) % 100}%`;
        star.style.top = `${(i * 31 + 11) % 100}%`;
        dust.append(star);
    }
    body.prepend(dust);

    const portraitCell = document.querySelector('.portrait-cell');
    const portrait = portraitCell?.querySelector(':scope > a');
    let portraitMessage;
    let greetingTimer;

    function sparklesAt(element) {
        if (!enabled || document.hidden) return;
        const rect = element.getBoundingClientRect();
        for (let i = 0; i < 8; i++) {
            const angle = Math.PI * 2 * i / 8;
            const spark = document.createElement('span');
            spark.className = 'stardust-spark';
            spark.textContent = i % 2 ? '✧' : '✦';
            spark.setAttribute('aria-hidden', 'true');
            spark.style.left = `${rect.left + rect.width / 2}px`;
            spark.style.top = `${rect.top + rect.height / 2}px`;
            spark.style.setProperty('--spark-dx', `${Math.cos(angle) * (42 + i % 3 * 15)}px`);
            spark.style.setProperty('--spark-dy', `${Math.sin(angle) * (42 + i % 3 * 15)}px`);
            spark.style.setProperty('--spark-color', ['#839d6a', '#96a9bc', '#b19b68'][i % 3]);
            body.append(spark);
            window.setTimeout(() => spark.remove(), 1050);
        }
    }

    if (portraitCell && portrait) {
        const greet = document.createElement('button');
        greet.type = 'button';
        greet.className = 'portrait-greet';
        greet.textContent = 'Say hello ✧';
        portraitMessage = document.createElement('span');
        portraitMessage.className = 'portrait-hello';
        portraitMessage.setAttribute('role', 'status');
        portraitCell.append(greet, portraitMessage);
        greet.addEventListener('click', () => {
            window.clearTimeout(greetingTimer);
            portraitMessage.textContent = 'Hi! Welcome to my little universe.';
            portraitMessage.classList.add('is-visible');
            sparklesAt(greet);
            greetingTimer = window.setTimeout(() => portraitMessage.classList.remove('is-visible'), 3000);
        });
    }

    function resetPointer() {
        cancelAnimationFrame(pointerFrame);
        pointerFrame = 0;
        dust.style.removeProperty('--sky-x');
        dust.style.removeProperty('--sky-y');
        portrait?.style.removeProperty('--portrait-rx');
        portrait?.style.removeProperty('--portrait-ry');
    }

    function updatePointer() {
        pointerFrame = 0;
        if (!enabled || !finePointer.matches || document.hidden || !lastPointer) return;
        const { x, y, target } = lastPointer;
        dust.style.setProperty('--sky-x', `${(x / window.innerWidth - .5) * 9}px`);
        dust.style.setProperty('--sky-y', `${(y / window.innerHeight - .5) * 7}px`);
        if (portrait && portraitCell.contains(target)) {
            const rect = portrait.getBoundingClientRect();
            const px = Math.max(-.5, Math.min(.5, (x - rect.left) / rect.width - .5));
            const py = Math.max(-.5, Math.min(.5, (y - rect.top) / rect.height - .5));
            portrait.style.setProperty('--portrait-rx', `${-py * 8}deg`);
            portrait.style.setProperty('--portrait-ry', `${px * 10}deg`);
        } else {
            portrait?.style.removeProperty('--portrait-rx');
            portrait?.style.removeProperty('--portrait-ry');
        }
    }

    document.addEventListener('pointermove', event => {
        if (!enabled || !finePointer.matches || document.hidden) return;
        lastPointer = { x: event.clientX, y: event.clientY, target: event.target };
        if (!pointerFrame) pointerFrame = requestAnimationFrame(updatePointer);
    }, { passive: true });
    document.addEventListener('pointerleave', resetPointer);

    function updateMarker() {
        const selected = nav?.querySelector('a[aria-current="page"]');
        if (!selected || !indicator) return;
        const a = selected.getBoundingClientRect();
        const n = nav.getBoundingClientRect();
        indicator.style.setProperty('--marker-x', `${a.left - n.left + 10}px`);
        indicator.style.setProperty('--marker-y', `${a.bottom - n.top - 3}px`);
        indicator.style.setProperty('--marker-width', `${Math.max(14, a.width - 20)}px`);
    }

    const footer = document.querySelector('.site-footer');
    if (footer) {
        footer.classList.add('has-surprise');
        const surprise = document.createElement('button');
        surprise.type = 'button';
        surprise.className = 'orbit-surprise';
        surprise.textContent = '✦';
        surprise.setAttribute('aria-label', 'A little stardust');
        const message = document.createElement('span');
        message.className = 'orbit-message';
        message.setAttribute('role', 'status');
        footer.append(surprise, message);
        let messageTimer;
        surprise.addEventListener('click', () => {
            window.clearTimeout(messageTimer);
            sparklesAt(surprise);
            message.textContent = 'A little curiosity goes a long way.';
            message.classList.add('is-visible');
            messageTimer = window.setTimeout(() => message.classList.remove('is-visible'), 2800);
        });
    }

    function applyMotionPreference() {
        enabled = !reduced.matches && storedPreference !== 'off';
        body.dataset.motion = enabled ? 'on' : 'off';
        root.dataset.motion = body.dataset.motion;
        if (toggle) {
            toggle.textContent = reduced.matches ? 'Reduced motion' : enabled ? 'Motion on' : 'Motion off';
            toggle.setAttribute('aria-label', 'Animations');
            toggle.setAttribute('aria-pressed', String(enabled));
            toggle.title = reduced.matches ? 'Your system preference reduces motion' : enabled ? 'Pause animations' : 'Resume animations';
            toggle.disabled = reduced.matches;
        }
        if (!enabled) {
            resetPointer();
            activeAnimations.forEach(animation => animation.cancel());
            activeAnimations.clear();
            document.querySelectorAll('.stardust-spark').forEach(spark => spark.remove());
        }
    }

    toggle?.addEventListener('click', () => {
        storedPreference = enabled ? 'off' : 'on';
        try { localStorage.setItem(storageKey, storedPreference); } catch (_) { /* Keep the current page preference. */ }
        applyMotionPreference();
        updateMarker();
    });
    reduced.addEventListener('change', applyMotionPreference);
    finePointer.addEventListener('change', resetPointer);

    const seen = new WeakSet();
    const revealTargets = [...document.querySelectorAll('.about-copy > p, .about-note, .portrait-cell > a, .education-item, .publication-table tr, .experience-table tr, .writing-card, .toy-card')];
    if ('IntersectionObserver' in window && typeof Element.prototype.animate === 'function') {
        const reveal = new IntersectionObserver(entries => {
            entries.filter(entry => entry.isIntersecting).forEach((entry, index) => {
                if (seen.has(entry.target)) return;
                seen.add(entry.target);
                reveal.unobserve(entry.target);
                if (!enabled || document.hidden) return;
                const animation = entry.target.animate(
                    [{ opacity: .15, translate: '0 16px' }, { opacity: 1, translate: '0 0' }],
                    { duration: 520, delay: Math.min(index, 5) * 50, easing: 'cubic-bezier(.2,.7,.2,1)' }
                );
                activeAnimations.add(animation);
                animation.finished.catch(() => {}).finally(() => activeAnimations.delete(animation));
            });
        }, { threshold: .06 });
        revealTargets.forEach(target => reveal.observe(target));
    }

    if ('ResizeObserver' in window && nav) new ResizeObserver(updateMarker).observe(nav);
    document.fonts?.ready.then(updateMarker);
    window.addEventListener('resize', updateMarker, { passive: true });
    window.addEventListener('hashchange', () => { resetPointer(); requestAnimationFrame(updateMarker); });
    document.addEventListener('visibilitychange', () => {
        body.classList.toggle('is-page-hidden', document.hidden);
        if (document.hidden) {
            resetPointer();
            activeAnimations.forEach(animation => animation.finish());
        }
    });
    applyMotionPreference();
    body.classList.add('motion-ready');
    updateMarker();
})();

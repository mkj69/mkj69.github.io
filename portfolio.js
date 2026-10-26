(() => {
    const header = document.querySelector('.portfolio-page .site-header, .toys-page .site-header');
    if (!header || typeof HTMLDialogElement === 'undefined' || !HTMLDialogElement.prototype.showModal) return;

    const make = (tag, className, value) => {
        const element = document.createElement(tag);
        if (className) element.className = className;
        if (value) element.textContent = value;
        return element;
    };
    const normalize = value => value.normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
    const entries = [];
    const known = new Set();
    const onToys = document.body.classList.contains('toys-page');
    const homeUrl = new URL(onToys ? '../' : './', window.location.href);
    const toysUrl = new URL('toys/', homeUrl);
    let indexLoading = true;
    let indexIncomplete = false;
    function add(anchor, kind, description = '', baseUrl = window.location.href) {
        const title = anchor.textContent.replace(/\s+/g, ' ').trim().replace(/\s*↗$/, '');
        const url = new URL(anchor.getAttribute('href'), baseUrl);
        if (!title || !['http:', 'https:'].includes(url.protocol)) return;
        const key = `${url.href}|${title}`;
        if (known.has(key)) return;
        known.add(key);
        entries.push({ title, kind, description: description.replace(/\s+/g, ' ').trim(), href: url.href,
            target: anchor.target, rel: anchor.rel, titleKey: normalize(title),
            searchKey: normalize(`${title} ${kind} ${description}`) });
    }
    document.querySelectorAll('.quick-nav a').forEach(anchor => add(anchor, anchor.hash ? 'Section' : 'Page'));
    function indexPage(page, baseUrl) {
        page.querySelectorAll('.publication-table .paper-title a').forEach(anchor => {
            const row = anchor.closest('tr');
            add(anchor, 'Publication', [...row.querySelectorAll('.paper-authors, .paper-meta')].map(el => el.textContent).join(' '), baseUrl);
        });
        page.querySelectorAll('.writing-card h3 a').forEach(anchor => {
            const card = anchor.closest('.writing-card');
            add(anchor, 'Writing', [...card.querySelectorAll('.writing-card-body > p, .writing-tags')].map(el => el.textContent).join(' '), baseUrl);
        });
        page.querySelectorAll('.toy-card h2 a').forEach(anchor => {
            add(anchor, 'Toy', anchor.closest('.toy-card').querySelector('.toy-description')?.textContent || '', baseUrl);
        });
    }
    indexPage(document, window.location.href);

    const trigger = make('button', 'portfolio-search-trigger');
    trigger.type = 'button';
    trigger.setAttribute('aria-label', 'Quick find');
    trigger.title = 'Find papers, notes, and sections';
    trigger.append(make('span', 'search-trigger-icon', '⌕'), make('span', 'search-trigger-label', 'Find'),
        make('kbd', '', /Mac|iPhone|iPad/.test(navigator.platform) ? '⌘ K' : 'Ctrl K'));
    header.append(trigger);

    const dialog = make('dialog', 'portfolio-search');
    dialog.setAttribute('aria-labelledby', 'search-title');
    const head = make('div', 'search-head');
    const heading = make('h2', '', 'Quick find');
    heading.id = 'search-title';
    const subtitle = make('p', 'search-subtitle', 'Papers, notes, and places on this site.');
    const close = make('button', 'search-close', '×');
    close.type = 'button';
    close.setAttribute('aria-label', 'Close search');
    head.append(heading, subtitle, close);
    const input = make('input', 'search-input');
    input.type = 'search';
    input.placeholder = 'Search papers, notes, or sections…';
    input.setAttribute('aria-label', 'Search this site');
    input.autocomplete = 'off';
    input.spellcheck = false;
    const results = make('ul', 'search-results');
    const empty = make('p', 'search-empty', 'No matches yet. Try a topic or a title.');
    const footer = make('div', 'search-footer');
    const count = make('span', 'search-count');
    count.setAttribute('role', 'status');
    footer.append(make('span', '', '↑ ↓ to move · Enter to open · Esc to close'), count);
    dialog.append(head, input, results, empty, footer);
    document.body.append(dialog);

    function render() {
        const focusedHref = results.contains(document.activeElement) ? document.activeElement.href : null;
        const words = normalize(input.value.trim()).split(/\s+/).filter(Boolean);
        const matches = entries.filter(entry => words.every(word => entry.searchKey.includes(word)))
            .map((entry, order) => ({ entry, order, score: words.reduce((sum, word) => sum + (entry.titleKey.includes(word) ? 3 : 0), 0) }))
            .sort((a, b) => b.score - a.score || a.order - b.order);
        results.replaceChildren();
        matches.slice(0, 12).forEach(({ entry }) => {
            const item = make('li');
            const link = make('a', 'search-result');
            link.href = entry.href;
            if (entry.target) link.target = entry.target;
            if (entry.rel) link.rel = entry.rel;
            link.append(make('span', 'search-kind', entry.kind), make('span', 'search-result-title', entry.title));
            link.addEventListener('click', () => dialog.close());
            item.append(link);
            results.append(item);
        });
        empty.hidden = matches.length > 0;
        empty.textContent = indexLoading ? 'Loading the rest of the site…' : indexIncomplete
            ? 'No matches on this page. The full site index is temporarily unavailable.' : 'No matches yet. Try a topic or a title.';
        count.textContent = indexLoading ? 'Loading more entries…' : words.length
            ? `${matches.length} result${matches.length === 1 ? '' : 's'}` : 'Explore the site';
        if (focusedHref) {
            const previous = [...results.querySelectorAll('a')].find(link => link.href === focusedHref);
            (previous || input).focus({ preventScroll: true });
        }
    }
    function open() {
        if (dialog.open) return;
        input.value = '';
        render();
        document.body.dataset.searchOpen = 'true';
        dialog.showModal();
        input.focus();
    }
    trigger.addEventListener('click', open);
    close.addEventListener('click', () => dialog.close());
    dialog.addEventListener('close', () => {
        delete document.body.dataset.searchOpen;
        trigger.focus({ preventScroll: true });
    });
    dialog.addEventListener('click', event => {
        if (event.target !== dialog) return;
        const rect = dialog.getBoundingClientRect();
        if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) dialog.close();
    });
    input.addEventListener('input', render);
    dialog.addEventListener('keydown', event => {
        if (event.isComposing || event.keyCode === 229) return;
        const links = [...results.querySelectorAll('a')];
        if (!links.length) return;
        if (event.key === 'Enter' && event.target === input) {
            event.preventDefault();
            links[0].click();
        }
        if (event.key !== 'ArrowDown' && event.key !== 'ArrowUp') return;
        event.preventDefault();
        const current = links.indexOf(document.activeElement);
        const next = current < 0 ? (event.key === 'ArrowDown' ? 0 : links.length - 1)
            : (current + (event.key === 'ArrowDown' ? 1 : -1) + links.length) % links.length;
        links[next].focus();
    });
    document.addEventListener('keydown', event => {
        if (event.isComposing || event.keyCode === 229) return;
        if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
            event.preventDefault();
            if (dialog.open) dialog.close(); else open();
        }
    });

    // Both pages share the public index. Search terms stay in this browser.
    const otherPage = onToys ? homeUrl : toysUrl;
    fetch(otherPage.href, { credentials: 'omit' })
        .then(response => {
            if (!response.ok) throw new Error('Site index unavailable');
            return response.text();
        })
        .then(source => indexPage(new DOMParser().parseFromString(source, 'text/html'), otherPage))
        .catch(() => { indexIncomplete = true; })
        .finally(() => {
            indexLoading = false;
            if (dialog.open) render();
        });
})();

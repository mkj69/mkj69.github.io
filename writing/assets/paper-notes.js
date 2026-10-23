(() => {
    "use strict";

    const reader = document.querySelector("body.paper-notes-site [data-paper-reader]");
    if (!reader) return;

    const storageKey = "kaijing-paper-note-language-v2";
    const languages = new Set(["zh", "en"]);
    const controls = [...reader.querySelectorAll("button[data-paper-language]")];
    const versions = [...reader.querySelectorAll("[data-paper-language-content]")];
    const status = reader.querySelector(".reader-status");
    const dialog = document.getElementById("paper-image-dialog");
    let imageOpener = null;

    function rememberLanguage(language) {
        try { window.localStorage.setItem(storageKey, language); } catch {}
    }

    function setLanguage(requestedLanguage, remember = true) {
        const language = languages.has(requestedLanguage) ? requestedLanguage : "en";
        reader.dataset.language = language;
        document.documentElement.lang = language === "zh" ? "zh-CN" : "en";
        versions.forEach((element) => {
            element.hidden = element.dataset.paperLanguageContent !== language;
        });
        controls.forEach((button) => {
            button.setAttribute("aria-pressed", String(button.dataset.paperLanguage === language));
        });
        if (status) {
            status.textContent = language === "zh" ? "当前显示中文笔记。" : "The notes are in English.";
        }
        if (remember) rememberLanguage(language);
    }

    let initialLanguage = "en";
    try {
        const storedLanguage = window.localStorage.getItem(storageKey);
        if (languages.has(storedLanguage)) {
            initialLanguage = storedLanguage;
        } else if (storedLanguage !== null) {
            rememberLanguage("en");
        }
    } catch {}
    setLanguage(initialLanguage, false);

    controls.forEach((button) => {
        button.addEventListener("click", () => setLanguage(button.dataset.paperLanguage));
    });

    if (dialog) {
        const enlargedImage = dialog.querySelector("img");
        const closeButton = dialog.querySelector(".paper-dialog-close");

        reader.addEventListener("click", (event) => {
            if (!(event.target instanceof Element)) return;
            const button = event.target.closest(".figure-open");
            if (!button || !reader.contains(button) || !enlargedImage) return;
            const sourceImage = button.querySelector("img");
            if (!sourceImage || typeof dialog.showModal !== "function") return;
            enlargedImage.src = sourceImage.currentSrc || sourceImage.src;
            enlargedImage.alt = sourceImage.alt;
            imageOpener = button;
            if (!dialog.open) dialog.showModal();
        });

        if (closeButton) closeButton.addEventListener("click", () => dialog.close());
        dialog.addEventListener("click", (event) => {
            if (event.target !== dialog) return;
            const bounds = dialog.getBoundingClientRect();
            const outside = event.clientX < bounds.left || event.clientX > bounds.right
                || event.clientY < bounds.top || event.clientY > bounds.bottom;
            if (outside) dialog.close();
        });
        dialog.addEventListener("close", () => {
            const opener = imageOpener;
            imageOpener = null;
            if (opener && document.contains(opener) && !opener.closest("[hidden]")) {
                opener.focus();
            } else {
                const activeControl = controls.find((button) => button.getAttribute("aria-pressed") === "true");
                if (activeControl) activeControl.focus();
            }
        });
    }

    function revealHashTarget() {
        let id;
        try { id = decodeURIComponent(window.location.hash.slice(1)); } catch { return; }
        if (!id) return;
        const target = document.getElementById(id);
        if (!target || !reader.contains(target)) return;
        const version = target.closest("[data-paper-language-content]");
        if (version && languages.has(version.dataset.paperLanguageContent)) {
            setLanguage(version.dataset.paperLanguageContent);
        }
        window.requestAnimationFrame(() => {
            target.scrollIntoView({ block: "start", behavior: "auto" });
        });
    }

    window.addEventListener("hashchange", revealHashTarget);
    revealHashTarget();
})();

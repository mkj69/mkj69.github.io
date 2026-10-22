(() => {
    const reader = document.querySelector("#writing [data-paper-reader]");
    if (!reader) return;

    const storageKey = "kaijing-writing-note-language";
    const group = reader.closest(".writing-group-papers");
    const languages = new Set(["zh", "en", "both"]);
    const status = reader.querySelector(".paper-reader-status");
    const controls = [...reader.querySelectorAll("[data-paper-language]")];
    const dialog = reader.querySelector(".paper-image-dialog");
    let imageOpener = null;

    function setLanguage(language, remember = true) {
        if (!languages.has(language)) language = "zh";
        reader.dataset.language = language;
        group.querySelectorAll("[data-paper-ui-language]").forEach((label) => {
            label.hidden = language !== "both" && label.dataset.paperUiLanguage !== language;
        });
        reader.querySelectorAll("[data-paper-language-content]").forEach((panel) => {
            panel.hidden = language !== "both" && panel.dataset.paperLanguageContent !== language;
        });
        reader.querySelectorAll("[data-paper-summary-language]").forEach((label) => {
            label.hidden = language === "both" ? false : label.dataset.paperSummaryLanguage !== language;
        });
        controls.forEach((button) => {
            button.setAttribute("aria-pressed", String(button.dataset.paperLanguage === language));
        });
        if (remember) {
            try { window.localStorage.setItem(storageKey, language); } catch {}
        }
    }

    let initialLanguage = "zh";
    try { initialLanguage = window.localStorage.getItem(storageKey) || "zh"; } catch {}
    setLanguage(initialLanguage, false);

    controls.forEach((button) => button.addEventListener("click", () => {
        const language = button.dataset.paperLanguage;
        setLanguage(language);
        status.textContent = {
            zh: "当前显示中文笔记。",
            en: "The reading notes are in English.",
            both: "中文和英文笔记同时显示。"
        }[language];
    }));

    reader.addEventListener("click", (event) => {
        const button = event.target.closest(".figure-open");
        if (!button || !reader.contains(button) || !dialog) return;
        const sourceImage = button.querySelector("img");
        if (!sourceImage) return;
        const enlargedImage = dialog.querySelector("img");
        enlargedImage.src = sourceImage.currentSrc || sourceImage.src;
        enlargedImage.alt = sourceImage.alt;
        imageOpener = button;
        if (typeof dialog.showModal === "function") dialog.showModal();
    });

    if (dialog) {
        dialog.querySelector("button").addEventListener("click", () => dialog.close());
        dialog.addEventListener("click", (event) => {
            if (event.target === dialog) dialog.close();
        });
        dialog.addEventListener("close", () => {
            if (imageOpener && document.contains(imageOpener)) imageOpener.focus();
        });
    }

    function revealHashTarget() {
        let id;
        try { id = decodeURIComponent(window.location.hash.slice(1)); } catch { return; }
        const target = document.getElementById(id);
        const note = target && target.closest("#writing details[data-paper-note]");
        if (!note) return;
        const panel = target.closest("[data-paper-language-content]");
        if (panel && reader.dataset.language !== "both") setLanguage(panel.dataset.paperLanguageContent);
        note.open = true;
        window.setTimeout(() => {
            target.scrollIntoView({ block: "start", behavior: "auto" });
        }, 120);
    }

    window.addEventListener("hashchange", revealHashTarget);
    revealHashTarget();
})();

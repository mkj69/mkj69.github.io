(() => {
    const views = ["about", "education", "news", "publications", "experience"];
    const viewSet = new Set(views);
    const navigationLinks = [...document.querySelectorAll(".quick-nav a[href^='#']")];
    const wheelThreshold = 46;
    const transitionDuration = 620;

    let currentView = "about";
    let pendingDirection = null;
    let wheelDistance = 0;
    let wheelDirection = 0;
    let wheelResetTimer = 0;
    let transitionLocked = false;
    let transitionTimer = 0;

    function viewFromLocation() {
        const requestedView = window.location.hash.slice(1).toLowerCase();
        return viewSet.has(requestedView) ? requestedView : "about";
    }

    function directionBetween(fromView, toView) {
        return views.indexOf(toView) >= views.indexOf(fromView) ? "forward" : "backward";
    }

    function showCurrentView() {
        const nextView = viewFromLocation();
        const direction = pendingDirection || directionBetween(currentView, nextView);

        document.body.dataset.direction = direction;
        document.body.dataset.view = nextView;
        currentView = nextView;
        pendingDirection = null;

        navigationLinks.forEach((link) => {
            const isCurrent = link.getAttribute("href") === `#${currentView}`;
            link.classList.toggle("is-active", isCurrent);

            if (isCurrent) {
                link.setAttribute("aria-current", "page");
            } else {
                link.removeAttribute("aria-current");
            }
        });

        window.setTimeout(() => {
            window.scrollTo({ top: 0, left: 0, behavior: "auto" });
        }, 80);
    }

    function pageBoundaryReached(direction) {
        const maximumScroll = Math.max(0, document.documentElement.scrollHeight - window.innerHeight);

        if (maximumScroll <= 2) {
            return true;
        }

        return direction > 0
            ? window.scrollY >= maximumScroll - 2
            : window.scrollY <= 2;
    }

    function moveToAdjacentView(direction) {
        const currentIndex = views.indexOf(currentView);
        const nextIndex = currentIndex + direction;

        if (nextIndex < 0 || nextIndex >= views.length || transitionLocked) {
            return false;
        }

        transitionLocked = true;
        pendingDirection = direction > 0 ? "forward" : "backward";
        window.location.hash = views[nextIndex];

        window.clearTimeout(transitionTimer);
        transitionTimer = window.setTimeout(() => {
            transitionLocked = false;
        }, transitionDuration);

        return true;
    }

    function handleWheel(event) {
        if (event.ctrlKey || event.metaKey || Math.abs(event.deltaX) > Math.abs(event.deltaY)) {
            return;
        }

        const direction = Math.sign(event.deltaY);
        if (!direction || !pageBoundaryReached(direction)) {
            wheelDistance = 0;
            wheelDirection = 0;
            return;
        }

        const currentIndex = views.indexOf(currentView);
        const canMove = direction > 0 ? currentIndex < views.length - 1 : currentIndex > 0;
        if (!canMove) {
            return;
        }

        event.preventDefault();

        if (transitionLocked) {
            window.clearTimeout(transitionTimer);
            transitionTimer = window.setTimeout(() => {
                transitionLocked = false;
            }, 420);
            return;
        }

        if (wheelDirection !== direction) {
            wheelDistance = 0;
            wheelDirection = direction;
        }

        wheelDistance += Math.abs(event.deltaY);
        window.clearTimeout(wheelResetTimer);
        wheelResetTimer = window.setTimeout(() => {
            wheelDistance = 0;
            wheelDirection = 0;
        }, 180);

        if (wheelDistance >= wheelThreshold) {
            wheelDistance = 0;
            moveToAdjacentView(direction);
        }
    }

    navigationLinks.forEach((link) => {
        link.addEventListener("click", () => {
            const destination = link.getAttribute("href").slice(1);
            pendingDirection = directionBetween(currentView, destination);
        });
    });

    window.addEventListener("hashchange", showCurrentView);
    window.addEventListener("wheel", handleWheel, { passive: false });
    showCurrentView();
})();

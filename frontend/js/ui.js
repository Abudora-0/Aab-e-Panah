let activeActionButton = null;
let activeActionButtonWasDisabled = false;
let pendingActionFetches = 0;
let actionReleaseTimer = null;
let toastSequence = 0;


function showMessage(element, text, isError) {
    if (element) {
        element.textContent = text;
        element.className = text
            ? "message " + (isError ? "message-error" : "message-success")
            : "message";
    }
    if (!text) {
        return;
    }

    const region = document.getElementById("toast-region");
    const toast = document.createElement("div");
    const icon = makeIcon(isError ? "circle-alert" : "circle-check");
    const message = document.createElement("span");
    const toastId = "toast-" + toastSequence;
    toastSequence += 1;
    toast.className = "toast " + (isError ? "toast-error" : "toast-success");
    toast.id = toastId;
    toast.setAttribute("role", "status");
    toast.setAttribute("aria-live", "polite");
    message.textContent = text;
    toast.appendChild(icon);
    toast.appendChild(message);
    region.appendChild(toast);
    window.setTimeout(function () {
        toast.classList.add("toast-leaving");
        window.setTimeout(function () {
            toast.remove();
        }, 220);
    }, 4700);
    animateEntrance(region, ".toast:last-child");
}


function animateEntrance(container, selector) {
    if (!window.gsap || window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
        return;
    }
    const elements = container.querySelectorAll(selector);
    if (elements.length === 0) {
        return;
    }
    gsap.from(elements, {
        opacity: 0,
        y: 12,
        duration: 0.32,
        stagger: 0.06,
        ease: "power2.out",
    });
}


function showTableSkeleton(tableBody, rowCount, columnCount) {
    tableBody.textContent = "";
    for (let rowIndex = 0; rowIndex < rowCount; rowIndex += 1) {
        const row = document.createElement("tr");
        row.className = "skeleton-row";
        for (let columnIndex = 0; columnIndex < columnCount; columnIndex += 1) {
            const cell = document.createElement("td");
            const shimmer = document.createElement("span");
            shimmer.className = "skeleton-line";
            cell.appendChild(shimmer);
            row.appendChild(cell);
        }
        tableBody.appendChild(row);
    }
}


function updateMetric(element, value) {
    const currentValue = Number(element.textContent.replace(/,/g, "")) || 0;
    const targetValue = {value: currentValue};
    function renderValue() {
        element.textContent = Math.round(targetValue.value).toLocaleString();
    }
    if (window.gsap && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
        gsap.to(targetValue, {
            value: value,
            duration: 0.7,
            ease: "power2.out",
            onUpdate: renderValue,
        });
    } else {
        targetValue.value = value;
        renderValue();
    }
}

function updateOccupancyGauge(gauge, occupancy) {
    const currentValue = Number(gauge.dataset.fill) || 0;
    const fillValue = {value: currentValue};
    function renderFill() {
        gauge.style.setProperty("--occupancy-fill", fillValue.value + "%");
    }
    if (window.gsap && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
        gsap.to(fillValue, {
            value: occupancy,
            duration: 0.8,
            ease: "power2.out",
            onUpdate: renderFill,
        });
    } else {
        fillValue.value = occupancy;
        renderFill();
    }
    gauge.dataset.fill = String(occupancy);
}


function refreshOverview() {
    Promise.all([
        fetch("/api/camps"),
        fetch("/api/requests"),
    ]).then(function (responses) {
        return Promise.all([
            responses[0].json(),
            responses[1].json(),
        ]).then(function (data) {
            if (!responses[0].ok || !responses[1].ok) {
                throw new Error("Overview data request failed");
            }
            return data;
        });
    }).then(function (data) {
        const camps = data[0];
        const requests = data[1];
        let people = 0;
        let freePlaces = 0;
        let capacity = 0;
        for (const camp of camps) {
            people += Number(camp.current_occupancy);
            freePlaces += Number(camp.free_space);
            capacity += Number(camp.capacity);
        }
        const occupancy = capacity === 0 ? 0 : Math.round(people / capacity * 100);
        updateMetric(document.getElementById("overview-camps"), camps.length);
        updateMetric(document.getElementById("overview-people"), people);
        updateMetric(document.getElementById("overview-free"), freePlaces);
        updateMetric(
            document.getElementById("overview-waiting"),
            requests.waiting_count
        );
        document.getElementById("overview-occupancy").textContent = occupancy + "%";
        const gauge = document.getElementById("occupancy-gauge");
        updateOccupancyGauge(gauge, occupancy);
        gauge.setAttribute(
            "aria-label",
            occupancy + " percent occupancy"
        );
        document.getElementById("occupancy-summary").textContent =
            people.toLocaleString() + " people across "
            + camps.length + " active camps";
        updateCampTank(camps, document.getElementById("evacuee-camp").value);
    }).catch(function () {
        showMessage(
            document.getElementById("camp-sort-message"),
            "Could not refresh the field picture",
            true
        );
    });
}


function updateCampTank(camps, campId) {
    if (!camps || !campId) {
        return;
    }
    let selectedCamp = null;
    for (const camp of camps) {
        if (String(camp.camp_id) === String(campId)) {
            selectedCamp = camp;
            break;
        }
    }
    if (!selectedCamp) {
        return;
    }
    let percent = 0;
    if (selectedCamp.capacity !== 0) {
        percent = Math.round(
            selectedCamp.current_occupancy / selectedCamp.capacity * 100
        );
    }
    const tank = document.getElementById("camp-tank");
    tank.style.setProperty("--tank-fill", percent + "%");
    tank.setAttribute(
        "aria-label",
        selectedCamp.name + ": " + percent + " percent occupied"
    );
    document.getElementById("camp-tank-percent").textContent = percent + "%";
    document.getElementById("camp-tank-name").textContent = selectedCamp.name;
    document.getElementById("camp-tank-copy").textContent =
        selectedCamp.current_occupancy.toLocaleString() + " sheltered, "
        + selectedCamp.free_space.toLocaleString() + " free places";
}


function setActionButtonBusy(button, isBusy) {
    if (!button) {
        return;
    }
    if (isBusy) {
        if (!button.querySelector(".loading-spinner")) {
            const spinner = document.createElement("span");
            spinner.className = "loading-spinner";
            spinner.setAttribute("aria-hidden", "true");
            button.appendChild(spinner);
        }
        button.classList.add("is-loading");
        button.setAttribute("aria-busy", "true");
        button.disabled = true;
    } else {
        button.classList.remove("is-loading");
        button.removeAttribute("aria-busy");
        button.disabled = activeActionButtonWasDisabled;
        const spinner = button.querySelector(".loading-spinner");
        if (spinner) {
            spinner.remove();
        }
    }
}


function releaseActionButton() {
    if (pendingActionFetches !== 0 || !activeActionButton) {
        return;
    }
    window.clearTimeout(actionReleaseTimer);
    actionReleaseTimer = window.setTimeout(function () {
        if (pendingActionFetches === 0 && activeActionButton) {
            setActionButtonBusy(activeActionButton, false);
            activeActionButton = null;
        }
    }, 380);
}


function beginAction(button) {
    if (!button || button.disabled) {
        return;
    }
    if (activeActionButton && activeActionButton !== button) {
        setActionButtonBusy(activeActionButton, false);
    }
    window.clearTimeout(actionReleaseTimer);
    activeActionButton = button;
    activeActionButtonWasDisabled = button.disabled;
    pendingActionFetches = 0;
    setActionButtonBusy(button, true);
    actionReleaseTimer = window.setTimeout(releaseActionButton, 7000);
}


function actionButtonForEvent(event) {
    let button = event.target.closest("button");
    if (button && button.type === "submit" && button.closest("form")) {
        if (!button.form.checkValidity()) {
            return null;
        }
        return button;
    }
    if (button && [
        "sort-camps",
        "reset-camps",
        "serve-request",
        "undo-button",
        "audit-refresh",
    ].indexOf(button.id) !== -1) {
        return button;
    }
    return null;
}


function initializeButtonLoading() {
    document.addEventListener("click", function (event) {
        const button = actionButtonForEvent(event);
        if (button) {
            beginAction(button);
        }
    }, true);
    document.addEventListener("submit", function (event) {
        const button = event.target.querySelector('button[type="submit"]');
        if (button) {
            beginAction(button);
        }
    }, true);

    const originalFetch = window.fetch;
    window.fetch = function () {
        const tracksAction = Boolean(activeActionButton);
        if (tracksAction) {
            pendingActionFetches += 1;
            window.clearTimeout(actionReleaseTimer);
        }
        return originalFetch.apply(this, arguments).then(
            function (response) {
                if (tracksAction) {
                    pendingActionFetches -= 1;
                    releaseActionButton();
                }
                return response;
            },
            function (error) {
                if (tracksAction) {
                    pendingActionFetches -= 1;
                    releaseActionButton();
                }
                throw error;
            }
        );
    };
}


function initializeNumberSteppers() {
    const numberInputs = document.querySelectorAll('input[type="number"]');
    for (const input of numberInputs) {
        const wrapper = document.createElement("div");
        const decrease = document.createElement("button");
        const increase = document.createElement("button");
        const parent = input.parentNode;
        wrapper.className = "number-stepper";
        decrease.className = "stepper-button";
        decrease.type = "button";
        decrease.setAttribute("aria-label", "Decrease " + input.labels[0].textContent);
        decrease.appendChild(makeIcon("minus"));
        increase.className = "stepper-button";
        increase.type = "button";
        increase.setAttribute("aria-label", "Increase " + input.labels[0].textContent);
        increase.appendChild(makeIcon("plus"));
        parent.insertBefore(wrapper, input);
        wrapper.appendChild(decrease);
        wrapper.appendChild(input);
        wrapper.appendChild(increase);

        function changeValue(amount) {
            const currentValue = input.value === "" ? 0 : Number(input.value);
            const minimum = input.min === "" ? -Infinity : Number(input.min);
            const maximum = input.max === "" ? Infinity : Number(input.max);
            const nextValue = Math.min(maximum, Math.max(minimum, currentValue + amount));
            input.value = String(nextValue);
            input.dispatchEvent(new Event("input", {bubbles: true}));
            input.dispatchEvent(new Event("change", {bubbles: true}));
        }

        function startRepeating(button, amount) {
            let repeatTimer = null;
            button.addEventListener("click", function () {
                changeValue(amount);
            });
            button.addEventListener("pointerdown", function (event) {
                event.preventDefault();
                repeatTimer = window.setTimeout(function () {
                    repeatTimer = window.setInterval(function () {
                        changeValue(amount);
                    }, 90);
                }, 420);
            });
            function stopRepeating() {
                window.clearTimeout(repeatTimer);
                window.clearInterval(repeatTimer);
            }
            button.addEventListener("pointerup", stopRepeating);
            button.addEventListener("pointerleave", stopRepeating);
            button.addEventListener("pointercancel", stopRepeating);
        }

        startRepeating(decrease, -1);
        startRepeating(increase, 1);
    }
}


function initializeTheme() {
    const toggle = document.getElementById("night-toggle");
    let savedTheme = null;
    try {
        savedTheme = localStorage.getItem("aab-theme");
    } catch (error) {
        savedTheme = null;
    }
    const useNightTheme = savedTheme
        ? savedTheme === "night"
        : window.matchMedia("(prefers-color-scheme: dark)").matches;
    applyTheme(useNightTheme);
    toggle.addEventListener("click", function () {
        const isNight = document.documentElement.dataset.theme !== "night";
        applyTheme(isNight);
        try {
            localStorage.setItem("aab-theme", isNight ? "night" : "day");
        } catch (error) {
            toggle.setAttribute("aria-label", "Theme changed for this visit only");
        }
    });
}


function applyTheme(isNight) {
    const toggle = document.getElementById("night-toggle");
    document.documentElement.dataset.theme = isNight ? "night" : "day";
    toggle.setAttribute("aria-pressed", String(isNight));
    toggle.querySelector("span").textContent = isNight
        ? "Day operations"
        : "Night operations";
    toggle.replaceChild(makeIcon(isNight ? "sun" : "moon"), toggle.querySelector("svg"));
}


function initializeCampDialog() {
    const dialog = document.getElementById("camp-dialog");
    document.querySelectorAll("[data-open-camp-form]").forEach(function (button) {
        button.addEventListener("click", function () {
            dialog.showModal();
        });
    });
    document.querySelectorAll("[data-close-camp-form]").forEach(function (button) {
        button.addEventListener("click", function () {
            dialog.close();
        });
    });
    dialog.addEventListener("click", function (event) {
        if (event.target === dialog) {
            dialog.close();
        }
    });
}


function setViewToggle(buttonIds, panelIds, selectedIndex) {
    for (let index = 0; index < buttonIds.length; index += 1) {
        const button = document.getElementById(buttonIds[index]);
        const panel = document.getElementById(panelIds[index]);
        const selected = index === selectedIndex;
        button.classList.toggle("is-selected", selected);
        button.setAttribute("aria-pressed", String(selected));
        panel.hidden = !selected;
    }
}


function initializeViewToggles() {
    document.getElementById("camp-view-cards").addEventListener("click", function () {
        setViewToggle(
            ["camp-view-cards", "camp-view-table"],
            ["camp-cards", "camp-table-panel"],
            0
        );
    });
    document.getElementById("camp-view-table").addEventListener("click", function () {
        setViewToggle(
            ["camp-view-cards", "camp-view-table"],
            ["camp-cards", "camp-table-panel"],
            1
        );
    });
    document.getElementById("supply-view-nodes").addEventListener("click", function () {
        setViewToggle(
            ["supply-view-nodes", "supply-view-table"],
            ["supply-nodes", "supply-table-panel"],
            0
        );
    });
    document.getElementById("supply-view-table").addEventListener("click", function () {
        setViewToggle(
            ["supply-view-nodes", "supply-view-table"],
            ["supply-nodes", "supply-table-panel"],
            1
        );
    });
}


function initializeFieldValidation() {
    document.querySelectorAll(".field input").forEach(function (input) {
        input.addEventListener("blur", function () {
            input.closest(".field").classList.toggle("is-invalid", !input.validity.valid);
            input.closest(".field").classList.toggle("is-valid", input.validity.valid);
        });
        input.addEventListener("input", function () {
            if (input.closest(".field").classList.contains("is-invalid")) {
                input.closest(".field").classList.toggle("is-invalid", !input.validity.valid);
                input.closest(".field").classList.toggle("is-valid", input.validity.valid);
            }
        });
    });
}


function initializeScrollEffects() {
    const header = document.getElementById("site-header");
    const progress = document.getElementById("scroll-progress");
    const nav = document.querySelector(".depth-nav");
    const navLinks = document.querySelectorAll(".depth-nav a");
    const waterFill = document.querySelector(".depth-water");
    function updateScrollPosition() {
        const scrollable = document.documentElement.scrollHeight - window.innerHeight;
        const percent = scrollable <= 0 ? 0 : window.scrollY / scrollable * 100;
        progress.style.transform = "scaleX(" + percent / 100 + ")";
        if (window.innerWidth <= 850) {
            waterFill.style.width = percent + "%";
        } else {
            waterFill.style.height = percent + "%";
        }
        header.classList.toggle("is-compact", window.scrollY > 90);
    }
    window.addEventListener("scroll", updateScrollPosition, {passive: true});
    window.addEventListener("resize", updateScrollPosition);
    updateScrollPosition();

    if ("IntersectionObserver" in window) {
        const sectionObserver = new IntersectionObserver(function (entries) {
            for (const entry of entries) {
                if (!entry.isIntersecting) {
                    continue;
                }
                for (const link of navLinks) {
                    if (link.getAttribute("href") === "#" + entry.target.id) {
                        link.setAttribute("aria-current", "location");
                    } else {
                        link.removeAttribute("aria-current");
                    }
                }
            }
        }, {rootMargin: "-30% 0px -58% 0px"});
        for (const link of navLinks) {
            const section = document.querySelector(link.getAttribute("href"));
            if (section) {
                sectionObserver.observe(section);
            }
        }

        const waveObserver = new IntersectionObserver(function (entries) {
            for (const entry of entries) {
                if (window.gsap && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
                    if (entry.isIntersecting) {
                        gsap.to(".hero-wave-back", {
                            x: -18,
                            duration: 5,
                            repeat: -1,
                            yoyo: true,
                            ease: "sine.inOut",
                        });
                        gsap.to(".hero-wave-middle", {
                            x: 13,
                            duration: 5.5,
                            repeat: -1,
                            yoyo: true,
                            ease: "sine.inOut",
                        });
                        gsap.to(".hero-wave-front", {
                            x: 16,
                            duration: 6,
                            repeat: -1,
                            yoyo: true,
                            ease: "sine.inOut",
                        });
                        gsap.to(".status-beacon", {
                            scale: 1.28,
                            opacity: 0.72,
                            duration: 0.9,
                            repeat: -1,
                            yoyo: true,
                            ease: "sine.inOut",
                        });
                    } else {
                        gsap.killTweensOf(
                            ".hero-wave-back, .hero-wave-middle, .hero-wave-front, .status-beacon"
                        );
                    }
                }
            }
        });
        waveObserver.observe(header);

        if (window.gsap && window.ScrollTrigger
            && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
            gsap.registerPlugin(ScrollTrigger);
            document.querySelectorAll(".reveal-section").forEach(function (section) {
                gsap.from(section, {
                    opacity: 0,
                    y: 16,
                    duration: 0.55,
                    ease: "power2.out",
                    scrollTrigger: {
                        trigger: section,
                        start: "top 88%",
                        once: true,
                    },
                });
            });
        } else {
            document.querySelectorAll(".reveal-section").forEach(function (section) {
                section.classList.add("is-visible");
            });
        }
    } else {
        document.querySelectorAll(".reveal-section").forEach(function (section) {
            section.classList.add("is-visible");
        });
    }

    nav.addEventListener("click", function (event) {
        const link = event.target.closest("a");
        if (link) {
            const target = document.querySelector(link.getAttribute("href"));
            if (target) {
                event.preventDefault();
                target.scrollIntoView({behavior: "smooth", block: "start"});
            }
        }
    });
}


function initializeNumberInputs() {
    initializeNumberSteppers();
    initializeFieldValidation();
}


initializeTheme();
initializeCampDialog();
initializeViewToggles();
initializeNumberInputs();
initializeButtonLoading();
initializeScrollEffects();
refreshOverview();

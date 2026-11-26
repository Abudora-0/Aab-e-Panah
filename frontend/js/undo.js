const undoButton = document.getElementById("undo-button");
const undoMessage = document.getElementById("undo-message");
const undoList = document.getElementById("undo-list");


async function loadUndoHistory() {
    try {
        const response = await fetch("/api/undo/history");
        const data = await response.json();
        if (!response.ok) {
            showMessage(undoMessage, data.error, true);
            return;
        }
        undoList.textContent = "";
        for (let index = 0; index < data.history.length; index += 1) {
            const record = data.history[index];
            const card = document.createElement("article");
            const number = document.createElement("span");
            const copy = document.createElement("span");
            card.className = "undo-card";
            if (index === 0) {
                card.classList.add("is-top");
            }
            number.className = "undo-index";
            number.textContent = String(index + 1).padStart(2, "0");
            copy.className = "undo-copy";
            copy.textContent = record.action + " - " + record.details;
            card.appendChild(number);
            card.appendChild(copy);
            if (index === 0) {
                const top = document.createElement("span");
                top.className = "undo-top-badge";
                top.textContent = "TOP";
                card.appendChild(top);
            }
            undoList.appendChild(card);
        }
        if (data.history.length === 0) {
            const empty = document.createElement("p");
            empty.className = "empty-state";
            empty.textContent = "No reversible actions are waiting.";
            undoList.appendChild(empty);
        }
        animateEntrance(undoList, ".undo-card");
    } catch (error) {
        showMessage(undoMessage, "Could not load undo history", true);
    }
}


function animateTopCard() {
    const topCard = undoList.querySelector(".undo-card.is-top");
    if (!topCard || !window.gsap
        || window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
        return Promise.resolve();
    }
    return new Promise(function (resolve) {
        gsap.to(topCard, {
            y: -18,
            opacity: 0,
            duration: 0.22,
            ease: "power2.in",
            onComplete: resolve,
        });
    });
}


undoButton.addEventListener("click", async function () {
    try {
        const response = await fetch("/api/undo", {method: "POST"});
        const data = await response.json();
        showMessage(
            undoMessage,
            response.ok ? data.message : data.error,
            !response.ok
        );
        if (response.ok) {
            await animateTopCard();
            await loadUndoHistory();
            if (typeof loadCamps === "function") {
                await loadCamps();
            }
            if (typeof refreshCampSelect === "function") {
                await refreshCampSelect();
            }
            if (typeof refreshEvacueeCamp === "function") {
                await refreshEvacueeCamp();
            }
            if (typeof loadCampSupplies === "function") {
                await loadCampSupplies();
            }
            refreshOverview();
        }
    } catch (error) {
        showMessage(undoMessage, "Could not undo action", true);
    }
});


loadUndoHistory();

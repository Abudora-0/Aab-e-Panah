// This file handles undo.

const undoButton = document.getElementById("undo-button");
const undoMessage = document.getElementById("undo-message");
const undoList = document.getElementById("undo-list");

async function loadUndoHistory() {
    try {
        const response = await fetch("/api/undo/history");
        const data = await response.json();
        undoList.textContent = "";
        for (const record of data.history) {
            const item = document.createElement("li");
            item.textContent = record.action + " - " + record.details;
            undoList.appendChild(item);
        }
    } catch (error) {
        undoMessage.textContent = "Could not load undo history";
    }
}

undoButton.addEventListener("click", async function () {
    try {
        const response = await fetch("/api/undo", {method: "POST"});
        const data = await response.json();
        undoMessage.textContent = response.ok ? data.message : data.error;
        if (response.ok) {
            await loadUndoHistory();
            if (typeof loadCamps === "function") {
                await loadCamps();
            }
            if (typeof refreshCampSelect === "function") {
                await refreshCampSelect();
            }
            if (typeof loadCampSupplies === "function") {
                await loadCampSupplies();
            }
        }
    } catch (error) {
        undoMessage.textContent = "Could not undo action";
    }
});

loadUndoHistory();

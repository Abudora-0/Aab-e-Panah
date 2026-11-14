// This file handles camp supplies.

const supplyCamp = document.getElementById("supply-camp");
const supplyList = document.getElementById("supply-list");
const supplyMessage = document.getElementById("supply-message");
const addSupplyForm = document.getElementById("add-supply-form");
const issueSupplyForm = document.getElementById("issue-supply-form");

function addSupplyCell(row, value) {
    const cell = document.createElement("td");
    cell.textContent = value;
    row.appendChild(cell);
}

function showSupplies(supplies) {
    supplyList.textContent = "";
    for (const batch of supplies) {
        const row = document.createElement("tr");
        addSupplyCell(row, batch.batch_id);
        addSupplyCell(row, batch.item_name);
        addSupplyCell(row, batch.quantity);
        addSupplyCell(row, batch.expiry_days);
        supplyList.appendChild(row);
    }
}

async function loadCampSupplies() {
    if (!supplyCamp.value) {
        showSupplies([]);
        showMessage(supplyMessage, "No camps are available", true);
        return;
    }
    try {
        const response = await fetch(
            "/api/camps/" + supplyCamp.value + "/supplies"
        );
        const data = await response.json();
        if (!response.ok) {
            showSupplies([]);
            showMessage(supplyMessage, data.error, true);
            return;
        }
        showSupplies(data.supplies);
        showMessage(supplyMessage, "", false);
    } catch (error) {
        showMessage(supplyMessage, "Could not load supplies", true);
    }
}

async function refreshCampSelect() {
    try {
        await fillCampSelect(supplyCamp);
        await loadCampSupplies();
    } catch (error) {
        showMessage(supplyMessage, "Could not load camps", true);
    }
}

addSupplyForm.addEventListener("submit", async function (event) {
    event.preventDefault();
    const data = {
        item_name: document.getElementById("supply-item").value.trim(),
        quantity: Number(document.getElementById("supply-quantity").value),
        expiry_days: Number(document.getElementById("supply-expiry").value),
    };
    try {
        const response = await fetch(
            "/api/camps/" + supplyCamp.value + "/supplies",
            {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify(data),
            }
        );
        const result = await response.json();
        showMessage(supplyMessage, response.ok
            ? "Supply batch added"
            : result.error, !response.ok);
        if (response.ok) {
            addSupplyForm.reset();
            await loadCampSupplies();
            if (typeof loadUndoHistory === "function") {
                await loadUndoHistory();
            }
        }
    } catch (error) {
        showMessage(supplyMessage, "Could not add supply", true);
    }
});

issueSupplyForm.addEventListener("submit", async function (event) {
    event.preventDefault();
    const data = {
        item_name: document.getElementById("issue-item").value.trim(),
        amount: Number(document.getElementById("issue-amount").value),
    };
    try {
        const response = await fetch(
            "/api/camps/" + supplyCamp.value + "/supplies/issue",
            {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify(data),
            }
        );
        const result = await response.json();
        showMessage(supplyMessage, response.ok
            ? result.message
            : result.error, !response.ok);
        if (response.ok) {
            issueSupplyForm.reset();
            await loadCampSupplies();
            if (typeof loadUndoHistory === "function") {
                await loadUndoHistory();
            }
        }
    } catch (error) {
        showMessage(supplyMessage, "Could not issue supplies", true);
    }
});

supplyCamp.addEventListener("change", loadCampSupplies);
refreshCampSelect();

const supplyCamp = document.getElementById("supply-camp");
const supplyList = document.getElementById("supply-list");
const supplyNodes = document.getElementById("supply-nodes");
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
    supplyNodes.textContent = "";
    if (supplies.length === 0) {
        const empty = document.createElement("div");
        const title = document.createElement("h4");
        const copy = document.createElement("p");
        empty.className = "empty-state";
        title.textContent = "No supply batches at this camp";
        copy.textContent = "Add a batch to build the camp's expiry chain.";
        empty.appendChild(makeIcon("package-open"));
        empty.appendChild(title);
        empty.appendChild(copy);
        supplyNodes.appendChild(empty);
        return;
    }

    for (let index = 0; index < supplies.length; index += 1) {
        const batch = supplies[index];
        const row = document.createElement("tr");
        addSupplyCell(row, batch.batch_id);
        addSupplyCell(row, batch.item_name);
        addSupplyCell(row, batch.quantity);
        addSupplyCell(row, batch.expiry_days);
        supplyList.appendChild(row);

        const node = document.createElement("article");
        const item = document.createElement("h4");
        const quantity = document.createElement("p");
        const expiry = document.createElement("p");
        node.className = "supply-node";
        if (index === 0) {
            node.classList.add("is-head");
            const head = document.createElement("span");
            head.className = "node-head-label";
            head.textContent = "Issues first";
            node.appendChild(head);
        }
        item.textContent = batch.item_name;
        quantity.textContent = "Quantity " + Number(batch.quantity).toLocaleString();
        expiry.textContent = "Expires in " + batch.expiry_days + " days";
        node.appendChild(item);
        node.appendChild(quantity);
        node.appendChild(expiry);
        supplyNodes.appendChild(node);
    }
    const nullEnd = document.createElement("span");
    nullEnd.className = "supply-null";
    nullEnd.textContent = "NULL";
    supplyNodes.appendChild(nullEnd);
    animateEntrance(supplyNodes, ".supply-node");
}


async function loadCampSupplies() {
    if (!supplyCamp.value) {
        showSupplies([]);
        if (supplyCamp.options.length === 0) {
            showMessage(supplyMessage, "No camps are available", true);
        } else {
            showMessage(supplyMessage, "", false);
        }
        return;
    }
    showTableSkeleton(supplyList, 3, 4);
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
        if (supplyCamp.options.length === 0) {
            showMessage(supplyMessage, "No camps are available", true);
        } else {
            showMessage(supplyMessage, "", false);
        }
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
            refreshOverview();
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

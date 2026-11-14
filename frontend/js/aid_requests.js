// This file handles aid requests.

const requestForm = document.getElementById("request-form");
const requestMessage = document.getElementById("request-message");
const requestList = document.getElementById("request-list");
const rankedRequestList = document.getElementById("ranked-request-list");
const servedList = document.getElementById("served-list");
const serveButton = document.getElementById("serve-request");

function addCell(row, value) {
    const cell = document.createElement("td");
    cell.textContent = value;
    row.appendChild(cell);
}

function addStatusCell(row, status) {
    const cell = document.createElement("td");
    const chip = document.createElement("span");
    chip.textContent = status;
    chip.className = status === "SERVED"
        ? "chip chip-success"
        : "chip chip-warning";
    cell.appendChild(chip);
    row.appendChild(cell);
}

function showWaitingRequests(requests) {
    requestList.textContent = "";
    for (const aidRequest of requests) {
        const row = document.createElement("tr");
        addCell(row, aidRequest.position);
        addCell(row, aidRequest.area_name);
        addCell(row, aidRequest.needs);
        addCell(row, aidRequest.severity);
        addStatusCell(row, aidRequest.status);
        addCell(row, aidRequest.created_at);
        requestList.appendChild(row);
    }
}

function showRankedRequests(requests) {
    rankedRequestList.textContent = "";
    for (const aidRequest of requests) {
        const row = document.createElement("tr");
        addCell(row, aidRequest.rank);
        addCell(row, aidRequest.area_name);
        addCell(row, aidRequest.needs);
        addCell(row, aidRequest.severity);
        addStatusCell(row, aidRequest.status);
        rankedRequestList.appendChild(row);
    }
}

function showServedRequests(requests) {
    servedList.textContent = "";
    for (const aidRequest of requests) {
        const row = document.createElement("tr");
        addCell(row, aidRequest.area_name);
        addCell(row, aidRequest.needs);
        addCell(row, aidRequest.severity);
        addStatusCell(row, aidRequest.status);
        addCell(row, aidRequest.served_at);
        servedList.appendChild(row);
    }
}

async function loadRequests() {
    try {
        const waitingResponse = await fetch("/api/requests");
        const waitingData = await waitingResponse.json();
        const servedResponse = await fetch("/api/requests/served");
        const servedData = await servedResponse.json();
        const rankedResponse = await fetch("/api/requests/ranked");
        const rankedData = await rankedResponse.json();
        if (!waitingResponse.ok || !servedResponse.ok || !rankedResponse.ok) {
            showMessage(requestMessage, "Could not load requests", true);
            return;
        }
        showWaitingRequests(waitingData.requests);
        showServedRequests(servedData);
        showRankedRequests(rankedData.requests);
    } catch (error) {
        showMessage(requestMessage, "Could not load requests", true);
    }
}

requestForm.addEventListener("submit", async function (event) {
    event.preventDefault();
    const formData = new FormData(requestForm);
    const requestData = {
        area_name: formData.get("area_name").trim(),
        needs: formData.get("needs").trim(),
        severity: Number(formData.get("severity")),
    };
    try {
        const response = await fetch("/api/requests", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(requestData),
        });
        const data = await response.json();
        if (!response.ok) {
            showMessage(requestMessage, data.error, true);
            return;
        }
        showMessage(requestMessage, "Request added successfully", false);
        requestForm.reset();
        await loadRequests();
    } catch (error) {
        showMessage(requestMessage, "Could not add request", true);
    }
});

serveButton.addEventListener("click", async function () {
    try {
        const response = await fetch("/api/requests/serve-next", {method: "POST"});
        const data = await response.json();
        if (!response.ok) {
            showMessage(requestMessage, data.error, true);
            return;
        }
        showMessage(requestMessage, "Request served successfully", false);
        await loadRequests();
    } catch (error) {
        showMessage(requestMessage, "Could not serve request", true);
    }
});

loadRequests();

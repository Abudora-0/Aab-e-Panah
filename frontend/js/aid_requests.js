// This file handles aid requests.

const requestForm = document.getElementById("request-form");
const requestMessage = document.getElementById("request-message");
const requestList = document.getElementById("request-list");
const servedList = document.getElementById("served-list");
const serveButton = document.getElementById("serve-request");

function addCell(row, value) {
    const cell = document.createElement("td");
    cell.textContent = value;
    row.appendChild(cell);
}

function showWaitingRequests(requests) {
    requestList.textContent = "";

    for (const request of requests) {
        const row = document.createElement("tr");
        addCell(row, request.position);
        addCell(row, request.area_name);
        addCell(row, request.needs);
        addCell(row, request.severity);
        addCell(row, request.created_at);
        requestList.appendChild(row);
    }
}

function showServedRequests(requests) {
    servedList.textContent = "";

    for (const request of requests) {
        const row = document.createElement("tr");
        addCell(row, request.area_name);
        addCell(row, request.needs);
        addCell(row, request.severity);
        addCell(row, request.served_at);
        servedList.appendChild(row);
    }
}

async function loadRequests() {
    try {
        const waitingResponse = await fetch("/api/requests");
        const waitingData = await waitingResponse.json();
        const servedResponse = await fetch("/api/requests/served");
        const servedData = await servedResponse.json();

        if (!waitingResponse.ok || !servedResponse.ok) {
            requestMessage.textContent = "Could not load requests";
            return;
        }

        showWaitingRequests(waitingData.requests);
        showServedRequests(servedData);
    } catch (error) {
        requestMessage.textContent = "Could not load requests";
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
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(requestData),
        });
        const data = await response.json();

        if (!response.ok) {
            requestMessage.textContent = data.error;
            return;
        }

        requestMessage.textContent = "Request added successfully";
        requestForm.reset();
        await loadRequests();
    } catch (error) {
        requestMessage.textContent = "Could not add request";
    }
});

serveButton.addEventListener("click", async function () {
    try {
        const response = await fetch("/api/requests/serve-next", {
            method: "POST",
        });
        const data = await response.json();

        if (!response.ok) {
            requestMessage.textContent = data.error;
            return;
        }

        requestMessage.textContent = "Request served successfully";
        await loadRequests();
    } catch (error) {
        requestMessage.textContent = "Could not serve request";
    }
});

loadRequests();

const requestForm = document.getElementById("request-form");
const requestMessage = document.getElementById("request-message");
const requestList = document.getElementById("request-list");
const rankedRequestList = document.getElementById("ranked-request-list");
const servedList = document.getElementById("served-list");
const serveButton = document.getElementById("serve-request");
const requestLane = document.getElementById("request-lane");
const urgentBuckets = document.getElementById("urgent-buckets");
const servedTimeline = document.getElementById("served-timeline");


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


function addSeverityMeter(container, severity) {
    const meter = document.createElement("div");
    meter.className = "severity-meter";
    meter.setAttribute("aria-label", "Severity " + severity + " out of 5");
    for (let index = 1; index <= 5; index += 1) {
        const segment = document.createElement("span");
        if (index <= severity) {
            segment.classList.add("is-filled");
        }
        meter.appendChild(segment);
    }
    container.appendChild(meter);
}


function showWaitingRequests(requests) {
    requestList.textContent = "";
    requestLane.textContent = "";
    document.getElementById("waiting-empty").textContent = "";
    document.getElementById("waiting-empty").hidden = requests.length !== 0;
    document.getElementById("queue-count").textContent =
        requests.length + " in queue";

    if (requests.length === 0) {
        const empty = document.getElementById("waiting-empty");
        const title = document.createElement("h4");
        const copy = document.createElement("p");
        empty.appendChild(makeEmptyIllustration());
        title.textContent = "The dispatch lane is clear";
        copy.textContent = "New area requests will appear here in arrival order.";
        empty.appendChild(title);
        empty.appendChild(copy);
        return;
    }

    for (const aidRequest of requests) {
        const row = document.createElement("tr");
        addCell(row, aidRequest.position);
        addCell(row, aidRequest.area_name);
        addCell(row, aidRequest.needs);
        addCell(row, aidRequest.severity);
        addStatusCell(row, aidRequest.status);
        addCell(row, aidRequest.created_at);
        requestList.appendChild(row);

        const ticket = document.createElement("article");
        const position = document.createElement("span");
        const title = document.createElement("h4");
        const needs = document.createElement("p");
        ticket.className = "ticket-card severity-" + aidRequest.severity;
        if (Number(aidRequest.position) === 1) {
            ticket.classList.add("is-front");
            const next = document.createElement("span");
            next.className = "ticket-next";
            next.textContent = "NEXT";
            ticket.appendChild(next);
        }
        position.className = "ticket-position";
        position.textContent = "#" + aidRequest.position;
        title.textContent = aidRequest.area_name;
        needs.textContent = aidRequest.needs;
        ticket.appendChild(position);
        ticket.appendChild(title);
        ticket.appendChild(needs);
        addSeverityMeter(ticket, Number(aidRequest.severity));
        requestLane.appendChild(ticket);
    }
    animateEntrance(requestLane, ".ticket-card");
}


function showRankedRequests(requests) {
    rankedRequestList.textContent = "";
    urgentBuckets.textContent = "";
    for (let severity = 5; severity >= 1; severity -= 1) {
        const bucket = document.createElement("article");
        const heading = document.createElement("div");
        const level = document.createElement("span");
        const count = document.createElement("span");
        const matching = [];
        for (const aidRequest of requests) {
            if (Number(aidRequest.severity) === severity) {
                matching.push(aidRequest);
            }
        }
        bucket.className = "severity-bucket severity-" + severity;
        heading.className = "bucket-heading";
        level.className = "bucket-level";
        level.textContent = severity;
        count.textContent = matching.length + " calls";
        heading.appendChild(level);
        heading.appendChild(count);
        bucket.appendChild(heading);
        if (matching.length === 0) {
            const empty = document.createElement("p");
            empty.className = "empty-bucket";
            empty.textContent = "Bucket empty";
            bucket.appendChild(empty);
        }
        for (const aidRequest of matching) {
            const item = document.createElement("div");
            item.className = "bucket-ticket";
            item.textContent = aidRequest.area_name + ": " + aidRequest.needs;
            bucket.appendChild(item);
        }
        urgentBuckets.appendChild(bucket);
    }

    for (const aidRequest of requests) {
        const row = document.createElement("tr");
        addCell(row, aidRequest.rank);
        addCell(row, aidRequest.area_name);
        addCell(row, aidRequest.needs);
        addCell(row, aidRequest.severity);
        addStatusCell(row, aidRequest.status);
        rankedRequestList.appendChild(row);
    }
    animateEntrance(urgentBuckets, ".severity-bucket");
}


function showServedRequests(requests) {
    servedList.textContent = "";
    servedTimeline.textContent = "";
    for (const aidRequest of requests) {
        const row = document.createElement("tr");
        addCell(row, aidRequest.area_name);
        addCell(row, aidRequest.needs);
        addCell(row, aidRequest.severity);
        addStatusCell(row, aidRequest.status);
        addCell(row, aidRequest.served_at);
        servedList.appendChild(row);

        const event = document.createElement("article");
        const area = document.createElement("strong");
        const requestNeeds = document.createElement("span");
        const time = document.createElement("span");
        event.className = "served-event";
        area.textContent = aidRequest.area_name;
        requestNeeds.textContent = aidRequest.needs;
        time.textContent = aidRequest.served_at;
        event.appendChild(area);
        event.appendChild(requestNeeds);
        event.appendChild(time);
        servedTimeline.appendChild(event);
    }
}


async function loadRequests() {
    showTableSkeleton(requestList, 3, 6);
    showTableSkeleton(rankedRequestList, 3, 5);
    showTableSkeleton(servedList, 2, 5);
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
        refreshOverview();
    } catch (error) {
        showMessage(requestMessage, "Could not add request", true);
    }
});


function animateFrontTicket() {
    const front = requestLane.querySelector(".ticket-card.is-front");
    if (!front || !window.gsap
        || window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
        return Promise.resolve();
    }
    return new Promise(function (resolve) {
        gsap.to(front, {
            x: 34,
            opacity: 0,
            duration: 0.24,
            ease: "power2.in",
            onComplete: resolve,
        });
    });
}


serveButton.addEventListener("click", async function () {
    try {
        const response = await fetch("/api/requests/serve-next", {method: "POST"});
        const data = await response.json();
        if (!response.ok) {
            showMessage(requestMessage, data.error, true);
            return;
        }
        await animateFrontTicket();
        showMessage(requestMessage, "Request served successfully", false);
        await loadRequests();
        refreshOverview();
    } catch (error) {
        showMessage(requestMessage, "Could not serve request", true);
    }
});


loadRequests();

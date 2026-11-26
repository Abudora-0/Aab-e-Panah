const auditAction = document.getElementById("audit-action");
const auditList = document.getElementById("audit-list");
const auditMessage = document.getElementById("audit-message");
const auditResult = document.getElementById("audit-result");
const auditCount = document.getElementById("audit-count");
const auditFilterChips = document.getElementById("audit-filter-chips");

const auditActions = [
    "ADD_CAMP", "UPDATE_CAMP", "ADD_ROAD", "BLOCK_ROAD",
    "UNBLOCK_ROAD", "ADD_REQUEST", "SERVE_REQUEST", "UNDO_ACTION",
    "RUN_ROUTE", "SORT_CAMPS", "FIND_CAMP", "RANK_REQUESTS",
    "ADD_SUPPLY", "ISSUE_SUPPLIES", "REGISTER_ARRIVAL",
    "REGISTER_DEPARTURE", "SYSTEM_ERROR",
];


function fillAuditActions() {
    auditAction.textContent = "";
    const allOption = document.createElement("option");
    allOption.value = "all";
    allOption.textContent = "All actions";
    auditAction.appendChild(allOption);
    for (const action of auditActions) {
        const option = document.createElement("option");
        option.value = action;
        option.textContent = action;
        auditAction.appendChild(option);
    }
}


function updateAuditFilterChips() {
    auditFilterChips.textContent = "";
    const values = [
        auditResult.options[auditResult.selectedIndex].textContent,
        auditAction.options[auditAction.selectedIndex].textContent,
        auditCount.value + " entries",
    ];
    for (const value of values) {
        const chip = document.createElement("span");
        chip.className = "filter-chip";
        chip.appendChild(makeIcon("filter"));
        const text = document.createElement("span");
        text.textContent = value;
        chip.appendChild(text);
        auditFilterChips.appendChild(chip);
    }
}


function appendAuditDetails(row, details, index) {
    const cell = document.createElement("td");
    const button = document.createElement("button");
    const detailRow = document.createElement("tr");
    const detailCell = document.createElement("td");
    const detailText = document.createElement("span");
    const detailId = "audit-detail-" + index;
    button.className = "audit-detail-button";
    button.type = "button";
    button.textContent = "Show details";
    button.setAttribute("aria-expanded", "false");
    button.setAttribute("aria-controls", detailId);
    detailRow.className = "audit-detail-row";
    detailRow.hidden = true;
    detailCell.colSpan = 6;
    detailText.className = "audit-details-text";
    detailText.id = detailId;
    detailText.textContent = details || "No details recorded";
    detailCell.appendChild(detailText);
    detailRow.appendChild(detailCell);
    button.addEventListener("click", function () {
        const expanded = button.getAttribute("aria-expanded") === "true";
        button.setAttribute("aria-expanded", String(!expanded));
        detailRow.hidden = expanded;
        button.textContent = expanded ? "Show details" : "Hide details";
    });
    cell.appendChild(button);
    row.appendChild(cell);
    auditList.appendChild(detailRow);
}


function showAuditEntries(entries) {
    auditList.textContent = "";
    for (let index = 0; index < entries.length; index += 1) {
        const entry = entries[index];
        const row = document.createElement("tr");
        const values = [
            entry.time,
            entry.actor,
            entry.action,
            entry.target,
        ];
        if (entry.result === "FAILED") {
            row.classList.add("failed-row");
        }
        for (const value of values) {
            const cell = document.createElement("td");
            cell.textContent = value;
            row.appendChild(cell);
        }
        const resultCell = document.createElement("td");
        const badge = document.createElement("span");
        badge.className = entry.result === "FAILED"
            ? "result-badge result-failed"
            : "result-badge result-success";
        badge.appendChild(makeIcon(
            entry.result === "FAILED" ? "circle-x" : "circle-check"
        ));
        const resultText = document.createElement("span");
        resultText.textContent = entry.result;
        badge.appendChild(resultText);
        resultCell.appendChild(badge);
        row.appendChild(resultCell);
        auditList.appendChild(row);
        appendAuditDetails(row, entry.details, index);
    }
    animateEntrance(auditList, "tr:not(.audit-detail-row)");
}


async function loadAuditEntries() {
    const count = auditCount.value;
    const action = auditAction.value;
    const url = "/api/audit?count=" + count + "&result=" + auditResult.value
        + "&action=" + action;
    updateAuditFilterChips();
    showTableSkeleton(auditList, 3, 6);
    try {
        const response = await fetch(url);
        const data = await response.json();
        if (!response.ok) {
            showMessage(auditMessage, data.error, true);
            return;
        }
        showAuditEntries(data.entries);
        showMessage(auditMessage, data.entries.length === 0
            ? "No audit entries found"
            : "", false);
    } catch (error) {
        showMessage(auditMessage, "Could not load audit log", true);
    }
}


fillAuditActions();
document.getElementById("audit-refresh").addEventListener(
    "click",
    loadAuditEntries
);
auditResult.addEventListener("change", loadAuditEntries);
auditAction.addEventListener("change", loadAuditEntries);
auditCount.addEventListener("change", loadAuditEntries);
loadAuditEntries();

// This file handles the audit log.

const auditAction = document.getElementById("audit-action");
const auditList = document.getElementById("audit-list");
const auditMessage = document.getElementById("audit-message");

const auditActions = [
    "ADD_CAMP", "UPDATE_CAMP", "ADD_ROAD", "BLOCK_ROAD",
    "UNBLOCK_ROAD", "ADD_REQUEST", "SERVE_REQUEST", "UNDO_ACTION",
    "RUN_ROUTE", "SORT_CAMPS", "FIND_CAMP", "RANK_REQUESTS",
    "ADD_SUPPLY", "ISSUE_SUPPLIES", "REGISTER_ARRIVAL",
    "REGISTER_DEPARTURE", "SYSTEM_ERROR",
];

function fillAuditActions() {
    const allOption = document.createElement("option");
    allOption.value = "all";
    allOption.textContent = "All";
    auditAction.appendChild(allOption);
    for (const action of auditActions) {
        const option = document.createElement("option");
        option.value = action;
        option.textContent = action;
        auditAction.appendChild(option);
    }
}

async function loadAuditEntries() {
    const result = document.getElementById("audit-result").value;
    const count = document.getElementById("audit-count").value;
    const action = auditAction.value;
    const url = "/api/audit?count=" + count + "&result=" + result
        + "&action=" + action;
    try {
        const response = await fetch(url);
        const data = await response.json();
        auditList.textContent = "";
        if (!response.ok) {
            auditMessage.textContent = data.error;
            return;
        }
        for (const entry of data.entries) {
            const row = document.createElement("tr");
            if (entry.result === "FAILED") {
                row.classList.add("failed-row");
            }
            const values = [
                entry.time,
                entry.actor,
                entry.action,
                entry.target,
                entry.result,
                entry.details,
            ];
            for (const value of values) {
                const cell = document.createElement("td");
                cell.textContent = value;
                row.appendChild(cell);
            }
            auditList.appendChild(row);
        }
        auditMessage.textContent = data.entries.length === 0
            ? "No audit entries found"
            : "";
    } catch (error) {
        auditMessage.textContent = "Could not load audit log";
    }
}

fillAuditActions();
document.getElementById("audit-refresh").addEventListener(
    "click",
    loadAuditEntries
);
loadAuditEntries();

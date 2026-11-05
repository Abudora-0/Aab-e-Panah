// This file handles camps.

const campForm = document.getElementById("camp-form");
const campMessage = document.getElementById("message");
const campList = document.getElementById("camp-list");
const statusLine = document.getElementById("status");
const sortButton = document.getElementById("sort-camps");
const resetButton = document.getElementById("reset-camps");
const sortMessage = document.getElementById("camp-sort-message");
const freeSpaceForm = document.getElementById("free-space-form");
const campNameSearchForm = document.getElementById("camp-name-search-form");
const findMessage = document.getElementById("camp-find-message");

async function updateHealth() {
    try {
        const response = await fetch("/api/health");
        const data = await response.json();
        if (response.ok && data.database_connected) {
            statusLine.textContent = "Database connected";
        } else {
            statusLine.textContent = "Database not connected";
        }
    } catch (error) {
        statusLine.textContent = "Database not connected";
    }
}

function showCamps(camps) {
    campList.textContent = "";
    for (const camp of camps) {
        const row = document.createElement("tr");
        const fields = [
            camp.name,
            camp.district,
            camp.capacity,
            camp.current_occupancy,
            camp.free_space,
        ];
        for (const field of fields) {
            const cell = document.createElement("td");
            cell.textContent = field;
            row.appendChild(cell);
        }
        campList.appendChild(row);
    }
}

async function loadCamps() {
    try {
        const response = await fetch("/api/camps");
        const data = await response.json();
        if (!response.ok) {
            campMessage.textContent = data.error;
            return;
        }
        showCamps(data);
    } catch (error) {
        campMessage.textContent = "Could not load camps";
    }
}

campForm.addEventListener("submit", async function (event) {
    event.preventDefault();
    const formData = new FormData(campForm);
    const camp = {
        name: formData.get("name").trim(),
        district: formData.get("district").trim(),
        capacity: Number(formData.get("capacity")),
    };
    try {
        const response = await fetch("/api/camps", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(camp),
        });
        const data = await response.json();
        if (!response.ok) {
            campMessage.textContent = data.error;
            return;
        }
        campMessage.textContent = "Camp added successfully";
        campForm.reset();
        await loadCamps();
        if (typeof refreshCampSelect === "function") {
            await refreshCampSelect();
        }
        if (typeof loadUndoHistory === "function") {
            await loadUndoHistory();
        }
    } catch (error) {
        campMessage.textContent = "Could not add camp";
    }
});

sortButton.addEventListener("click", async function () {
    const sort = document.getElementById("camp-sort").value;
    const order = document.getElementById("camp-order").value;
    const algorithm = document.getElementById("camp-algorithm").value;
    try {
        const response = await fetch(
            "/api/camps/sorted?sort=" + sort + "&order=" + order
            + "&algorithm=" + algorithm
        );
        const data = await response.json();
        if (!response.ok) {
            sortMessage.textContent = data.error;
            return;
        }
        showCamps(data.camps);
        sortMessage.textContent = "Sorted by " + sort + " with "
            + algorithm + " sort in " + data.milliseconds.toFixed(2) + " ms";
    } catch (error) {
        sortMessage.textContent = "Could not sort camps";
    }
});

resetButton.addEventListener("click", async function () {
    sortMessage.textContent = "";
    await loadCamps();
});

async function findCamp(url) {
    try {
        const response = await fetch(url);
        const data = await response.json();
        if (!response.ok) {
            findMessage.textContent = data.error;
            return;
        }
        findMessage.textContent = data.name + " has " + data.free_space
            + " free places";
    } catch (error) {
        findMessage.textContent = "Could not find camp";
    }
}

freeSpaceForm.addEventListener("submit", function (event) {
    event.preventDefault();
    const value = document.getElementById("minimum-free-space").value;
    findCamp("/api/camps/find?free_space=" + encodeURIComponent(value));
});

campNameSearchForm.addEventListener("submit", function (event) {
    event.preventDefault();
    const value = document.getElementById("camp-name-search").value.trim();
    findCamp("/api/camps/find?name=" + encodeURIComponent(value));
});

updateHealth();
loadCamps();

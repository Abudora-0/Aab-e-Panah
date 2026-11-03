// This file handles the camp form.

const campForm = document.getElementById("camp-form");
const campMessage = document.getElementById("message");
const campList = document.getElementById("camp-list");
const statusLine = document.getElementById("status");

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
        const nameCell = document.createElement("td");
        const districtCell = document.createElement("td");
        const capacityCell = document.createElement("td");
        const occupancyCell = document.createElement("td");

        nameCell.textContent = camp.name;
        districtCell.textContent = camp.district;
        capacityCell.textContent = camp.capacity;
        occupancyCell.textContent = camp.current_occupancy;

        row.appendChild(nameCell);
        row.appendChild(districtCell);
        row.appendChild(capacityCell);
        row.appendChild(occupancyCell);
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
            headers: {
                "Content-Type": "application/json",
            },
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
    } catch (error) {
        campMessage.textContent = "Could not add camp";
    }
});

updateHealth();
loadCamps();

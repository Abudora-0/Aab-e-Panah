// This file handles the dummy camp form.

const statusLine = document.getElementById("status");
const campForm = document.getElementById("camp-form");
const messageLine = document.getElementById("message");
const campList = document.getElementById("camp-list");

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
    campList.innerHTML = "";

    for (const camp of camps) {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${camp.name}</td>
            <td>${camp.district}</td>
            <td>${camp.capacity}</td>
            <td>${camp.current_occupancy}</td>
        `;
        campList.appendChild(row);
    }
}

async function loadCamps() {
    try {
        const response = await fetch("/api/camps");
        const data = await response.json();

        if (!response.ok) {
            messageLine.textContent = data.error;
            return;
        }

        showCamps(data);
    } catch (error) {
        messageLine.textContent = "Could not load camps";
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
            messageLine.textContent = data.error;
            return;
        }

        messageLine.textContent = "Camp added successfully";
        campForm.reset();
        await loadCamps();
    } catch (error) {
        messageLine.textContent = "Could not add camp";
    }
});

updateHealth();
loadCamps();

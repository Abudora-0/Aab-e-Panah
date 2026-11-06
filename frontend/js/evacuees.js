// This file handles arrivals and departures.

const evacueeCamp = document.getElementById("evacuee-camp");
const evacueeMessage = document.getElementById("evacuee-message");

async function refreshEvacueeCamp() {
    try {
        await fillCampSelect(evacueeCamp);
    } catch (error) {
        evacueeMessage.textContent = "Could not load camps";
    }
}

async function changeOccupancy(path, inputId) {
    const people = Number(document.getElementById(inputId).value);
    try {
        const response = await fetch(
            "/api/camps/" + evacueeCamp.value + "/" + path,
            {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({people: people}),
            }
        );
        const data = await response.json();
        evacueeMessage.textContent = response.ok ? data.message : data.error;
        if (response.ok) {
            document.getElementById(inputId).value = "";
            await loadCamps();
            await refreshEvacueeCamp();
            await refreshCampSelect();
            if (typeof loadAuditEntries === "function") {
                await loadAuditEntries();
            }
        }
    } catch (error) {
        evacueeMessage.textContent = "Could not update occupancy";
    }
}

document.getElementById("arrival-form").addEventListener(
    "submit",
    function (event) {
        event.preventDefault();
        changeOccupancy("arrivals", "arrival-people");
    }
);

document.getElementById("departure-form").addEventListener(
    "submit",
    function (event) {
        event.preventDefault();
        changeOccupancy("departures", "departure-people");
    }
);

refreshEvacueeCamp();

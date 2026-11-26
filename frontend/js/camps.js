const campForm = document.getElementById("camp-form");
const campMessage = document.getElementById("message");
const campList = document.getElementById("camp-list");
const campCards = document.getElementById("camp-cards");
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
        const connected = response.ok && data.database_connected;
        statusLine.classList.toggle("is-disconnected", !connected);
        statusLine.querySelector("span:last-child").textContent = connected
            ? "Database connected"
            : "Database not connected";
    } catch (error) {
        statusLine.classList.add("is-disconnected");
        statusLine.querySelector("span:last-child").textContent =
            "Database not connected";
    }
}


function showCamps(camps) {
    campList.textContent = "";
    campCards.textContent = "";
    if (camps.length === 0) {
        const empty = document.createElement("div");
        const title = document.createElement("h4");
        const copy = document.createElement("p");
        empty.className = "empty-state";
        empty.appendChild(makeEmptyIllustration());
        title.textContent = "No camps on the map yet";
        copy.textContent = "Register a relief camp to begin tracking capacity.";
        empty.appendChild(title);
        empty.appendChild(copy);
        campCards.appendChild(empty);
        return;
    }

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

        let percent = 0;
        if (camp.capacity !== 0) {
            percent = Math.round(camp.current_occupancy / camp.capacity * 100);
        }
        const card = document.createElement("article");
        const top = document.createElement("div");
        const title = document.createElement("h3");
        const district = document.createElement("p");
        const level = document.createElement("div");
        const percentText = document.createElement("span");
        const stats = document.createElement("div");
        const occupied = document.createElement("span");
        const free = document.createElement("span");
        let levelIcon = "waves";
        let levelText = "Room available";
        if (percent >= 70) {
            levelText = "High waterline";
        }
        if (percent > 90) {
            levelIcon = "triangle-alert";
            levelText = "Critical waterline";
        }
        card.className = "camp-card";
        if (percent > 90) {
            card.classList.add("level-critical");
        } else if (percent >= 70) {
            card.classList.add("level-watch");
        }
        card.style.setProperty("--water-level", "0");
        top.className = "camp-card-top";
        title.textContent = camp.name;
        district.className = "camp-district";
        district.textContent = camp.district;
        level.className = "camp-level";
        level.appendChild(makeIcon(levelIcon));
        const levelLabel = document.createElement("span");
        levelLabel.textContent = levelText;
        level.appendChild(levelLabel);
        percentText.className = "camp-percent";
        percentText.textContent = percent + "%";
        top.appendChild(title);
        top.appendChild(percentText);
        stats.className = "camp-stats";
        occupied.textContent = "Sheltered ";
        const occupiedValue = document.createElement("strong");
        occupiedValue.textContent = Number(camp.current_occupancy).toLocaleString();
        occupied.appendChild(occupiedValue);
        free.textContent = "Free ";
        const freeValue = document.createElement("strong");
        freeValue.textContent = Number(camp.free_space).toLocaleString();
        free.appendChild(freeValue);
        stats.appendChild(occupied);
        stats.appendChild(free);
        card.appendChild(top);
        card.appendChild(district);
        card.appendChild(level);
        card.appendChild(stats);
        campCards.appendChild(card);
        window.requestAnimationFrame(function () {
            card.style.setProperty("--water-level", String(percent / 100));
        });
    }
    animateEntrance(campCards, ".camp-card");
}


async function loadCamps() {
    showTableSkeleton(campList, 3, 5);
    try {
        const response = await fetch("/api/camps");
        const data = await response.json();
        if (!response.ok) {
            showMessage(campMessage, data.error, true);
            return;
        }
        showCamps(data);
    } catch (error) {
        showMessage(campMessage, "Could not load camps", true);
    }
}


async function fillCampSelect(selectElement) {
    const oldValue = selectElement.value;
    const response = await fetch("/api/camps");
    const camps = await response.json();
    if (!response.ok) {
        throw new Error(camps.error || "Could not load camps");
    }
    selectElement.textContent = "";
    for (const camp of camps) {
        const option = document.createElement("option");
        option.value = camp.camp_id;
        option.textContent = camp.name;
        selectElement.appendChild(option);
    }
    if (camps.length === 0) {
        return;
    }
    selectElement.value = oldValue;
    if (selectElement.value !== oldValue) {
        selectElement.value = camps[0].camp_id;
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
            showMessage(campMessage, data.error, true);
            return;
        }
        showMessage(campMessage, "Camp added successfully", false);
        campForm.reset();
        document.getElementById("camp-dialog").close();
        await loadCamps();
        if (typeof refreshCampSelect === "function") {
            await refreshCampSelect();
        }
        if (typeof refreshEvacueeCamp === "function") {
            await refreshEvacueeCamp();
        }
        if (typeof loadUndoHistory === "function") {
            await loadUndoHistory();
        }
        refreshOverview();
    } catch (error) {
        showMessage(campMessage, "Could not add camp", true);
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
            showMessage(sortMessage, data.error, true);
            return;
        }
        showCamps(data.camps);
        showMessage(sortMessage, "Sorted by " + sort + " with "
            + algorithm + " sort in " + data.milliseconds.toFixed(2) + " ms", false);
    } catch (error) {
        showMessage(sortMessage, "Could not sort camps", true);
    }
});


resetButton.addEventListener("click", async function () {
    showMessage(sortMessage, "", false);
    await loadCamps();
});


async function findCamp(url) {
    try {
        const response = await fetch(url);
        const data = await response.json();
        if (!response.ok) {
            showMessage(findMessage, data.error, true);
            return;
        }
        showMessage(findMessage, data.name + " has " + data.free_space
            + " free places", false);
    } catch (error) {
        showMessage(findMessage, "Could not find camp", true);
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

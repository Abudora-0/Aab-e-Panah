function selectLabel(selectElement) {
    const label = document.querySelector('label[for="' + selectElement.id + '"]');
    if (label) {
        return label.textContent.trim();
    }
    return "Choose an option";
}


function createCustomSelect(selectElement) {
    if (selectElement.dataset.customized === "true") {
        return;
    }

    selectElement.dataset.customized = "true";
    selectElement.classList.add("native-select-source");
    selectElement.setAttribute("aria-hidden", "true");
    selectElement.tabIndex = -1;

    const wrapper = document.createElement("div");
    const button = document.createElement("button");
    const label = document.createElement("span");
    const chevron = makeIcon("chevron-down");
    const listbox = document.createElement("div");
    const listboxId = selectElement.id + "-listbox";
    const parent = selectElement.parentNode;
    wrapper.className = "custom-select";
    button.className = "select-trigger";
    button.type = "button";
    button.setAttribute("role", "combobox");
    button.setAttribute("aria-haspopup", "listbox");
    button.setAttribute("aria-expanded", "false");
    button.setAttribute("aria-controls", listboxId);
    button.setAttribute("aria-label", selectLabel(selectElement));
    label.className = "select-value";
    listbox.id = listboxId;
    listbox.className = "select-listbox";
    listbox.setAttribute("role", "listbox");
    listbox.setAttribute("aria-label", selectLabel(selectElement));
    listbox.hidden = true;
    button.appendChild(label);
    button.appendChild(chevron);
    parent.insertBefore(wrapper, selectElement);
    wrapper.appendChild(selectElement);
    wrapper.appendChild(button);
    wrapper.appendChild(listbox);

    function optionButtons() {
        return listbox.querySelectorAll('[role="option"]:not([aria-disabled="true"])');
    }

    function closeList() {
        listbox.hidden = true;
        button.setAttribute("aria-expanded", "false");
        wrapper.classList.remove("is-open");
    }

    function openList() {
        if (selectElement.disabled) {
            return;
        }
        listbox.hidden = false;
        button.setAttribute("aria-expanded", "true");
        wrapper.classList.add("is-open");
        const options = optionButtons();
        let currentIndex = selectElement.selectedIndex;
        if (currentIndex < 0 || currentIndex >= options.length) {
            currentIndex = 0;
        }
        if (options.length > 0) {
            options[currentIndex].focus();
        }
    }

    function updateDisplay() {
        const selectedOption = selectElement.options[selectElement.selectedIndex];
        label.textContent = selectedOption ? selectedOption.textContent : "Select a camp";
        button.disabled = selectElement.disabled;
        listbox.textContent = "";
        if (selectElement.options.length === 0) {
            const emptyOption = document.createElement("div");
            emptyOption.className = "select-empty";
            emptyOption.setAttribute("role", "option");
            emptyOption.setAttribute("aria-disabled", "true");
            emptyOption.textContent = "No options available";
            listbox.appendChild(emptyOption);
            return;
        }

        for (let index = 0; index < selectElement.options.length; index += 1) {
            const sourceOption = selectElement.options[index];
            const option = document.createElement("button");
            const optionText = document.createElement("span");
            option.type = "button";
            option.className = "select-option";
            option.setAttribute("role", "option");
            option.setAttribute("aria-selected", String(index === selectElement.selectedIndex));
            option.dataset.index = String(index);
            optionText.textContent = sourceOption.textContent;
            option.appendChild(optionText);
            if (index === selectElement.selectedIndex) {
                option.appendChild(makeIcon("check"));
            }
            listbox.appendChild(option);
        }
    }

    function chooseOption(index) {
        if (index < 0 || index >= selectElement.options.length) {
            return;
        }
        selectElement.selectedIndex = index;
        selectElement.dispatchEvent(new Event("change", {bubbles: true}));
        updateDisplay();
        closeList();
        button.focus();
    }

    function jumpToMatch(key) {
        const searchText = (button.dataset.searchText || "") + key.toLowerCase();
        button.dataset.searchText = searchText;
        window.clearTimeout(button.searchTimer);
        button.searchTimer = window.setTimeout(function () {
            button.dataset.searchText = "";
        }, 700);
        for (let index = 0; index < selectElement.options.length; index += 1) {
            if (selectElement.options[index].textContent.toLowerCase().indexOf(searchText) === 0) {
                chooseOption(index);
                break;
            }
        }
    }

    button.addEventListener("click", function () {
        if (listbox.hidden) {
            openList();
        } else {
            closeList();
        }
    });

    button.addEventListener("keydown", function (event) {
        const options = optionButtons();
        if (event.key === "ArrowDown" || event.key === "ArrowUp") {
            event.preventDefault();
            if (listbox.hidden) {
                openList();
            } else if (options.length > 0) {
                const current = Array.prototype.indexOf.call(options, document.activeElement);
                let next = current + (event.key === "ArrowDown" ? 1 : -1);
                if (next < 0) {
                    next = options.length - 1;
                }
                if (next >= options.length) {
                    next = 0;
                }
                options[next].focus();
            }
        } else if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            if (listbox.hidden) {
                openList();
            }
        } else if (event.key === "Escape") {
            closeList();
        } else if (event.key === "Home" || event.key === "End") {
            event.preventDefault();
            openList();
            const currentOptions = optionButtons();
            if (currentOptions.length > 0) {
                currentOptions[event.key === "Home" ? 0 : currentOptions.length - 1].focus();
            }
        } else if (event.key.length === 1 && !event.ctrlKey && !event.altKey) {
            jumpToMatch(event.key);
        }
    });

    listbox.addEventListener("keydown", function (event) {
        const options = optionButtons();
        const current = Array.prototype.indexOf.call(options, document.activeElement);
        if (event.key === "ArrowDown" || event.key === "ArrowUp") {
            event.preventDefault();
            let next = current + (event.key === "ArrowDown" ? 1 : -1);
            if (next < 0) {
                next = options.length - 1;
            }
            if (next >= options.length) {
                next = 0;
            }
            if (options.length > 0) {
                options[next].focus();
            }
        } else if (event.key === "Home" || event.key === "End") {
            event.preventDefault();
            if (options.length > 0) {
                options[event.key === "Home" ? 0 : options.length - 1].focus();
            }
        } else if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            if (current >= 0) {
                chooseOption(Number(options[current].dataset.index));
            }
        } else if (event.key === "Escape") {
            event.preventDefault();
            closeList();
            button.focus();
        } else if (event.key.length === 1 && !event.ctrlKey && !event.altKey) {
            event.preventDefault();
            jumpToMatch(event.key);
        }
    });

    listbox.addEventListener("click", function (event) {
        const option = event.target.closest('[role="option"]');
        if (option && option.dataset.index) {
            chooseOption(Number(option.dataset.index));
        }
    });

    selectElement.addEventListener("change", updateDisplay);
    const observer = new MutationObserver(updateDisplay);
    observer.observe(selectElement, {childList: true, subtree: true});
    document.addEventListener("pointerdown", function (event) {
        if (!wrapper.contains(event.target)) {
            closeList();
        }
    });
    updateDisplay();
}


function initializeCustomSelects() {
    const selects = document.querySelectorAll("select");
    for (const selectElement of selects) {
        createCustomSelect(selectElement);
    }
}


initializeCustomSelects();

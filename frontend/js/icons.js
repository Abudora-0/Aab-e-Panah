function makeIcon(name, label) {
    const namespace = "http://www.w3.org/2000/svg";
    const icon = document.createElementNS(namespace, "svg");
    const use = document.createElementNS(namespace, "use");
    icon.setAttribute("class", "icon");
    use.setAttribute("href", "/static/vendor/lucide/sprite.svg#" + name);
    icon.appendChild(use);
    if (label) {
        icon.setAttribute("role", "img");
        icon.setAttribute("aria-label", label);
    } else {
        icon.setAttribute("aria-hidden", "true");
    }
    return icon;
}


function makeEmptyIllustration() {
    const namespace = "http://www.w3.org/2000/svg";
    const illustration = document.createElementNS(namespace, "svg");
    const hull = document.createElementNS(namespace, "path");
    const water = document.createElementNS(namespace, "path");
    const sail = document.createElementNS(namespace, "path");
    illustration.setAttribute("viewBox", "0 0 180 100");
    illustration.setAttribute("class", "empty-boat");
    illustration.setAttribute("role", "img");
    illustration.setAttribute("aria-label", "An empty relief boat on calm water");
    hull.setAttribute("d", "M34 61h111l-15 17H52z");
    water.setAttribute("d", "M18 84c15-7 26 7 41 0s27 7 42 0 27 7 43 0 23 5 31 1");
    sail.setAttribute("d", "M89 23v37H60z");
    illustration.appendChild(hull);
    illustration.appendChild(water);
    illustration.appendChild(sail);
    return illustration;
}

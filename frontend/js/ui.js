function showMessage(element, text, isError) {
    element.textContent = text;
    element.className = text
        ? "message " + (isError ? "message-error" : "message-success")
        : "message";
}

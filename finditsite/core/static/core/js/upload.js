document.querySelector(".upload-form").addEventListener("submit", (event) => {
    const button = event.currentTarget.querySelector("button[type=submit]");
    button.disabled = true;
    button.textContent = button.dataset.loadingLabel;
});

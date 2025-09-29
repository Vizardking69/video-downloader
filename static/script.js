document.addEventListener("DOMContentLoaded", function () {
    const checkbox = document.getElementById("agree");
    const button = document.querySelector("button[type='submit']");

    // Disable button initially
    button.disabled = true;
    button.style.opacity = 0.6;

    // Enable button only when checkbox is checked
    checkbox.addEventListener("change", function () {
        if (checkbox.checked) {
            button.disabled = false;
            button.style.opacity = 1;
        } else {
            button.disabled = true;
            button.style.opacity = 0.6;
        }
    });
});

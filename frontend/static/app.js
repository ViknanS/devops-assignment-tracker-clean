document.addEventListener("DOMContentLoaded", () => {
    const deleteForms = document.querySelectorAll(".delete-form");
    deleteForms.forEach((form) => {
        form.addEventListener("submit", (event) => {
            const confirmed = window.confirm("Are you sure you want to delete this assignment?");
            if (!confirmed) {
                event.preventDefault();
            }
        });
    });
});

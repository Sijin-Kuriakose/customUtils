document.addEventListener("DOMContentLoaded", function() {
    // Select all accordion items
    const accordions = document.querySelectorAll(".accordion");

    // Loop through each accordion
    accordions.forEach(function(accordion) {
        accordion.addEventListener("click", function() {
            // Toggle the active class to show or hide the content
            this.classList.toggle("active");

            // Toggle the display of the next element (accordion content)
            const panel = this.nextElementSibling;
            if (panel.style.display === "block") {
                panel.style.display = "none";
            } else {
                panel.style.display = "block";
            }
        });
    });
});


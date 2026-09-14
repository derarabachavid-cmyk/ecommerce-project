document.addEventListener("DOMContentLoaded", function () {

    console.log("E-Commerce website loaded successfully.");


    /* =====================================================
       AUTO HIDE MESSAGES
       ===================================================== */

    const messages = document.querySelectorAll(".message");

    messages.forEach(function (message) {

        setTimeout(function () {

            message.style.opacity = "0";
            message.style.transform = "translateX(30px)";

            setTimeout(function () {
                message.remove();
            }, 300);

        }, 3500);

    });


    /* =====================================================
       IMAGE ERROR HANDLING
       ===================================================== */

    const images = document.querySelectorAll("img");

    images.forEach(function (image) {

        image.addEventListener("error", function () {

            image.style.display = "none";

        });

    });


    /* =====================================================
       BUTTON LOADING EFFECT
       ===================================================== */

    const primaryButtons = document.querySelectorAll(
        'form button[type="submit"]'
    );

    primaryButtons.forEach(function (button) {

        button.addEventListener("click", function () {

            const form = button.closest("form");

            if (!form) {
                return;
            }

            if (form.checkValidity()) {

                button.style.opacity = "0.7";
                button.style.pointerEvents = "none";

            }

        });

    });

});
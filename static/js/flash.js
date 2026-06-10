window.HandLinkFlash = {
    init() {
        const flashMessages = document.querySelectorAll(".alert");

        flashMessages.forEach((alert) => {
            const progressBar = alert.querySelector(".flash-progress-bar");

            if (progressBar) {
                setTimeout(() => {
                    progressBar.style.transition = "width 3s linear";
                    progressBar.style.width = "0%";
                }, 50);
            }

            setTimeout(() => {
                alert.classList.remove("show");

                setTimeout(() => {
                    const parentContainer = alert.parentElement;
                    alert.remove();

                    if (parentContainer && parentContainer.children.length === 0) {
                        parentContainer.remove();
                    }
                }, 150);
            }, 3500);
        });
    },
};

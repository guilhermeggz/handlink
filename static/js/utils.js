window.HandLinkUtils = {
    escapeHtml(value) {
        const element = document.createElement("div");
        element.textContent = value ?? "";
        return element.innerHTML;
    },

    normalizeCategory(value) {
        return String(value || "")
            .toLowerCase()
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "");
    },
};

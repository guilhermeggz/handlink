const fallbackCategories = [
    { id: 1, nome: "Limpeza", icone: "fa-broom" },
    { id: 2, nome: "Eletricidade", icone: "fa-bolt" },
    { id: 3, nome: "Encanamento", icone: "fa-wrench" },
    { id: 4, nome: "Montagem", icone: "fa-hammer" },
    { id: 5, nome: "Pintura", icone: "fa-paint-roller" },
    { id: 6, nome: "Frete", icone: "fa-truck" },
];

const categoryIcons = {
    limpeza: "fa-broom",
    eletricidade: "fa-bolt",
    encanamento: "fa-wrench",
    montagem: "fa-hammer",
    pintura: "fa-paint-roller",
    frete: "fa-truck",
};

const fallbackServices = [
    {
        titulo: "Instalação de ar-condicionado",
        profissional: "João Silva",
        avaliacao: "4.9",
        imagem: "https://images.unsplash.com/photo-1621905252507-b35492cc74b4?auto=format&fit=crop&w=500&q=60",
        preco: "R$ 150,00",
    },
    {
        titulo: "Faxina completa",
        profissional: "Maria Souza",
        avaliacao: "5.0",
        imagem: "https://images.unsplash.com/photo-1581578731548-c64695cc6952?auto=format&fit=crop&w=500&q=60",
        preco: "R$ 120,00",
    },
    {
        titulo: "Reparo hidráulico",
        profissional: "Carlos Lima",
        avaliacao: "4.8",
        imagem: "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?auto=format&fit=crop&w=500&q=60",
        preco: "R$ 90,00",
    },
    {
        titulo: "Pintura de interior",
        profissional: "Ana Beatriz",
        avaliacao: "4.7",
        imagem: "https://images.unsplash.com/photo-1562259949-e8e7689d7828?auto=format&fit=crop&w=500&q=60",
        preco: "Sob consulta",
    },
];

document.addEventListener("DOMContentLoaded", () => {
    loadCategories();
    renderServices(fallbackServices);
    bindSearchForm();
    animateFlashMessages();
});

function bindSearchForm() {
    const searchForm = document.getElementById("search-form");
    if (!searchForm) {
        return;
    }

    searchForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        await searchServices();
    });
}

async function loadCategories() {
    const container = document.getElementById("categories-container");
    if (!container) {
        return;
    }

    try {
        const response = await fetch("/api/categorias");
        if (!response.ok) {
            throw new Error("Erro ao buscar categorias.");
        }

        const data = await response.json();
        const categories = data.categorias.map((category) => ({
            id: category.id,
            nome: category.name,
            icone: getCategoryIcon(category.name),
        }));

        renderCategories(categories.length ? categories : fallbackCategories);
    } catch (error) {
        renderCategories(fallbackCategories);
    }
}

function renderCategories(categories) {
    const container = document.getElementById("categories-container");
    container.innerHTML = "";

    categories.forEach((category) => {
        const col = document.createElement("div");
        col.className = "col-6 col-md-4 col-lg-2";
        col.innerHTML = `
            <a href="/servicos/categoria/${category.id}" class="category-link">
                <div class="card category-card h-100 text-center p-3 shadow-sm">
                    <div class="card-body">
                        <i class="fa-solid ${category.icone} category-icon"></i>
                        <h6 class="card-title fw-bold text-dark mt-2">${category.nome}</h6>
                    </div>
                </div>
            </a>
        `;
        container.appendChild(col);
    });
}

function getCategoryIcon(categoryName) {
    const normalizedName = categoryName
        .toLowerCase()
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "");

    return categoryIcons[normalizedName] || "fa-briefcase";
}

async function searchServices() {
    const query = document.getElementById("search-input").value.trim();
    const subtitle = document.getElementById("services-subtitle");

    if (!query) {
        subtitle.textContent = "Baseado nos agendamentos mais concluídos do último mês.";
        renderServices(fallbackServices);
        return;
    }

    subtitle.textContent = `Resultados para "${query}"`;

    try {
        const response = await fetch(`/api/servicos/buscar?q=${encodeURIComponent(query)}`);
        if (!response.ok) {
            throw new Error("Erro ao buscar serviços.");
        }

        const data = await response.json();
        const services = data.servicos.map((service) => ({
            titulo: service.name,
            profissional: service.prestador || "Profissional HandLink",
            avaliacao: "Novo",
            imagem: "https://images.unsplash.com/photo-1521791136064-7986c2920216?auto=format&fit=crop&w=500&q=60",
            preco: service.preco ? `R$ ${Number(service.preco).toFixed(2).replace(".", ",")}` : "Sob consulta",
        }));

        renderServices(services, "Nenhum serviço encontrado para sua busca.");
    } catch (error) {
        renderServices([], "Não foi possível carregar os serviços agora.");
    }
}

function renderServices(services, emptyMessage = "Nenhum serviço disponível no momento.") {
    const container = document.getElementById("services-container");
    if (!container) {
        return;
    }

    container.innerHTML = "";

    if (!services.length) {
        container.innerHTML = `<div class="col-12 text-center text-muted">${emptyMessage}</div>`;
        return;
    }

    services.forEach((service) => {
        const col = document.createElement("div");
        col.className = "col-12 col-md-6 col-lg-3";
        col.innerHTML = `
            <div class="card service-card h-100 shadow-sm position-relative">
                <span class="badge-popular"><i class="fa-solid fa-star"></i> Em alta</span>
                <img src="${service.imagem}" class="card-img-top service-img" alt="${service.titulo}">
                <div class="card-body">
                    <h5 class="card-title fw-bold text-truncate" title="${service.titulo}">${service.titulo}</h5>
                    <p class="text-muted mb-2 small">
                        <i class="fa-solid fa-user text-primary"></i>
                        ${service.profissional}
                    </p>
                    <div class="d-flex justify-content-between align-items-center mt-3">
                        <span class="text-success fw-bold">${service.preco}</span>
                        <span class="badge bg-light text-dark border">
                            <i class="fa-solid fa-star text-warning"></i>
                            ${service.avaliacao}
                        </span>
                    </div>
                </div>
                <div class="card-footer bg-white border-top-0 pb-3">
                    <a class="btn btn-outline-primary w-100" href="/login">Ver detalhes</a>
                </div>
            </div>
        `;
        container.appendChild(col);
    });
}

function animateFlashMessages() {
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
}

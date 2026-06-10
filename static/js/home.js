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

const categoryImages = {
    limpeza: "https://images.unsplash.com/photo-1581578731548-c64695cc6952?auto=format&fit=crop&w=500&q=60",
    eletricidade: "https://images.unsplash.com/photo-1621905252507-b35492cc74b4?auto=format&fit=crop&w=500&q=60",
    encanamento: "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?auto=format&fit=crop&w=500&q=60",
    montagem: "https://images.unsplash.com/photo-1598300042247-d088f8ab3a91?auto=format&fit=crop&w=500&q=60",
    pintura: "https://images.unsplash.com/photo-1562259949-e8e7689d7828?auto=format&fit=crop&w=500&q=60",
    frete: "https://images.unsplash.com/photo-1601584115197-04ecc0da31d7?auto=format&fit=crop&w=500&q=60",
    default: "https://images.unsplash.com/photo-1521791136064-7986c2920216?auto=format&fit=crop&w=500&q=60",
};

window.HandLinkHome = (() => {
    const trendingPageSize = 4;
    let trendingOffset = 0;
    let trendingHasMore = true;
    let isSearchMode = false;

    const { escapeHtml, normalizeCategory } = window.HandLinkUtils;

    function init() {
        loadCategories();
        
        if (document.getElementById("services-container")) {
            loadTrendingServices({ reset: true });
        }
        
        bindSearchForm();
        bindLoadMoreButton();
    }

    function bindSearchForm() {
        const searchForm = document.getElementById("search-form");
        if (!searchForm) return;

        searchForm.addEventListener("submit", async (event) => {
            event.preventDefault();
            await searchServices();
        });
    }

    function bindLoadMoreButton() {
        const button = document.getElementById("load-more-services");
        if (!button) return;

        button.addEventListener("click", async () => {
            if (isSearchMode) {
                const searchInput = document.getElementById("search-input");
                if (searchInput) {
                    searchInput.value = "";
                }

                await loadTrendingServices({ reset: true });
                return;
            }

            await loadTrendingServices();
        });
    }

    async function loadCategories() {
        const mainContainer = document.getElementById("categories-container");
        const footerContainer = document.getElementById("categories-footer-container");
        
        if (!mainContainer && !footerContainer) return;

        try {
            const response = await fetch("/api/categorias");
            if (!response.ok) {
                throw new Error("Erro ao buscar categorias.");
            }

            const data = await response.json();
            const apiCategories = data.categorias || [];
            const categories = apiCategories.map((category) => ({
                id: category.id,
                nome: category.name,
                icone: getCategoryIcon(category.name),
            }));

            renderCategories(categories.length ? categories : fallbackCategories);
            renderCategoriesFooter(categories.length ? categories : fallbackCategories);
        } catch (error) {
            console.error("Erro ao carregar categorias:", error);

            renderCategories(fallbackCategories);
            renderCategoriesFooter(fallbackCategories);
        }
    }

    function renderCategories(categories) {
        const container = document.getElementById("categories-container");

        if (!container) return;

        container.innerHTML = "";

        categories.forEach((category) => {
            const col = document.createElement("div");
            col.className = "col-6 col-md-4 col-lg-2";
            col.innerHTML = `
                <a href="/servicos/categoria/${category.id}" class="category-link">
                    <div class="card category-card h-100 text-center p-3 shadow-sm">
                        <div class="card-body">
                            <i class="fa-solid ${category.icone} category-icon"></i>
                            <h6 class="card-title fw-bold text-dark mt-2">${escapeHtml(category.nome)}</h6>
                        </div>
                    </div>
                </a>
            `;
            container.appendChild(col);
        });
    }

    function renderCategoriesFooter(categories) {
        const container = document.getElementById("categories-footer-container");
        
        if (!container) return; 
        
        container.innerHTML = "";

        if (categories.length === 0) {
            container.innerHTML = `<li class="text-white-50 small fst-italic">Nenhuma categoria cadastrada.</li>`;
            return;
        }

        categories.forEach((category) => {
            const li = document.createElement("li");
            li.className = "mb-2";
            li.innerHTML = `
                <a href="/servicos/categoria/${category.id}" class="text-white-50 text-decoration-none link-light small">
                    ${escapeHtml(category.nome)}
                </a>
            `;
            container.appendChild(li);
        });
    }


    function getCategoryIcon(categoryName) {
        const normalizedName = normalizeCategory(categoryName);
        return categoryIcons[normalizedName] || "fa-briefcase";
    }

    async function loadTrendingServices({ reset = false } = {}) {
        const container = document.getElementById("services-container");
        const subtitle = document.getElementById("services-subtitle");
        if (!container) {
            return;
        }

        isSearchMode = false;

        if (reset) {
            trendingOffset = 0;
            trendingHasMore = true;
            container.innerHTML = loadingMarkup("Buscando serviços em alta...");
        }

        if (!trendingHasMore && !reset) {
            updateLoadMoreButton();
            return;
        }

        setLoadMoreButtonState({ label: "Carregando...", disabled: true, hidden: false });

        try {
            const params = new URLSearchParams({
                limit: trendingPageSize,
                offset: trendingOffset,
            });
            const response = await fetch(`/api/servicos/em-alta?${params}`);

            if (!response.ok) {
                throw new Error("Erro ao buscar serviços em alta.");
            }

            const data = await response.json();
            const services = (data.servicos || []).map(mapApiService);

            if (reset) {
                container.innerHTML = "";
            }

            appendServices(services, "Nenhum serviço disponível no momento.");
            trendingOffset += services.length;
            trendingHasMore = Boolean(data.has_more);

            if (subtitle) {
                const total = data.total_servicos || 0;
                subtitle.textContent = total
                    ? `${total} serviço${total === 1 ? "" : "s"} disponível${total === 1 ? "" : "is"} no momento.`
                    : "Assim que houver serviços cadastrados, eles aparecerão aqui.";
            }

            updateLoadMoreButton();
        } catch (error) {
            renderServices([], "Não foi possível carregar os serviços agora.");
            if (subtitle) {
                subtitle.textContent = "Tente novamente em alguns instantes.";
            }
            setLoadMoreButtonState({ hidden: true });
        }
    }

    async function searchServices() {
        const query = document.getElementById("search-input").value.trim();
        const subtitle = document.getElementById("services-subtitle");

        if (!query) {
            await loadTrendingServices({ reset: true });
            return;
        }

        isSearchMode = true;
        subtitle.textContent = `Resultados para "${query}"`;
        setLoadMoreButtonState({ label: "Buscando...", disabled: true, hidden: false });

        try {
            const response = await fetch(`/api/servicos/buscar?q=${encodeURIComponent(query)}`);
            if (!response.ok) {
                throw new Error("Erro ao buscar serviços.");
            }

            const data = await response.json();
            const services = (data.servicos || []).map(mapApiService);

            renderServices(services, "Nenhum serviço encontrado para sua busca.");
            setLoadMoreButtonState({ label: "Voltar aos serviços em alta", disabled: false, hidden: false });
        } catch (error) {
            renderServices([], "Não foi possível carregar os serviços agora.");
            setLoadMoreButtonState({ label: "Voltar aos serviços em alta", disabled: false, hidden: false });
        }
    }

    function mapApiService(service) {
        const categoryName = service.categoria || "";
        const categoryKey = normalizeCategory(categoryName);
        const price = service.preco
            ? `R$ ${Number(service.preco).toFixed(2).replace(".", ",")}`
            : "Sob consulta";

        return {
            titulo: service.name || "Serviço disponível",
            profissional: service.prestador || "Profissional HandLink",
            avaliacao: "Novo",
            imagem: categoryImages[categoryKey] || categoryImages.default,
            preco: price,
            detalhesUrl: service.id ? `/servicos/detalhes/${service.id}` : "/login",
        };
    }

    function renderServices(services, emptyMessage = "Nenhum serviço disponível no momento.") {
        const container = document.getElementById("services-container");
        if (!container) {
            return;
        }

        container.innerHTML = "";
        appendServices(services, emptyMessage);
    }

    function appendServices(services, emptyMessage = "Nenhum serviço disponível no momento.") {
        const container = document.getElementById("services-container");
        if (!container) {
            return;
        }

        if (!services.length && !container.children.length) {
            container.innerHTML = `<div class="col-12 text-center text-muted">${escapeHtml(emptyMessage)}</div>`;
            return;
        }

        services.forEach((service) => {
            const col = document.createElement("div");
            col.className = "col-12 col-md-6 col-lg-3";
            col.innerHTML = `
                <div class="card service-card h-100 shadow-sm position-relative">
                    <span class="badge-popular"><i class="fa-solid fa-star"></i> Em alta</span>
                    <img src="${service.imagem}" class="card-img-top service-img" alt="${escapeHtml(service.titulo)}">
                    <div class="card-body">
                        <h5 class="card-title fw-bold text-truncate" title="${escapeHtml(service.titulo)}">${escapeHtml(service.titulo)}</h5>
                        <p class="text-muted mb-2 small">
                            <i class="fa-solid fa-user text-primary"></i>
                            ${escapeHtml(service.profissional)}
                        </p>
                        <div class="d-flex justify-content-between align-items-center mt-3">
                            <span class="text-success fw-bold">${escapeHtml(service.preco)}/hora</span>
                            <span class="badge bg-light text-dark border">
                                <i class="fa-solid fa-star text-warning"></i>
                                ${escapeHtml(service.avaliacao)}
                            </span>
                        </div>
                    </div>
                    <div class="card-footer bg-white border-top-0 pb-3">
                        <a class="btn btn-outline-primary w-100" href="${service.detalhesUrl}">Ver detalhes</a>
                    </div>
                </div>
            `;
            container.appendChild(col);
        });
    }

    function updateLoadMoreButton() {
        setLoadMoreButtonState({
            label: "Ver Mais",
            disabled: false,
            hidden: !trendingHasMore,
        });
    }

    function setLoadMoreButtonState({ label = "Ver Mais", disabled = false, hidden = false } = {}) {
        const button = document.getElementById("load-more-services");
        if (!button) {
            return;
        }

        button.textContent = label;
        button.disabled = disabled;
        button.classList.toggle("d-none", hidden);
    }

    function loadingMarkup(message) {
        return `
            <div class="col-12 text-center text-muted">
                <div class="spinner-border text-danger" role="status"></div>
                <p class="mt-2">${escapeHtml(message)}</p>
            </div>
        `;
    }

    return { init };
})();

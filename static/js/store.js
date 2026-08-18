(() => {
  const grid = document.getElementById('storeProductGrid');
  if (!grid) return;

  const cards = [...grid.querySelectorAll('.store-product-card')];
  const search = document.getElementById('storeSearch');
  const sort = document.getElementById('storeSort');
  const count = document.getElementById('visibleProductCount');
  const activeLabel = document.getElementById('activeStoreFilter');
  const empty = document.getElementById('storeEmpty');
  const interestCount = document.getElementById('interestCount');
  const storageKey = 'bj-sports-store-interest';
  let interests = new Set(JSON.parse(localStorage.getItem(storageKey) || '[]'));

  function selectedValue(name) {
    return document.querySelector(`input[name="${name}"]:checked`)?.value || 'all';
  }

  function matchesPrice(price, range) {
    if (range === 'all') return true;
    const [minimum, maximum] = range.split('-').map(Number);
    return price >= minimum && price < maximum;
  }

  function applyFilters() {
    const sport = selectedValue('sport');
    const price = selectedValue('price');
    const term = search.value.trim().toLocaleLowerCase('pt-BR');
    const categories = new Set([...document.querySelectorAll('.category-filter:checked')].map(input => input.value));

    const visible = cards.filter(card => {
      const searchable = `${card.dataset.name} ${card.dataset.category} ${card.dataset.sport}`.toLocaleLowerCase('pt-BR');
      const show = (sport === 'all' || card.dataset.sport === sport)
        && (!categories.size || categories.has(card.dataset.category))
        && matchesPrice(Number(card.dataset.price), price)
        && (!term || searchable.includes(term));
      card.classList.toggle('hidden', !show);
      return show;
    });

    const comparator = {
      name: (a, b) => a.dataset.name.localeCompare(b.dataset.name, 'pt-BR'),
      'price-asc': (a, b) => Number(a.dataset.price) - Number(b.dataset.price),
      'price-desc': (a, b) => Number(b.dataset.price) - Number(a.dataset.price),
      featured: (a, b) => cards.indexOf(a) - cards.indexOf(b)
    }[sort.value];
    visible.sort(comparator).forEach(card => grid.appendChild(card));

    count.textContent = visible.length;
    empty.classList.toggle('hidden', visible.length !== 0);
    const labels = [];
    if (sport !== 'all') labels.push(sport === 'jiu-jitsu' ? 'Jiu-Jitsu' : 'Boxe');
    if (categories.size) labels.push([...categories].join(', '));
    if (price !== 'all') labels.push('faixa de preço selecionada');
    if (term) labels.push(`busca: “${search.value.trim()}”`);
    activeLabel.textContent = labels.length ? labels.join(' • ') : 'Todos os esportes e categorias';
  }

  function updateInterestButtons() {
    document.querySelectorAll('[data-interest]').forEach(button => {
      const active = interests.has(button.dataset.interest);
      button.classList.toggle('active', active);
      button.setAttribute('aria-pressed', String(active));
    });
    interestCount.textContent = interests.size;
    localStorage.setItem(storageKey, JSON.stringify([...interests]));
  }

  document.querySelectorAll('input[name="sport"], input[name="price"], .category-filter').forEach(input => input.addEventListener('change', applyFilters));
  search.addEventListener('input', applyFilters);
  sort.addEventListener('change', applyFilters);
  document.querySelectorAll('[data-quick-filter]').forEach(button => button.addEventListener('click', () => {
    const input = document.querySelector(`input[name="sport"][value="${button.dataset.quickFilter}"]`);
    input.checked = true;
    document.querySelector('.store-layout').scrollIntoView({behavior: 'smooth'});
    applyFilters();
  }));
  document.querySelectorAll('[data-interest]').forEach(button => button.addEventListener('click', () => {
    const id = button.dataset.interest;
    interests.has(id) ? interests.delete(id) : interests.add(id);
    updateInterestButtons();
  }));
  document.getElementById('clearStoreFilters').addEventListener('click', () => {
    document.querySelector('input[name="sport"][value="all"]').checked = true;
    document.querySelector('input[name="price"][value="all"]').checked = true;
    document.querySelectorAll('.category-filter').forEach(input => { input.checked = false; });
    search.value = '';
    sort.value = 'featured';
    applyFilters();
  });
  const filterPanel = document.querySelector('.store-filter-panel');
  const mobileFilterToggle = document.getElementById('storeMobileFilterToggle');
  if (window.matchMedia('(max-width: 800px)').matches) filterPanel.classList.add('filters-collapsed');
  mobileFilterToggle.addEventListener('click', () => {
    const collapsed = filterPanel.classList.toggle('filters-collapsed');
    mobileFilterToggle.textContent = collapsed ? 'Abrir' : 'Fechar';
  });

  updateInterestButtons();
  applyFilters();
})();

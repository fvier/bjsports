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

  // -------------------------------------------------------------
  // 1. FILTERING & SORTING LOGIC
  // -------------------------------------------------------------
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
    const sportNames = { 'jiu-jitsu': 'Jiu-Jitsu', 'boxe': 'Boxe', 'muay-thai': 'Muay Thai', 'mma': 'MMA' };
    if (sport !== 'all') labels.push(sportNames[sport] || sport);
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

  // -------------------------------------------------------------
  // 2. CARD SWATCH COLOR SWITCHING
  // -------------------------------------------------------------
  cards.forEach(card => {
    const swatches = card.querySelectorAll('.store-swatch-dot');
    if (!swatches.length) return;

    const imgEl = card.querySelector('.card-img-element');
    const badgeEl = card.querySelector('.card-badge-element');
    const priceEl = card.querySelector('.card-price');
    const oldPriceEl = card.querySelector('.card-old-price');

    swatches.forEach(swatch => {
      const activateSwatch = () => {
        swatches.forEach(s => s.classList.remove('active'));
        swatch.classList.add('active');

        if (imgEl && swatch.dataset.colorImg) imgEl.src = swatch.dataset.colorImg;
        if (priceEl && swatch.dataset.colorPrice) priceEl.textContent = swatch.dataset.colorPrice;
        if (oldPriceEl) oldPriceEl.textContent = swatch.dataset.colorOldPrice || '';
        if (badgeEl && swatch.dataset.colorBadge) badgeEl.textContent = swatch.dataset.colorBadge;
      };

      swatch.addEventListener('click', (e) => {
        e.stopPropagation();
        activateSwatch();
      });

      swatch.addEventListener('mouseenter', () => {
        activateSwatch();
      });
    });
  });

  // -------------------------------------------------------------
  // 3. PRODUCT QUICK-VIEW MODAL LOGIC
  // -------------------------------------------------------------
  const modal = document.getElementById('storeProductModal');
  const closeModalBtn = document.getElementById('closeProductModal');
  const modalTitle = document.getElementById('modalTitle');
  const modalSportTag = document.getElementById('modalSportTag');
  const modalCategoryTag = document.getElementById('modalCategoryTag');
  const modalMainImg = document.getElementById('modalMainImg');
  const modalBadge = document.getElementById('modalProductBadge');
  const modalPrice = document.getElementById('modalPrice');
  const modalOldPrice = document.getElementById('modalOldPrice');
  const modalDescription = document.getElementById('modalDescription');
  const modalColorBlock = document.getElementById('modalColorBlock');
  const modalColorPills = document.getElementById('modalColorPills');
  const modalSelectedColorText = document.getElementById('modalSelectedColorText');
  const modalSizeBlock = document.getElementById('modalSizeBlock');
  const modalSizePills = document.getElementById('modalSizePills');
  const modalSelectedSizeText = document.getElementById('modalSelectedSizeText');
  const modalThumbsRow = document.getElementById('modalThumbsRow');
  const modalZapLink = document.getElementById('modalZapLink');
  const modalInterestBtn = document.getElementById('modalInterestBtn');
  const modalInterestLabel = document.getElementById('modalInterestLabel');

  let currentProduct = null;
  let selectedColor = null;
  let selectedSize = null;

  function updateZapLink() {
    if (!currentProduct || !modalZapLink) return;
    const phone = '5554999999999'; // BJ Sports WhatsApp support
    const colorStr = selectedColor ? ` (Cor: ${selectedColor.name})` : '';
    const sizeStr = selectedSize ? ` (Tamanho: ${selectedSize})` : '';
    const text = encodeURIComponent(`Olá! Gostaria de consultar a disponibilidade do item *${currentProduct.name}*${colorStr}${sizeStr} na loja BJ Sports.`);
    modalZapLink.href = `https://wa.me/${phone}?text=${text}`;
  }

  function openModalForProduct(card) {
    if (!card.dataset.json || !modal) return;
    try {
      currentProduct = JSON.parse(card.dataset.json);
    } catch (e) {
      return;
    }

    const sportNames = { 'jiu-jitsu': 'Jiu-Jitsu', 'boxe': 'Boxe', 'muay-thai': 'Muay Thai', 'mma': 'MMA' };
    modalSportTag.textContent = sportNames[currentProduct.sport] || currentProduct.sport;
    modalCategoryTag.textContent = currentProduct.category || '';
    modalTitle.textContent = currentProduct.name || '';
    modalDescription.textContent = currentProduct.description || '';
    modalBadge.textContent = currentProduct.badge || 'Oficial';

    // Formatted Price
    const initialPriceStr = `R$ ${Number(currentProduct.price).toFixed(2).replace('.', ',')}`;
    modalPrice.textContent = initialPriceStr;
    if (currentProduct.old_price) {
      modalOldPrice.textContent = `R$ ${Number(currentProduct.old_price).toFixed(2).replace('.', ',')}`;
    } else {
      modalOldPrice.textContent = '';
    }

    // Set Initial Image
    const initialImgSrc = currentProduct.image ? `/static/${currentProduct.image}` : '';
    modalMainImg.src = initialImgSrc;
    modalMainImg.alt = currentProduct.name;

    // Reset Gallery / Thumbs
    modalThumbsRow.innerHTML = '';
    modalColorPills.innerHTML = '';
    modalSizePills.innerHTML = '';

    // Color Swatches / Gallery Setup
    if (currentProduct.colors && currentProduct.colors.length > 0) {
      modalColorBlock.classList.remove('hidden');
      selectedColor = currentProduct.colors[0];
      modalSelectedColorText.textContent = selectedColor.name;

      currentProduct.colors.forEach((col, idx) => {
        // Color pill button
        const pill = document.createElement('button');
        pill.type = 'button';
        pill.className = `modal-pill-btn ${idx === 0 ? 'active' : ''}`;
        pill.innerHTML = `<span class="modal-pill-color-dot" style="background-color:${col.hex}"></span> ${col.name}`;
        
        pill.addEventListener('click', () => {
          document.querySelectorAll('.modal-pill-btn').forEach(p => p.classList.remove('active'));
          pill.classList.add('active');
          selectedColor = col;
          modalSelectedColorText.textContent = col.name;
          
          if (col.image) modalMainImg.src = `/static/${col.image}`;
          if (col.price) modalPrice.textContent = `R$ ${Number(col.price).toFixed(2).replace('.', ',')}`;
          if (col.old_price) modalOldPrice.textContent = `R$ ${Number(col.old_price).toFixed(2).replace('.', ',')}`;
          if (col.badge) modalBadge.textContent = col.badge;
          
          updateZapLink();
        });
        modalColorPills.appendChild(pill);

        // Thumbnail button
        if (col.image) {
          const thumb = document.createElement('button');
          thumb.type = 'button';
          thumb.className = `modal-thumb-btn ${idx === 0 ? 'active' : ''}`;
          thumb.innerHTML = `<img src="/static/${col.image}" alt="${col.name}">`;
          thumb.addEventListener('click', () => {
            document.querySelectorAll('.modal-thumb-btn').forEach(t => t.classList.remove('active'));
            thumb.classList.add('active');
            pill.click();
          });
          modalThumbsRow.appendChild(thumb);
        }
      });
    } else {
      modalColorBlock.classList.add('hidden');
      selectedColor = null;
    }

    // Size Pills Setup
    if (currentProduct.sizes) {
      modalSizeBlock.classList.remove('hidden');
      const sizeList = Array.isArray(currentProduct.sizes) ? currentProduct.sizes : [currentProduct.sizes];
      selectedSize = sizeList[0];
      modalSelectedSizeText.textContent = selectedSize;

      sizeList.forEach((sz, idx) => {
        const szPill = document.createElement('button');
        szPill.type = 'button';
        szPill.className = `modal-pill-btn ${idx === 0 ? 'active' : ''}`;
        szPill.textContent = sz;
        szPill.addEventListener('click', () => {
          modalSizePills.querySelectorAll('.modal-pill-btn').forEach(p => p.classList.remove('active'));
          szPill.classList.add('active');
          selectedSize = sz;
          modalSelectedSizeText.textContent = sz;
          updateZapLink();
        });
        modalSizePills.appendChild(szPill);
      });
    } else {
      modalSizeBlock.classList.add('hidden');
      selectedSize = null;
    }

    // Update Interest State in Modal
    if (modalInterestBtn) {
      modalInterestBtn.dataset.interest = currentProduct.id;
      const isInterested = interests.has(currentProduct.id);
      modalInterestLabel.textContent = isInterested ? 'Remover dos Interesses' : 'Salvar nos Interesses';
    }

    updateZapLink();
    modal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
  }

  function closeModal() {
    if (!modal) return;
    modal.classList.add('hidden');
    document.body.style.overflow = '';
  }

  // Event delegation for opening quick-view modal
  document.addEventListener('click', (e) => {
    const trigger = e.target.closest('[data-open-modal]');
    if (trigger) {
      const card = trigger.closest('.store-product-card');
      if (card) openModalForProduct(card);
    }
  });

  if (closeModalBtn) closeModalBtn.addEventListener('click', closeModal);
  if (modal) {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) closeModal();
    });
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && !modal.classList.contains('hidden')) closeModal();
    });
  }

  if (modalInterestBtn) {
    modalInterestBtn.addEventListener('click', () => {
      if (!currentProduct) return;
      const id = currentProduct.id;
      interests.has(id) ? interests.delete(id) : interests.add(id);
      updateInterestButtons();
      const isInterested = interests.has(id);
      modalInterestLabel.textContent = isInterested ? 'Remover dos Interesses' : 'Salvar nos Interesses';
    });
  }

  // -------------------------------------------------------------
  // 4. EVENT LISTENERS SETUP
  // -------------------------------------------------------------
  document.querySelectorAll('input[name="sport"], input[name="price"], .category-filter').forEach(input => input.addEventListener('change', applyFilters));
  if (search) search.addEventListener('input', applyFilters);
  if (sort) sort.addEventListener('change', applyFilters);

  document.querySelectorAll('[data-quick-filter]').forEach(button => button.addEventListener('click', () => {
    const input = document.querySelector(`input[name="sport"][value="${button.dataset.quickFilter}"]`);
    if (input) {
      input.checked = true;
      document.querySelector('.store-layout')?.scrollIntoView({behavior: 'smooth'});
      applyFilters();
    }
  }));

  document.querySelectorAll('[data-interest]').forEach(button => button.addEventListener('click', (e) => {
    e.stopPropagation();
    const id = button.dataset.interest;
    interests.has(id) ? interests.delete(id) : interests.add(id);
    updateInterestButtons();
  }));

  const clearBtn = document.getElementById('clearStoreFilters');
  if (clearBtn) {
    clearBtn.addEventListener('click', () => {
      const sportAll = document.querySelector('input[name="sport"][value="all"]');
      const priceAll = document.querySelector('input[name="price"][value="all"]');
      if (sportAll) sportAll.checked = true;
      if (priceAll) priceAll.checked = true;
      document.querySelectorAll('.category-filter').forEach(input => { input.checked = false; });
      if (search) search.value = '';
      if (sort) sort.value = 'featured';
      applyFilters();
    });
  }

  const filterPanel = document.querySelector('.store-filter-panel');
  const mobileFilterToggle = document.getElementById('storeMobileFilterToggle');
  if (filterPanel && mobileFilterToggle) {
    if (window.matchMedia('(max-width: 800px)').matches) filterPanel.classList.add('filters-collapsed');
    mobileFilterToggle.addEventListener('click', () => {
      const collapsed = filterPanel.classList.toggle('filters-collapsed');
      mobileFilterToggle.textContent = collapsed ? 'Abrir' : 'Fechar';
    });
  }

  updateInterestButtons();
  applyFilters();

  // -------------------------------------------------------------
  // 5. INSTRUCTOR EDIT PRODUCT MODAL LOGIC
  // -------------------------------------------------------------
  const editModal = document.getElementById('storeEditProductModal');
  const closeEditModalBtn = document.getElementById('closeEditProductModal');
  const cancelEditBtn = document.getElementById('cancelEditProductBtn');
  const editForm = document.getElementById('storeEditProductForm');
  let currentEditingCard = null;

  function openEditModal(card) {
    if (!editModal || !card || !card.dataset.json) return;
    let prod = null;
    try {
      prod = JSON.parse(card.dataset.json);
    } catch (e) {
      return;
    }
    currentEditingCard = card;

    document.getElementById('editProductId').value = prod.id;
    document.getElementById('editModalProductCode').textContent = prod.id;
    document.getElementById('editIsSoldOut').checked = Boolean(prod.is_sold_out);
    document.getElementById('editIsHidden').checked = Boolean(prod.is_hidden);
    document.getElementById('editStockQuantity').value = prod.stock_quantity !== null && prod.stock_quantity !== undefined ? prod.stock_quantity : '';
    document.getElementById('editOutOfStockText').value = prod.out_of_stock_text || 'ESGOTADO • CHEGARÁ EM BREVE';
    document.getElementById('editProductName').value = prod.name || '';
    document.getElementById('editProductBadge').value = prod.badge || '';
    document.getElementById('editProductPrice').value = prod.price;
    document.getElementById('editProductOldPrice').value = prod.old_price !== null && prod.old_price !== undefined ? prod.old_price : '';
    document.getElementById('editProductDescription').value = prod.description || '';

    editModal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
  }

  function closeEditModal() {
    if (!editModal) return;
    editModal.classList.add('hidden');
    document.body.style.overflow = '';
    currentEditingCard = null;
  }

  if (closeEditModalBtn) closeEditModalBtn.addEventListener('click', closeEditModal);
  if (cancelEditBtn) cancelEditBtn.addEventListener('click', closeEditModal);
  if (editModal) {
    editModal.addEventListener('click', (e) => {
      if (e.target === editModal) closeEditModal();
    });
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && !editModal.classList.contains('hidden')) closeEditModal();
    });
  }

  // Handle Edit Card button clicks
  document.addEventListener('click', (e) => {
    const editBtn = e.target.closest('[data-edit-product]');
    if (editBtn) {
      e.stopPropagation();
      e.preventDefault();
      const card = editBtn.closest('.store-product-card');
      if (card) openEditModal(card);
    }
  });

  if (editForm) {
    editForm.addEventListener('submit', (e) => {
      e.preventDefault();
      if (!currentEditingCard) return;

      const productId = document.getElementById('editProductId').value;
      const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || window.CSRF_TOKEN || '';

      const rawStock = document.getElementById('editStockQuantity').value.trim();
      const payload = {
        is_sold_out: document.getElementById('editIsSoldOut').checked,
        is_hidden: document.getElementById('editIsHidden').checked,
        stock_quantity: rawStock !== '' ? parseInt(rawStock, 10) : null,
        out_of_stock_text: document.getElementById('editOutOfStockText').value.trim(),
        name: document.getElementById('editProductName').value.trim(),
        badge: document.getElementById('editProductBadge').value.trim(),
        price: document.getElementById('editProductPrice').value.trim(),
        old_price: document.getElementById('editProductOldPrice').value.trim() || null,
        description: document.getElementById('editProductDescription').value.trim()
      };

      const saveBtn = document.getElementById('saveEditProductBtn');
      if (saveBtn) {
        saveBtn.disabled = true;
        saveBtn.innerHTML = 'Salvando...';
      }

      fetch(`/api/store/products/${productId}/edit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRF-Token': csrfToken
        },
        body: JSON.stringify(payload)
      })
      .then(res => res.json())
      .then(data => {
        if (saveBtn) {
          saveBtn.disabled = false;
          saveBtn.innerHTML = '<i data-lucide="save"></i> Salvar Alterações';
          if (window.lucide) window.lucide.createIcons();
        }

        if (data.success && data.product) {
          const updated = data.product;
          currentEditingCard.dataset.json = JSON.stringify(updated);
          currentEditingCard.dataset.name = updated.name.toLowerCase();
          currentEditingCard.dataset.price = updated.price;

          // Toggle hidden state class on card
          currentEditingCard.classList.toggle('is-product-hidden', Boolean(updated.is_hidden));

          // Update title
          const titleEl = currentEditingCard.querySelector('h3');
          if (titleEl) titleEl.textContent = updated.name;

          // Update prices
          const priceEl = currentEditingCard.querySelector('.card-price');
          if (priceEl) priceEl.textContent = 'R$ ' + Number(updated.price).toFixed(2).replace('.', ',');

          const oldPriceEl = currentEditingCard.querySelector('.card-old-price');
          if (oldPriceEl) {
            oldPriceEl.textContent = updated.old_price ? 'R$ ' + Number(updated.old_price).toFixed(2).replace('.', ',') : '';
          }

          // Update badge
          const mediaEl = currentEditingCard.querySelector('.store-product-media');
          let badgeEl = currentEditingCard.querySelector('.card-badge-element');
          if (updated.badge) {
            if (!badgeEl) {
              badgeEl = document.createElement('span');
              badgeEl.className = 'store-product-badge card-badge-element';
              mediaEl.appendChild(badgeEl);
            }
            badgeEl.textContent = updated.badge;
          } else if (badgeEl) {
            badgeEl.remove();
          }

          // Update Hidden badge on card media
          let hiddenBadge = mediaEl.querySelector('.store-hidden-badge');
          if (updated.is_hidden) {
            if (!hiddenBadge) {
              hiddenBadge = document.createElement('span');
              hiddenBadge.className = 'store-hidden-badge';
              hiddenBadge.textContent = '👁️ OCULTO NO SITE';
              mediaEl.appendChild(hiddenBadge);
            }
          } else if (hiddenBadge) {
            hiddenBadge.remove();
          }

          // Update Stock Quantity in card footer
          const priceContainer = currentEditingCard.querySelector('.store-price');
          let stockEl = currentEditingCard.querySelector('.card-stock-element');
          if (updated.stock_quantity !== null && updated.stock_quantity !== undefined) {
            if (!stockEl && priceContainer) {
              stockEl = document.createElement('span');
              stockEl.className = 'store-stock-count card-stock-element';
              priceContainer.prepend(stockEl);
            }
            if (stockEl) {
              stockEl.innerHTML = `<i data-lucide="boxes"></i> Estoque: <strong>${updated.stock_quantity}</strong> un.`;
              if (window.lucide) window.lucide.createIcons();
            }
          } else if (stockEl) {
            stockEl.remove();
          }

          // Update ribbon & sold out media class
          let ribbonEl = mediaEl.querySelector('.store-sold-out-ribbon');
          if (updated.is_sold_out) {
            mediaEl.classList.add('is-sold-out');
            const text = updated.out_of_stock_text || 'ESGOTADO • CHEGARÁ EM BREVE';
            if (!ribbonEl) {
              ribbonEl = document.createElement('div');
              ribbonEl.className = 'store-sold-out-ribbon';
              mediaEl.prepend(ribbonEl);
            }
            ribbonEl.innerHTML = `<span>⛔ ${text} ⛔</span>`;
          } else {
            mediaEl.classList.remove('is-sold-out');
            if (ribbonEl) ribbonEl.remove();
          }

          closeEditModal();
          applyFilters();
        } else {
          alert(data.error || 'Erro ao salvar alterações do produto.');
        }
      })
      .catch(err => {
        console.error(err);
        if (saveBtn) {
          saveBtn.disabled = false;
          saveBtn.innerHTML = '<i data-lucide="save"></i> Salvar Alterações';
          if (window.lucide) window.lucide.createIcons();
        }
        alert('Erro de conexão ao salvar produto.');
      });
    });
  }
})();

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

    // Render per-color stock section if colors exist
    const colorSection = document.getElementById('editColorStockSection');
    const colorGrid = document.getElementById('editColorStockGrid');
    if (colorSection && colorGrid) {
      colorGrid.innerHTML = '';
      if (prod.colors && prod.colors.length > 0) {
        colorSection.classList.remove('hidden');
        prod.colors.forEach(c => {
          const item = document.createElement('div');
          item.className = 'store-form-group';
          item.innerHTML = `
            <label for="editColorStock_${c.id}">
              <span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${c.hex};margin-right:6px;border:1px solid rgba(255,255,255,0.3);vertical-align:middle;"></span>
              Estoque (${c.name})
            </label>
            <input type="number" min="0" step="1" id="editColorStock_${c.id}" class="edit-color-stock-input" data-color-id="${c.id}" value="${c.stock_quantity !== null && c.stock_quantity !== undefined ? c.stock_quantity : ''}" placeholder="Ex: 5">
          `;
          colorGrid.appendChild(item);
        });
      } else {
        colorSection.classList.add('hidden');
      }
    }

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

      const colorInputs = editForm.querySelectorAll('.edit-color-stock-input');
      let colorStocks = null;
      if (colorInputs.length > 0) {
        colorStocks = {};
        colorInputs.forEach(input => {
          const val = input.value.trim();
          colorStocks[input.dataset.colorId] = val !== '' ? parseInt(val, 10) : null;
        });
      }

      const rawStock = document.getElementById('editStockQuantity').value.trim();
      const payload = {
        is_sold_out: document.getElementById('editIsSoldOut').checked,
        is_hidden: document.getElementById('editIsHidden').checked,
        stock_quantity: rawStock !== '' ? parseInt(rawStock, 10) : null,
        color_stocks: colorStocks,
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

          // Update swatches dataset for color stocks
          if (updated.colors && updated.colors.length > 0) {
            const swatches = currentEditingCard.querySelectorAll('.store-swatch-dot');
            swatches.forEach(swatch => {
              const matchC = updated.colors.find(c => c.id === swatch.dataset.colorId);
              if (matchC) {
                swatch.dataset.colorStock = matchC.stock_quantity !== null && matchC.stock_quantity !== undefined ? matchC.stock_quantity : '';
              }
            });
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

  // -------------------------------------------------------------
  // 5. INSTRUCTOR ADD PRODUCT MODAL LOGIC
  // -------------------------------------------------------------
  const addModal = document.getElementById('storeAddProductModal');
  const openAddBtn = document.getElementById('openAddProductModalBtn');
  const closeAddBtn = document.getElementById('closeAddProductModalBtn');
  const cancelAddBtn = document.getElementById('cancelAddProductBtn');
  const addForm = document.getElementById('storeAddProductForm');

  if (addModal && addForm) {
    const mainImageInput = document.getElementById('addProductImage');
    const mainImagePreview = document.getElementById('mainImagePreview');
    const mainImagePlaceholder = document.getElementById('mainImagePlaceholder');
    const galleryInput = document.getElementById('addProductGallery');
    const galleryThumbsGrid = document.getElementById('galleryThumbsGrid');
    const selectedColorTags = document.getElementById('selectedColorTags');
    const addPaletteColors = document.getElementById('addPaletteColors');
    const addSizesGrid = document.getElementById('addSizesGrid');

    let selectedColors = [];
    let selectedSizes = new Set();

    function openAddModal() {
      addModal.classList.remove('hidden');
      addModal.setAttribute('aria-hidden', 'false');
      document.body.style.overflow = 'hidden';
    }

    function closeAddModal() {
      addModal.classList.add('hidden');
      addModal.setAttribute('aria-hidden', 'true');
      document.body.style.overflow = '';
      addForm.reset();

      if (mainImagePreview) {
        mainImagePreview.src = '';
        mainImagePreview.classList.add('hidden');
      }
      if (mainImagePlaceholder) {
        mainImagePlaceholder.classList.remove('hidden');
      }

      selectedColors = [];
      renderColorTags();

      if (addPaletteColors) {
        addPaletteColors.querySelectorAll('.palette-dot').forEach(dot => dot.classList.remove('selected'));
      }

      selectedSizes.clear();
      if (addSizesGrid) {
        addSizesGrid.querySelectorAll('.size-pill').forEach(pill => pill.classList.remove('active'));
      }

      if (galleryThumbsGrid) {
        const items = galleryThumbsGrid.querySelectorAll('.gallery-thumb-item');
        items.forEach(el => el.remove());
      }

      document.querySelectorAll('.gender-btn').forEach(btn => {
        const rad = btn.querySelector('input');
        if (rad && rad.value === 'Unissex') {
          rad.checked = true;
          btn.classList.add('active');
        } else {
          btn.classList.remove('active');
        }
      });
    }

    if (openAddBtn) openAddBtn.addEventListener('click', openAddModal);
    if (closeAddBtn) closeAddBtn.addEventListener('click', closeAddModal);
    if (cancelAddBtn) cancelAddBtn.addEventListener('click', closeAddModal);

    addModal.addEventListener('click', (e) => {
      if (e.target === addModal) closeAddModal();
    });

    if (mainImageInput) {
      mainImageInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
          const reader = new FileReader();
          reader.onload = (evt) => {
            mainImagePreview.src = evt.target.result;
            mainImagePreview.classList.remove('hidden');
            if (mainImagePlaceholder) mainImagePlaceholder.classList.add('hidden');
          };
          reader.readAsDataURL(file);
        }
      });
    }

    if (galleryInput && galleryThumbsGrid) {
      galleryInput.addEventListener('change', (e) => {
        const files = Array.from(e.target.files);
        galleryThumbsGrid.querySelectorAll('.gallery-thumb-item').forEach(el => el.remove());
        files.forEach(f => {
          const reader = new FileReader();
          reader.onload = (evt) => {
            const img = document.createElement('img');
            img.src = evt.target.result;
            img.className = 'gallery-thumb-item';
            galleryThumbsGrid.appendChild(img);
          };
          reader.readAsDataURL(f);
        });
      });
    }

    const genderBtns = document.querySelectorAll('.gender-btn');
    genderBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        genderBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const input = btn.querySelector('input');
        if (input) input.checked = true;
      });
    });

    function renderColorTags() {
      if (!selectedColorTags) return;
      selectedColorTags.innerHTML = '';
      selectedColors.forEach((c, idx) => {
        const tag = document.createElement('span');
        tag.className = 'color-tag-item';
        tag.style.borderLeft = `4px solid ${c.hex}`;
        tag.innerHTML = `${c.name} <button type="button" data-idx="${idx}" title="Remover cor">&times;</button>`;
        selectedColorTags.appendChild(tag);
      });

      selectedColorTags.querySelectorAll('button').forEach(btn => {
        btn.addEventListener('click', (e) => {
          const i = Number(e.target.dataset.idx);
          const removed = selectedColors.splice(i, 1)[0];
          renderColorTags();
          if (removed && addPaletteColors) {
            const dot = addPaletteColors.querySelector(`[data-color-id="${removed.id}"]`);
            if (dot && !selectedColors.some(sc => sc.id === removed.id)) {
              dot.classList.remove('selected');
            }
          }
        });
      });
    }

    if (addPaletteColors) {
      addPaletteColors.querySelectorAll('.palette-dot').forEach(dot => {
        dot.addEventListener('click', () => {
          const cid = dot.dataset.colorId;
          const cname = dot.dataset.colorName;
          const chex = dot.dataset.colorHex;

          const existingIdx = selectedColors.findIndex(c => c.id === cid);
          if (existingIdx >= 0) {
            selectedColors.splice(existingIdx, 1);
            dot.classList.remove('selected');
          } else {
            selectedColors.push({ id: cid, name: cname, hex: chex });
            dot.classList.add('selected');
          }
          renderColorTags();
        });
      });
    }

    if (addSizesGrid) {
      addSizesGrid.querySelectorAll('.size-pill').forEach(pill => {
        pill.addEventListener('click', () => {
          const sizeVal = pill.dataset.size;
          if (selectedSizes.has(sizeVal)) {
            selectedSizes.delete(sizeVal);
            pill.classList.remove('active');
          } else {
            selectedSizes.add(sizeVal);
            pill.classList.add('active');
          }
        });
      });
    }

    addForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const saveBtn = document.getElementById('saveAddProductBtn');
      if (saveBtn) {
        saveBtn.disabled = true;
        saveBtn.innerHTML = 'Salvando...';
      }

      const formData = new FormData(addForm);
      formData.set('sizes', JSON.stringify([...selectedSizes]));
      formData.set('colors', JSON.stringify(selectedColors));

      fetch('/api/store/products/add', {
        method: 'POST',
        body: formData
      })
      .then(res => res.json())
      .then(data => {
        if (saveBtn) {
          saveBtn.disabled = false;
          saveBtn.innerHTML = '<i data-lucide="plus-circle"></i> Cadastrar Produto';
          if (window.lucide) window.lucide.createIcons();
        }

        if (data.success && data.product) {
          const p = data.product;
          const cardArticle = document.createElement('article');
          cardArticle.className = `store-product-card ${p.is_hidden ? 'is-product-hidden' : ''}`;
          cardArticle.dataset.id = p.id;
          cardArticle.dataset.sport = p.sport;
          cardArticle.dataset.category = p.category;
          cardArticle.dataset.price = p.price;
          cardArticle.dataset.name = p.name.toLowerCase();
          cardArticle.dataset.json = JSON.stringify(p);

          const sportLabelMap = { 'jiu-jitsu': 'Jiu-Jitsu', 'boxe': 'Boxe', 'muay-thai': 'Muay Thai', 'mma': 'MMA' };
          const sportName = sportLabelMap[p.sport] || p.sport;

          let swatchesHtml = '';
          if (p.colors && p.colors.length > 0) {
            swatchesHtml = `
              <div class="store-card-colors">
                <span class="store-colors-title">Cores:</span>
                <div class="store-swatches-row">
                  ${p.colors.map((col, idx) => `
                    <button type="button" class="store-swatch-dot ${idx === 0 ? 'active' : ''}"
                            style="background-color: ${col.hex};"
                            title="${col.name}"
                            data-color-id="${col.id}"
                            data-color-name="${col.name}"
                            data-color-hex="${col.hex}">
                    </button>
                  `).join('')}
                </div>
              </div>
            `;
          }

          let sizesHtml = '';
          if (p.sizes && p.sizes.length > 0) {
            sizesHtml = `
              <div class="store-product-sizes">
                <span class="store-sizes-title">Tamanhos:</span>
                <div class="store-sizes-pills">
                  ${p.sizes.map(s => `<span class="size-pill">${s}</span>`).join('')}
                </div>
              </div>
            `;
          }

          const imgHtml = p.image ? `<img src="/static/${p.image}" alt="${p.name}" class="store-product-img card-img-element" loading="lazy">` : `<span class="store-product-icon" aria-hidden="true">${p.icon || '🥋'}</span>`;

          cardArticle.innerHTML = `
            <div class="store-product-media store-media-${p.sport} ${p.is_sold_out ? 'is-sold-out' : ''}" data-open-modal="${p.id}">
              ${p.is_hidden ? '<span class="store-hidden-badge" title="Este produto está oculto para alunos e visitantes">👁️ OCULTO NO SITE</span>' : ''}
              ${p.is_sold_out ? `<div class="store-sold-out-ribbon"><span>⛔ ${p.out_of_stock_text || 'ESGOTADO • CHEGARÁ EM BREVE'} ⛔</span></div>` : ''}
              <button class="store-edit-card-btn" type="button" data-edit-product="${p.id}" title="Editar card do produto (Instrutor)">
                <i data-lucide="edit-3"></i> Editar
              </button>
              ${p.badge ? `<span class="store-product-badge card-badge-element">${p.badge}</span>` : ''}
              <span class="store-product-code">${p.id}</span>
              ${imgHtml}
              <button class="store-interest-btn" type="button" aria-label="Adicionar ${p.name} à lista de interesse" data-interest="${p.id}"><i data-lucide="heart"></i></button>
            </div>
            <div class="store-product-body">
              <div class="store-product-meta"><span>${sportName}</span><span>${p.category}</span></div>
              <h3 class="card-title-clickable" data-open-modal="${p.id}">${p.name}</h3>
              ${swatchesHtml}
              ${sizesHtml}
              <div class="store-product-footer">
                <div class="store-price">
                  ${p.stock_quantity !== null && p.stock_quantity !== undefined ? `<span class="store-stock-count card-stock-element"><i data-lucide="boxes"></i> Estoque: <strong>${p.stock_quantity}</strong> un.</span>` : ''}
                  <span class="card-price">R$ ${Number(p.price).toFixed(2).replace('.', ',')}</span>
                  ${p.old_price ? `<span class="store-old-price card-old-price">R$ ${Number(p.old_price).toFixed(2).replace('.', ',')}</span>` : ''}
                </div>
                <button class="store-card-action-btn" data-open-modal="${p.id}"><i data-lucide="shopping-cart"></i> Ver Detalhes</button>
              </div>
            </div>
          `;

          grid.prepend(cardArticle);
          cards.unshift(cardArticle);

          if (window.lucide) window.lucide.createIcons();

          closeAddModal();
          applyFilters();
          alert('Produto cadastrado com sucesso!');
        } else {
          alert(data.error || 'Erro ao cadastrar produto.');
        }
      })
      .catch(err => {
        console.error(err);
        if (saveBtn) {
          saveBtn.disabled = false;
          saveBtn.innerHTML = '<i data-lucide="plus-circle"></i> Cadastrar Produto';
          if (window.lucide) window.lucide.createIcons();
        }
        alert('Erro de conexão ao cadastrar produto.');
      });
    });
  }

  // -------------------------------------------------------------
  // 6. IMAGE OPTIMIZER & DIAGNOSTICS LOGIC
  // -------------------------------------------------------------
  const optimizerModal = document.getElementById('imageOptimizerModal');
  const openOptimizerBtn = document.getElementById('openImageOptimizerBtn');
  const closeOptimizerBtn = document.getElementById('closeImageOptimizerModalBtn');
  const reAnalyzeBtn = document.getElementById('reAnalyzeImagesBtn');
  const runOptimizeBtn = document.getElementById('runOptimizationBtn');
  const optimizerSearchInput = document.getElementById('optimizerSearch');
  const optimizerTableBody = document.getElementById('optimizerTableBody');

  let currentReportItems = [];
  let currentActiveTab = 'all';

  function getCsrfToken() {
    return document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') ||
           window.CSRF_TOKEN ||
           document.querySelector('input[name="csrf_token"]')?.value || '';
  }

  function openOptimizerModal() {
    if (!optimizerModal) return;
    optimizerModal.classList.remove('hidden');
    optimizerModal.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
    fetchImageAnalysis();
  }

  function closeOptimizerModal() {
    if (!optimizerModal) return;
    optimizerModal.classList.add('hidden');
    optimizerModal.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
  }

  if (openOptimizerBtn) openOptimizerBtn.addEventListener('click', openOptimizerModal);
  if (closeOptimizerBtn) closeOptimizerBtn.addEventListener('click', closeOptimizerModal);
  if (reAnalyzeBtn) reAnalyzeBtn.addEventListener('click', fetchImageAnalysis);

  if (optimizerModal) {
    optimizerModal.addEventListener('click', (e) => {
      if (e.target === optimizerModal) closeOptimizerModal();
    });
  }

  function fetchImageAnalysis() {
    if (!optimizerTableBody) return;

    if (openOptimizerBtn) {
      openOptimizerBtn.disabled = true;
      openOptimizerBtn.innerHTML = 'Analisando...';
    }
    if (reAnalyzeBtn) {
      reAnalyzeBtn.disabled = true;
      reAnalyzeBtn.textContent = 'Analisando...';
    }

    optimizerTableBody.innerHTML = '<tr><td colspan="7" class="text-center">🔍 Escaneando e analisando imagens do sistema via Pillow...</td></tr>';

    fetch('/api/admin/images/analyze', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRF-Token': getCsrfToken()
      }
    })
    .then(res => res.json())
    .then(data => {
      if (openOptimizerBtn) {
        openOptimizerBtn.disabled = false;
        openOptimizerBtn.innerHTML = '<i data-lucide="image"></i> Analisar Imagens';
        if (window.lucide) window.lucide.createIcons();
      }
      if (reAnalyzeBtn) {
        reAnalyzeBtn.disabled = false;
        reAnalyzeBtn.textContent = 'Analisar Novamente';
      }

      if (data.success && data.report) {
        const { summary, items } = data.report;
        currentReportItems = items || [];

        const kpiScanned = document.getElementById('kpiTotalScanned');
        const kpiWeight = document.getElementById('kpiTotalWeight');
        const kpiHeavy = document.getElementById('kpiHeavyCount');
        const kpiSavings = document.getElementById('kpiProjectedSavings');

        if (kpiScanned) kpiScanned.textContent = summary.total_scanned;
        if (kpiWeight) kpiWeight.textContent = summary.total_weight_mb + ' MB';
        if (kpiHeavy) kpiHeavy.textContent = summary.heavy_count;
        if (kpiSavings) kpiSavings.textContent = summary.projected_savings_mb + ' MB';

        renderOptimizerTable();
      } else {
        optimizerTableBody.innerHTML = `<tr><td colspan="7" class="text-center text-red-500">${data.error || 'Erro ao analisar imagens.'}</td></tr>`;
      }
    })
    .catch(err => {
      console.error(err);
      if (openOptimizerBtn) {
        openOptimizerBtn.disabled = false;
        openOptimizerBtn.innerHTML = '<i data-lucide="image"></i> Analisar Imagens';
      }
      if (reAnalyzeBtn) {
        reAnalyzeBtn.disabled = false;
        reAnalyzeBtn.textContent = 'Analisar Novamente';
      }
      optimizerTableBody.innerHTML = '<tr><td colspan="7" class="text-center text-red-500">Erro de conexão ao realizar auditoria de imagens.</td></tr>';
    });
  }

  function renderOptimizerTable() {
    if (!optimizerTableBody) return;

    const query = (optimizerSearchInput?.value || '').trim().toLowerCase();

    const filtered = currentReportItems.filter(item => {
      let matchesTab = true;
      if (currentActiveTab === 'Banners') matchesTab = item.category === 'Banners';
      else if (currentActiveTab === 'Produtos') matchesTab = item.category === 'Produtos';
      else if (currentActiveTab === 'pesada') matchesTab = item.status === 'pesada';
      else if (currentActiveTab === 'pendente') matchesTab = item.status === 'pendente' || item.status === 'pesada';

      const matchesSearch = !query || item.filename.toLowerCase().includes(query) || item.rel_path.toLowerCase().includes(query);

      return matchesTab && matchesSearch;
    });

    if (filtered.length === 0) {
      optimizerTableBody.innerHTML = '<tr><td colspan="7" class="text-center">Nenhuma imagem encontrada para os filtros selecionados.</td></tr>';
      return;
    }

    optimizerTableBody.innerHTML = filtered.map(item => {
      const imgUrl = `/static/${item.rel_path}`;
      const sizeStr = item.size_mb > 1 ? `${item.size_mb} MB` : `${item.size_kb} KB`;
      return `
        <tr>
          <td><img src="${imgUrl}" alt="${item.filename}" class="table-thumb" loading="lazy"></td>
          <td><strong>${item.filename}</strong><br><small class="text-muted">${item.rel_path}</small></td>
          <td>${item.category}</td>
          <td>${item.width} × ${item.height} px</td>
          <td><span class="font-mono text-xs">${item.format}</span></td>
          <td><strong>${sizeStr}</strong></td>
          <td>
            <span class="badge-status ${item.badge_color}">
              ${item.badge_color === 'green' ? '🟢' : item.badge_color === 'yellow' ? '🟡' : '🔴'} ${item.status_label}
            </span>
          </td>
        </tr>
      `;
    }).join('');
  }

  const tabsContainer = document.getElementById('optimizerTabs');
  if (tabsContainer) {
    tabsContainer.querySelectorAll('.tab-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        tabsContainer.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentActiveTab = btn.dataset.tab;
        renderOptimizerTable();
      });
    });
  }

  if (optimizerSearchInput) {
    optimizerSearchInput.addEventListener('input', renderOptimizerTable);
  }

  if (runOptimizeBtn) {
    runOptimizeBtn.addEventListener('click', () => {
      const selectedProfile = document.querySelector('input[name="compression_profile"]:checked')?.value || 'balanced';

      runOptimizeBtn.disabled = true;
      runOptimizeBtn.innerHTML = 'Otimizando...';

      fetch('/api/admin/images/optimize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRF-Token': getCsrfToken()
        },
        body: JSON.stringify({
          profile: selectedProfile
        })
      })
      .then(res => res.json())
      .then(data => {
        runOptimizeBtn.disabled = false;
        runOptimizeBtn.innerHTML = '<i data-lucide="zap"></i> Executar Otimização';
        if (window.lucide) window.lucide.createIcons();

        if (data.success) {
          alert(`🎉 Otimização concluída com sucesso!\n\nProcessadas: ${data.total_processed} imagens\nEconomia total obtida: ${data.total_saved_mb} MB`);
          fetchImageAnalysis();
        } else {
          alert(data.error || 'Erro ao otimizar imagens.');
        }
      })
      .catch(err => {
        console.error(err);
        runOptimizeBtn.disabled = false;
        runOptimizeBtn.innerHTML = '<i data-lucide="zap"></i> Executar Otimização';
        alert('Erro de conexão ao executar otimização.');
      });
    });
  }

  // Global Event Delegation for toolbar buttons to guarantee modal opening
  document.addEventListener('click', (e) => {
    const addBtn = e.target.closest('#openAddProductModalBtn');
    if (addBtn) {
      e.preventDefault();
      openAddModal();
    }
    const optBtn = e.target.closest('#openImageOptimizerBtn');
    if (optBtn) {
      e.preventDefault();
      openOptimizerModal();
    }
  });
})();




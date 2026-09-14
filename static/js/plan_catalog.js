(() => {
  const stateNode = document.getElementById('planCatalogState');
  if (!stateNode) return;
  const state = JSON.parse(stateNode.textContent);
  const createPanel = document.querySelector('[data-plan-create-panel]');
  const category = document.querySelector('[data-plan-create-category]');
  const createLabel = document.querySelector('[data-plan-create-button]');
  const selectTab = (tab, updateUrl = true) => {
    document.querySelectorAll('[data-plan-tab]').forEach(button => {
      const selected = button.dataset.planTab === tab;
      button.classList.toggle('is-active', selected);
      button.setAttribute('aria-pressed', String(selected));
    });
    document.querySelectorAll('[data-plan-panel]').forEach(panel => panel.classList.toggle('hidden', panel.dataset.planPanel !== tab));
    document.querySelectorAll('[data-plan-return-tab]').forEach(input => { input.value = tab; });
    if (category) category.value = tab === 'modalities' ? 'Planos Individuais' : 'Combos & Planos Especiais';
    if (createLabel) createLabel.textContent = tab === 'modalities' ? 'Novo plano individual' : 'Novo combo ou especial';
    if (updateUrl) {
      const url = new URL(location.href);
      url.searchParams.set('tab', 'plans');
      url.searchParams.set('plan_tab', tab);
      history.replaceState(null, '', url);
    }
  };
  document.querySelectorAll('[data-plan-tab]').forEach(button => button.addEventListener('click', () => selectTab(button.dataset.planTab)));
  const setCreateOpen = open => {
    createPanel.classList.toggle('hidden', !open);
    document.querySelectorAll('[data-plan-create-toggle]').forEach(button => button.setAttribute('aria-expanded', String(open)));
    if (open) createPanel.querySelector('input[name="name"]')?.focus();
    else document.querySelector('.plan-catalog-heading [data-plan-create-toggle]')?.focus();
  };
  document.querySelectorAll('[data-plan-create-toggle]').forEach(button => button.addEventListener('click', () => setCreateOpen(createPanel.classList.contains('hidden'))));
  const singleModality = selected => {
    if (category.value !== 'Planos Individuais') return;
    const checked = [...createPanel.querySelectorAll('input[name="modalities"]:checked')];
    checked.forEach(input => { input.checked = input === (selected || checked[0]); });
  };
  createPanel.querySelectorAll('input[name="modalities"]').forEach(input => input.addEventListener('change', () => singleModality(input.checked ? input : null)));
  category.addEventListener('change', () => {
    singleModality();
    createPanel.querySelector('[data-plan-return-tab]').value = category.value === 'Planos Individuais' ? 'modalities' : 'plans';
  });
  document.querySelectorAll('[data-plan-benefits-toggle]').forEach(button => button.addEventListener('click', () => {
    const row = document.querySelector(`[data-plan-benefits="${button.dataset.planBenefitsToggle}"]`);
    row.classList.toggle('hidden');
    const open = !row.classList.contains('hidden');
    button.classList.toggle('is-open', open);
    button.setAttribute('aria-expanded', String(open));
    if (open) row.querySelector('textarea')?.focus();
  }));
  selectTab(state.activeTab, false);
  if (state.formState) {
    const data = state.formState.data;
    const creating = data.action?.[0] === 'plan_create';
    const form = creating ? createPanel.querySelector('form') : document.getElementById(`plan-edit-${data.plan_id?.[0]}`);
    if (form) {
      if (creating) setCreateOpen(true);
      else document.querySelector(`[data-plan-benefits="${data.plan_id[0]}"]`)?.classList.remove('hidden');
      [...form.elements].forEach(field => {
        if (field.name === 'csrf_token') return;
        const values = data[field.name] || [];
        if (field.type === 'checkbox' || field.type === 'radio') field.checked = values.includes(field.value);
        else if (values.length) field.value = values[0];
      });
    }
    document.getElementById('planFormErrors')?.focus();
  }
})();

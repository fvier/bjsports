(() => {
  const section = document.getElementById('registrationClasses');
  if (!section) return;
  const plans = JSON.parse(document.getElementById('registrationSchedulePlans').textContent);
  const planSelect = document.getElementById('regPlan');
  const locationSelect = document.getElementById('registrationClassLocation');
  const periodSelect = document.getElementById('registrationClassPeriod');
  const filters = section.querySelector('[data-class-filters]');
  const status = section.querySelector('[data-class-status]');
  const results = section.querySelector('[data-class-results]');
  const refresh = section.querySelector('[data-class-refresh]');
  let classes = [], modalities = [], requestNumber = 0, controller;
  const node = (tag, text, className) => {
    const element = document.createElement(tag);
    element.textContent = text;
    if (className) element.className = className;
    return element;
  };

  function selectedModalities() {
    const plan = plans.find(item => item.value === planSelect.value);
    if (!plan || plan.value === '__private_class__') return [];
    const values = Number(plan.selection_count) > 0
      ? [...document.querySelectorAll('[data-combo-slot] select:not(:disabled)')].map(select => select.value)
      : plan.modalities || [];
    return [...new Set(values.filter(value => value && plan.modalities.includes(value)))];
  }

  function render() {
    results.replaceChildren();
    let visibleCount = 0;
    for (const modality of modalities) {
      const matches = classes.filter(group => group.modality === modality
        && (!locationSelect.value || group.location.slug === locationSelect.value)
        && (!periodSelect.value || group.schedules.some(schedule => schedule.period === periodSelect.value)));
      const list = document.createElement('details');
      list.className = 'registration-class-list';
      list.open = modalities.length === 1 && matches.length <= 2;
      list.append(node('summary', `${modality} · ${matches.length} turma${matches.length === 1 ? '' : 's'}`));
      if (!matches.length) list.append(node('p', 'Nenhuma turma publicada para esta modalidade e estes filtros. Consulte a academia.', 'registration-classes-note'));
      for (const group of matches) {
        const card = document.createElement('article');
        card.className = 'registration-class-card';
        card.dataset.classId = group.id;
        card.append(node('h4', group.name), node('p', `${group.location.name} · ${group.location.city}`),
          node('p', `${group.audience} · ${group.age_label}`), node('p', `Professor: ${group.instructor}`));
        const schedules = document.createElement('ul');
        for (const schedule of group.schedules.filter(item => !periodSelect.value || item.period === periodSelect.value)) {
          schedules.append(node('li', `${schedule.days} · ${schedule.time}`));
        }
        card.append(schedules);
        if (!group.schedules.length) card.append(node('p', 'Horários ainda não definidos. Consulte a academia.'));
        if (group.full) card.append(node('p', 'Turma lotada · consulte a academia', 'registration-class-full'));
        list.append(card);
      }
      results.append(list);
      visibleCount += matches.length;
    }
    status.textContent = `${visibleCount} turma${visibleCount === 1 ? '' : 's'} na consulta.`;
  }

  async function update() {
    controller?.abort();
    const current = ++requestNumber;
    modalities = selectedModalities();
    classes = [];
    results.replaceChildren();
    filters.classList.add('hidden');
    refresh.classList.add('hidden');
    locationSelect.replaceChildren(new Option('Todas as unidades', ''));
    periodSelect.value = '';
    const hasPlan = !!planSelect.value && planSelect.value !== '__private_class__';
    section.classList.toggle('hidden', !hasPlan);
    section.removeAttribute('aria-busy');
    if (!hasPlan) return;
    if (!modalities.length) {
      const plan = plans.find(item => item.value === planSelect.value);
      status.textContent = Number(plan?.selection_count) > 0
        ? 'Escolha as modalidades do combo para consultar suas turmas.'
        : 'Este plano não tem modalidades de turma definidas. Consulte a academia.';
      return;
    }
    status.textContent = 'Consultando horários…';
    section.setAttribute('aria-busy', 'true');
    controller = new AbortController();
    try {
      const response = await fetch(section.dataset.catalogUrl, {signal: controller.signal, cache: 'no-store'});
      if (!response.ok) throw new Error('Consulta indisponível');
      const data = await response.json();
      if (!Array.isArray(data.classes)) throw new Error('Grade inválida');
      if (current !== requestNumber) return;
      classes = data.classes.filter(group => modalities.includes(group.modality));
      const locations = new Map(classes.map(group => [group.location.slug, group.location]));
      for (const [slug, location] of locations) locationSelect.add(new Option(`${location.name} · ${location.city}`, slug));
      locationSelect.closest('label').classList.toggle('hidden', locations.size < 2);
      filters.classList.remove('hidden');
      render();
    } catch (error) {
      if (current !== requestNumber || error.name === 'AbortError') return;
      classes = [];
      results.replaceChildren();
      status.textContent = 'Não foi possível consultar os horários. Tente atualizar ou entre em contato com a academia.';
    } finally {
      if (current === requestNumber) {
        section.removeAttribute('aria-busy');
        refresh.classList.remove('hidden');
      }
    }
  }
  planSelect.addEventListener('change', update);
  document.querySelectorAll('[data-combo-slot] select').forEach(select => select.addEventListener('change', update));
  locationSelect.addEventListener('change', render);
  periodSelect.addEventListener('change', render);
  refresh.addEventListener('click', update);
  update();
})();

(() => {
  const section = document.getElementById('registrationClasses');
  if (!section) return;
  const plans = JSON.parse(document.getElementById('registrationSchedulePlans').textContent);
  const planSelect = document.getElementById('regPlan');
  const selectionField = document.getElementById('regClassSelection');
  const birthDate = document.getElementById('regBirthDate');
  const frequency = document.getElementById('regTrainingDays');
  const locationSelect = document.getElementById('registrationClassLocation');
  const periodSelect = document.getElementById('registrationClassPeriod');
  const filters = section.querySelector('[data-class-filters]');
  const status = section.querySelector('[data-class-status]');
  const announcement = section.querySelector('[data-class-announcement]');
  const results = section.querySelector('[data-class-results]');
  const summary = section.querySelector('[data-training-summary]');
  const refresh = section.querySelector('[data-class-refresh]');
  let classes = [], modalities = [], requestNumber = 0, controller, previousPlan = planSelect.value;
  let selected = new Set(), referenceDate = new Date().toISOString().slice(0, 10);
  try {
    const restored = JSON.parse(selectionField.value || '[]');
    if (Array.isArray(restored)) selected = new Set(restored.filter(Number.isInteger));
  } catch (_) { /* Discard an invalid draft, never guess a class. */ }
  const node = (tag, text, className) => {
    const element = document.createElement(tag);
    element.textContent = text;
    if (className) element.className = className;
    return element;
  };
  const currentPlan = () => plans.find(item => item.value === planSelect.value);
  const flexible = () => currentPlan()?.selection_mode === 'preference';
  function selectedModalities() {
    const plan = currentPlan();
    if (!plan || plan.value === '__private_class__') return [];
    const values = Number(plan.selection_count) > 0
      ? [...document.querySelectorAll('[data-combo-slot] select:not(:disabled)')].map(select => select.value)
      : plan.modalities || [];
    return [...new Set(values.filter(value => value && plan.modalities.includes(value)))];
  }
  function syncSelection() {
    selectionField.value = JSON.stringify([...selected].sort((a, b) => a - b));
    selectionField.dispatchEvent(new Event('input', {bubbles: true}));
  }
  function unavailableReason(group) {
    if (!group.schedules.length) return 'Horários ainda não definidos.';
    if (group.min_age != null || group.max_age != null) {
      if (!birthDate.value) return 'Informe a data de nascimento para conferir a faixa etária.';
      const [year, month, day] = referenceDate.split('-').map(Number);
      const [by, bm, bd] = birthDate.value.split('-').map(Number);
      const age = year - by - (month < bm || (month === bm && day < bd) ? 1 : 0);
      if ((group.min_age != null && age < group.min_age) || (group.max_age != null && age > group.max_age)) {
        return 'Fora da faixa etária configurada para o aluno.';
      }
    }
    if (!flexible()) {
      const allowed = {'ter-qui': ['Ter', 'Qui'], 'seg-qua-sex': ['Seg', 'Qua', 'Sex']}[frequency.value];
      if (allowed && !group.schedules.some(item => item.days.split(',').some(day => allowed.includes(day.trim())))) {
        return 'Os dias desta turma não estão incluídos no plano escolhido.';
      }
      if (group.full) return 'Sem vaga para matrícula nesta turma.';
    }
    return '';
  }
  function renderSummary() {
    summary.replaceChildren(node('h4', 'Resumo do treino'));
    const plan = currentPlan();
    if (!plan) return;
    const frequencyLabel = flexible()
      ? {'ter-qui': '2 aulas por semana', 'seg-qua-sex': '3 aulas por semana', 'todos': 'Ilimitado'}[frequency.value]
      : {'ter-qui': 'Ter e Qui', 'seg-qua-sex': 'Seg, Qua e Sex', 'todos': 'Todos os dias'}[frequency.value];
    summary.append(node('p', `${plan.label} · ${frequencyLabel || ''} · ${plan.prices?.[frequency.value] || 'Valor conforme plano'}`));
    for (const modality of modalities) {
      const chosen = classes.filter(group => selected.has(group.id) && group.modality === modality);
      summary.append(node('strong', modality));
      if (!chosen.length) summary.append(node('p', 'Escolha de turma pendente. Nenhuma vaga reservada.'));
      for (const group of chosen) {
        summary.append(node('p', `${flexible() ? 'Preferência' : 'Turma para matrícula'}: ${group.name} · ${group.location.name}`));
        summary.append(node('small', group.schedules.map(item => `${item.days} · ${item.time}`).join(' / ')));
      }
    }
    summary.append(node('p', flexible()
      ? 'Preferências não reservam vagas. Seus créditos continuam válidos nas outras aulas elegíveis da modalidade.'
      : 'A matrícula é confirmada ao concluir o cadastro, após validar a disponibilidade. Modalidades sem escolha ficam pendentes.', 'registration-classes-note'));
  }
  function reconcileSelection() {
    const before = selected.size;
    const usedModalities = new Set();
    for (const id of selected) {
      const group = classes.find(item => item.id === id && modalities.includes(item.modality));
      if (!group || unavailableReason(group) || (!flexible() && usedModalities.has(group.modality))) selected.delete(id);
      else usedModalities.add(group.modality);
    }
    if (selected.size !== before) announcement.textContent = 'Uma escolha ficou incompatível com o plano, a idade ou a disponibilidade e foi removida. Confira o resumo.';
    syncSelection();
  }
  function render() {
    const openLists = new Map([...results.querySelectorAll('.registration-class-list')]
      .map(list => [list.dataset.modality, list.open]));
    results.replaceChildren();
    section.querySelector('[data-class-rule]').textContent = flexible()
      ? 'Marque as turmas e horários de preferência. Você pode indicar mais de uma opção, sem reservar vagas.'
      : 'Escolha uma turma por modalidade para matrícula. A vaga será validada novamente ao concluir o cadastro.';
    let visibleCount = 0;
    for (const modality of modalities) {
      const matches = classes.filter(group => group.modality === modality
        && (!locationSelect.value || group.location.slug === locationSelect.value)
        && (!periodSelect.value || group.schedules.some(schedule => schedule.period === periodSelect.value)));
      const list = document.createElement('details');
      list.className = 'registration-class-list';
      list.dataset.modality = modality;
      list.open = openLists.get(modality) ?? ((modalities.length === 1 && matches.length <= 2) || matches.some(group => selected.has(group.id)));
      list.append(node('summary', `${modality} · ${matches.length} turma${matches.length === 1 ? '' : 's'}`));
      if (!matches.length) list.append(node('p', 'Nenhuma turma publicada para esta modalidade e estes filtros. Consulte a academia.', 'registration-classes-note'));
      for (const group of matches) {
        const card = node('article', '', 'registration-class-card');
        card.dataset.classId = group.id;
        card.classList.toggle('is-selected', selected.has(group.id));
        card.append(node('h4', group.name), node('p', `${group.location.name} · ${group.location.city}`),
          node('p', `${group.audience} · ${group.age_label}`), node('p', `Professor: ${group.instructor}`));
        const schedules = document.createElement('ul');
        for (const schedule of group.schedules.filter(item => !periodSelect.value || item.period === periodSelect.value)) schedules.append(node('li', `${schedule.days} · ${schedule.time}`));
        card.append(schedules);
        if (group.full) card.append(node('p', flexible() ? 'Turma lotada · preferência não garante vaga' : 'Turma lotada · consulte a academia', 'registration-class-full'));
        if (group.min_age == null && group.max_age == null) card.append(node('p', 'Confirme a adequação desta turma com a academia.', 'registration-classes-note'));
        const reason = unavailableReason(group);
        const label = node('label', '', 'registration-class-choice');
        const input = document.createElement('input');
        input.type = 'checkbox'; input.checked = selected.has(group.id); input.disabled = !!reason;
        input.dataset.selectClass = group.id;
        input.setAttribute('aria-label', `${flexible() ? 'Preferência' : 'Matricular em'} ${group.name}`);
        label.append(input, node('span', reason || (flexible() ? 'Adicionar às preferências' : 'Escolher esta turma')));
        input.addEventListener('change', () => {
          announcement.textContent = '';
          if (input.checked) {
            if (!flexible()) classes.filter(item => item.modality === group.modality).forEach(item => selected.delete(item.id));
            selected.add(group.id);
          } else selected.delete(group.id);
          syncSelection();
          render();
          section.querySelector(`[data-select-class="${group.id}"]`)?.focus({preventScroll: true});
        });
        card.append(label); list.append(card);
      }
      results.append(list); visibleCount += matches.length;
    }
    status.textContent = `${visibleCount} turma${visibleCount === 1 ? '' : 's'} na consulta.`;
    renderSummary();
  }
  async function update() {
    controller?.abort();
    const current = ++requestNumber;
    if (previousPlan !== planSelect.value) {
      if (selected.size) announcement.textContent = 'O plano mudou. Escolha novamente as turmas compatíveis.';
      selected.clear(); syncSelection(); previousPlan = planSelect.value;
    }
    modalities = selectedModalities();
    const previousLocation = locationSelect.value;
    results.replaceChildren(); summary.replaceChildren();
    filters.classList.add('hidden'); refresh.classList.add('hidden');
    locationSelect.replaceChildren(new Option('Todas as unidades', ''));
    const hasPlan = !!planSelect.value && planSelect.value !== '__private_class__';
    section.classList.toggle('hidden', !hasPlan); section.removeAttribute('aria-busy');
    if (!hasPlan || !modalities.length) {
      classes = []; selected.clear(); syncSelection();
      if (hasPlan) status.textContent = Number(currentPlan()?.selection_count) > 0
        ? 'Escolha as modalidades do combo para consultar suas turmas.'
        : 'Este plano não tem modalidades de turma definidas. Consulte a academia.';
      return;
    }
    status.textContent = 'Consultando horários…'; section.setAttribute('aria-busy', 'true');
    controller = new AbortController();
    try {
      const response = await fetch(section.dataset.catalogUrl, {signal: controller.signal, cache: 'no-store'});
      if (!response.ok) throw new Error('Consulta indisponível');
      const data = await response.json();
      if (!Array.isArray(data.classes)) throw new Error('Grade inválida');
      if (current !== requestNumber) return;
      referenceDate = data.reference_date || referenceDate;
      classes = data.classes.filter(group => modalities.includes(group.modality));
      const locations = new Map(classes.map(group => [group.location.slug, group.location]));
      for (const [slug, location] of locations) locationSelect.add(new Option(`${location.name} · ${location.city}`, slug));
      if (locations.has(previousLocation)) locationSelect.value = previousLocation;
      locationSelect.closest('label').classList.toggle('hidden', locations.size < 2);
      filters.classList.remove('hidden'); reconcileSelection(); render();
    } catch (error) {
      if (current !== requestNumber || error.name === 'AbortError') return;
      status.textContent = 'Não foi possível consultar os horários. Tente atualizar ou entre em contato com a academia.';
      // Keep the draft for retry; the server always validates the submitted IDs.
    } finally {
      if (current === requestNumber) { section.removeAttribute('aria-busy'); refresh.classList.remove('hidden'); }
    }
  }
  planSelect.addEventListener('change', () => {locationSelect.value = ''; periodSelect.value = ''; update();});
  document.querySelectorAll('[data-combo-slot] select').forEach(select => select.addEventListener('change', update));
  locationSelect.addEventListener('change', render); periodSelect.addEventListener('change', render);
  birthDate.addEventListener('change', () => {reconcileSelection(); render();});
  frequency.addEventListener('change', () => {reconcileSelection(); render();});
  refresh.addEventListener('click', update);
  update();
})();

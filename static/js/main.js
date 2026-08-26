// Initialize Lucide Icons
function initIcons() {
  if (window.lucide) {
    window.lucide.createIcons();
  }
}

function escapeHtml(value) {
  const element = document.createElement('span');
  element.textContent = String(value ?? '');
  return element.innerHTML;
}

function setupCsrfProtection() {
  const token = document.querySelector('meta[name="csrf-token"]')?.content;
  if (!token) return;
  document.querySelectorAll('form[method="POST"], form[method="post"]').forEach(form => {
    if (form.querySelector('input[name="csrf_token"]')) return;
    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = 'csrf_token';
    input.value = token;
    form.appendChild(input);
  });
}

function setupFlashMessages() {
  document.querySelectorAll('[data-flash-message]').forEach((message, index) => {
    const duration = Number(message.dataset.flashDuration) || 3000;
    const timerBar = message.querySelector('.flash-message-timer');
    if (timerBar) timerBar.style.animationDuration = `${duration}ms`;

    let dismissTimer;
    const dismiss = () => {
      window.clearTimeout(dismissTimer);
      if (message.classList.contains('is-leaving')) return;
      message.classList.add('is-leaving');
      window.setTimeout(() => {
        message.remove();
        const stack = document.querySelector('.flash-stack');
        if (stack && !stack.querySelector('[data-flash-message]')) stack.remove();
      }, 240);
    };

    message.querySelector('[data-flash-close]')?.addEventListener('click', dismiss);
    dismissTimer = window.setTimeout(dismiss, duration + (index * 120));
  });
}

function setupDueDateProrationPreview() {
  const form = document.querySelector('[data-due-date-form]');
  if (!form) return;
  const select = form.querySelector('[data-due-date-select]');
  const preview = form.querySelector('[data-due-date-proration]');
  const currentDay = Number(form.dataset.currentDueDate);
  const monthlyPrice = Number(form.dataset.monthlyPrice);
  if (!select || !preview || !currentDay || !Number.isFinite(monthlyPrice)) return;

  const updatePreview = () => {
    const newDay = Number(select.value);
    const extraDays = (newDay - currentDay + 30) % 30;
    const proportional = monthlyPrice * extraDays / 30;
    if (!extraDays) {
      preview.textContent = 'Esta já é sua data de vencimento. Nenhum valor será acrescentado.';
      return;
    }
    const formatted = proportional.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
    preview.innerHTML = `<strong>${extraDays} dia(s) proporcionais:</strong> ${formatted} serão adicionados à sua fatura aberta.`;
  };
  select.addEventListener('change', updatePreview);
  updatePreview();
}

// Schedule Data based on Mestre Bolivar's exact parameters
const scheduleData = {
  seg: [
    { name: 'Boxe Matinal', freq: '3x / semana (Seg, Qua, Sex)', time: '06:00h', price: 'R$ 90,00 /mês', tag: 'tag-boxe', tagLabel: 'Boxe' },
    { name: 'Muay Thai', freq: 'Segunda, Quarta e Sexta', time: '07:30h', price: 'Consulte-nos', tag: 'tag-muay', tagLabel: 'Muay Thai' },
    { name: 'MMA Profissional', freq: '3x / semana (Seg, Qua, Sex)', time: '11:30h', price: 'R$ 130,00 /mês', tag: 'tag-mma', tagLabel: 'MMA' },
    { name: 'Jiu-Jitsu Kids 2', freq: 'Segunda e Quarta', time: '16:00h', price: 'Consulte-nos', tag: 'tag-kids', tagLabel: 'Kids' },
    { name: 'Jiu-Jitsu Tarde', freq: '3x / semana (Seg, Qua, Sex)', time: '17:00h', price: 'R$ 100,00 /mês', tag: 'tag-bjj', tagLabel: 'Jiu-Jitsu' },
    { name: 'Muay Thai', freq: 'Segunda, Quarta e Sexta', time: '18:00h', price: 'Consulte-nos', tag: 'tag-muay', tagLabel: 'Muay Thai' },
    { name: 'Jiu-Jitsu Noturno', freq: '3x / semana (Seg, Qua, Sex)', time: '19:00h', price: 'R$ 100,00 /mês', tag: 'tag-bjj', tagLabel: 'Jiu-Jitsu' }
  ],
  ter: [
    { name: 'Jiu-Jitsu / Meio dia', freq: '2x / semana (Ter, Qui)', time: '12:00h', price: 'R$ 90,00 /mês', tag: 'tag-bjj', tagLabel: 'Jiu-Jitsu' },
    { name: 'Jiu-Jitsu Kids 1', freq: 'Terça e Quinta', time: '17:00h', price: 'Consulte-nos', tag: 'tag-kids', tagLabel: 'Kids' },
    { name: 'MMA Amador / Iniciantes', freq: '2x / semana (Ter, Qui)', time: '18:00h', price: 'R$ 130,00 /mês', tag: 'tag-mma', tagLabel: 'MMA' },
    { name: 'Muay Thai Kids', freq: 'Terça e Quinta', time: '18:00h', price: 'Consulte-nos', tag: 'tag-muay', tagLabel: 'Muay Thai' },
    { name: 'Jiu-Jitsu NoGi', freq: '2x / semana (Ter, Qui)', time: '19:00h', price: 'R$ 90,00 /mês', tag: 'tag-bjj', tagLabel: 'Jiu-Jitsu NoGi' },
    { name: 'Boxe Noturno', freq: '2x / semana (Ter, Qui)', time: '19:00h', price: 'R$ 90,00 /mês', tag: 'tag-boxe', tagLabel: 'Boxe' },
    { name: 'Muay Thai', freq: 'Terça e Quinta', time: '20:00h', price: 'Consulte-nos', tag: 'tag-muay', tagLabel: 'Muay Thai' }
  ],
  todos: [
    { name: 'Plano Passe Livre (BJJ & Boxe)', freq: 'Diário (Livre Acesso)', time: 'Todos os Horários', price: 'R$ 120,00 /mês', tag: 'tag-func', tagLabel: 'Livre Acesso' },
    { name: '⚡ Plano Combo + 1 (2 Modalidades)', freq: 'Pratique 2 modalidades à escolha', time: 'Horários Combinados', price: 'R$ 150,00 /mês', tag: 'tag-bjj', tagLabel: 'Combo + 1' },
    { name: '🔥 Plano Combo + 2 (3 Modalidades)', freq: 'Pratique 3 modalidades à escolha', time: 'Horários Combinados', price: 'R$ 180,00 /mês', tag: 'tag-mma', tagLabel: 'Combo + 2' },
    { name: 'Plano Casal (2 pessoas)', freq: 'Livre Escolha', time: 'Todos os Horários', price: 'R$ 190,00 /mês', tag: 'tag-boxe', tagLabel: 'Casal' },
    { name: 'Plano Família (3 pessoas)', freq: 'Livre Escolha', time: 'Todos os Horários', price: 'R$ 280,00 /mês', tag: 'tag-bjj', tagLabel: 'Família' }
  ]
};

let scheduleCapacity = [];
let activeScheduleDay = 'seg';

async function loadScheduleCapacity() {
  if (!document.getElementById('scheduleTableBody')) return;
  try {
    const response = await fetch('/api/bookings/availability', {headers: {'Accept': 'application/json'}});
    if (!response.ok) return;
    scheduleCapacity = (await response.json()).classes || [];
    renderSchedule(activeScheduleDay);
  } catch (error) {
    // Mantém a grade visível quando a consulta de capacidade estiver temporariamente indisponível.
  }
}

function getScheduleCapacity(item) {
  const time = String(item.time || '').replace('h', '');
  return scheduleCapacity.find(entry => entry.name === item.name && entry.class_time === time);
}

function renderScheduleStatus(item) {
  const capacity = getScheduleCapacity(item);
  if (!capacity) return '<span class="schedule-status"><i></i> Disponível</span>';
  if (capacity.status === 'esgotado') {
    return '<span class="schedule-status is-sold-out"><i></i> Esgotado</span>';
  }
  if (capacity.status === 'esgotando') {
    return `<span class="schedule-status is-running-out"><i></i> Esgotando • ${capacity.remaining} vaga(s)</span>`;
  }
  return `<span class="schedule-status"><i></i> Disponível • ${capacity.remaining} vaga(s)</span>`;
}

// Render Schedule Table
function renderSchedule(day = 'seg') {
  const tbody = document.getElementById('scheduleTableBody');
  if (!tbody) return;
  activeScheduleDay = day;

  const rows = (day === 'hoje' ? getTodayScheduleRows() : (scheduleData[day] || []))
    .slice()
    .sort((first, second) => getScheduleTimeInMinutes(first.time) - getScheduleTimeInMinutes(second.time));
  if (rows.length === 0) {
    const message = day === 'hoje'
      ? 'Não há aulas programadas para hoje.'
      : 'Nenhum treino listado.';
    tbody.innerHTML = `<tr><td colspan="6" class="text-center schedule-empty-state">${message}</td></tr>`;
    return;
  }

  tbody.innerHTML = rows.map(item => `
    <tr class="schedule-flight-row">
      <td class="schedule-time-cell"><strong>${item.time}</strong></td>
      <td class="schedule-class-cell">
        <span class="schedule-class-code ${item.tag}">${getScheduleCode(item.name)}</span>
        <span class="schedule-class-name">
          <strong>${item.name}</strong>
          <small>${getScheduleAudience(item.name)}</small>
        </span>
      </td>
      <td class="schedule-days-cell">${getNextClassDisplay(item)}</td>
      <td><span class="price-highlight">${item.price}</span></td>
      <td>${renderScheduleStatus(item)}</td>
      <td class="schedule-action-cell">
        <button class="btn btn-secondary btn-sm quick-book-btn" data-modality="${item.name}">
          <i data-lucide="log-in"></i> Check-in
        </button>
      </td>
    </tr>
  `).join('');

  tbody.querySelectorAll('.quick-book-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const modality = btn.getAttribute('data-modality');
      openModalWithModality(modality);
    });
  });
  initIcons();
}

function getScheduleTimeInMinutes(timeLabel) {
  const match = String(timeLabel).match(/(\d{1,2}):(\d{2})/);
  return match ? Number(match[1]) * 60 + Number(match[2]) : Number.MAX_SAFE_INTEGER;
}

const abbreviatedDayNames = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'];

function getRecurringDays(item) {
  if (Array.isArray(item.days)) return item.days;
  const frequency = String(item.freq || '').toLowerCase();
  if (frequency.includes('seg') && frequency.includes('qua') && frequency.includes('sex')) return [1, 3, 5];
  if (frequency.includes('seg') && frequency.includes('qua')) return [1, 3];
  if (frequency.includes('ter') && frequency.includes('qui')) return [2, 4];
  if (frequency.includes('diário') || frequency.includes('livre')) return [0, 1, 2, 3, 4, 5, 6];
  return [];
}

function formatTimeUntil(milliseconds) {
  const totalMinutes = Math.max(1, Math.ceil(milliseconds / 60000));
  const days = Math.floor(totalMinutes / 1440);
  const hours = Math.floor((totalMinutes % 1440) / 60);
  const minutes = totalMinutes % 60;
  const parts = [];
  if (days) parts.push(`${days}d`);
  if (hours) parts.push(`${hours}h`);
  if (minutes && !days) parts.push(`${minutes}min`);
  return parts.join(' ') || 'menos de 1 min';
}

function getNextClassDisplay(item) {
  const recurringDays = getRecurringDays(item);
  const recurringLabel = recurringDays.length === 7
    ? 'Todos os dias'
    : recurringDays.map(day => abbreviatedDayNames[day]).join(', ');
  const classMinutes = getScheduleTimeInMinutes(item.time);

  if (!recurringDays.length || classMinutes === Number.MAX_SAFE_INTEGER) {
    return `<strong class="schedule-next-class">Acesso livre</strong><br><small class="schedule-recurring-days">(${recurringLabel || 'Consulte a grade'})</small>`;
  }

  const now = new Date();
  let nextClass = null;
  for (let offset = 0; offset <= 7; offset += 1) {
    const candidate = new Date(now);
    candidate.setDate(now.getDate() + offset);
    if (!recurringDays.includes(candidate.getDay())) continue;
    candidate.setHours(Math.floor(classMinutes / 60), classMinutes % 60, 0, 0);
    if (candidate > now) {
      nextClass = candidate;
      break;
    }
  }

  if (!nextClass) return `<strong class="schedule-next-class">Próxima turma</strong><br><small class="schedule-recurring-days">(${recurringLabel})</small>`;
  const dayLabel = nextClass.toDateString() === now.toDateString()
    ? 'Hoje'
    : abbreviatedDayNames[nextClass.getDay()];
  const timeUntil = formatTimeUntil(nextClass.getTime() - now.getTime());
  return `<strong class="schedule-next-class">${dayLabel} — em ${timeUntil}</strong><br><small class="schedule-recurring-days">(${recurringLabel})</small>`;
}

function getScheduleCode(name) {
  const normalized = name.toLowerCase();
  if (normalized.includes('mma profissional')) return 'MMA-PRO';
  if (normalized.includes('mma')) return 'MMA';
  if (normalized.includes('jiu-jitsu kids 1')) return 'BJJ-K1';
  if (normalized.includes('jiu-jitsu kids 2')) return 'BJJ-K2';
  if (normalized.includes('jiu-jitsu')) return 'BJJ';
  if (normalized.includes('muay thai kids')) return 'MT-K';
  if (normalized.includes('muay thai')) return 'MT';
  if (normalized.includes('boxe')) return 'BOX';
  if (normalized.includes('família')) return 'FAM';
  if (normalized.includes('casal')) return 'CASAL';
  if (normalized.includes('passe livre')) return 'LIVRE';
  return 'BJS';
}

function getScheduleAudience(name) {
  const normalized = name.toLowerCase();
  if (normalized.includes('mma profissional')) return 'Profissional';
  if (normalized.includes('mma amador') || normalized.includes('iniciantes')) return 'Iniciantes';
  if (normalized.includes('kids')) return 'Infantil';
  if (normalized.includes('plano') || normalized.includes('família') || normalized.includes('casal')) return 'Plano especial';
  return 'Adulto';
}

function getTodayScheduleRows() {
  const today = new Date();
  let targetDate = new Date(today);
  let classes = getClassesForDay(targetDate.getDay());
  let daysAhead = 0;

  while (classes.length === 0 && daysAhead < 7) {
    daysAhead += 1;
    targetDate = new Date(today);
    targetDate.setDate(today.getDate() + daysAhead);
    classes = getClassesForDay(targetDate.getDay());
  }

  const availabilityLabel = daysAhead === 0
    ? 'Disponível hoje'
    : `Próxima: ${dayNamesBR[targetDate.getDay()]} (${formatDateBR(targetDate)})`;

  return classes.map(item => {
    const title = item.title.toLowerCase();
    const isMma = title.includes('mma');
    const isKids = title.includes('kids');
    const isMuay = title.includes('muay thai');
    const isBoxe = title.includes('boxe');
    const isJiuJitsu = title.includes('jiu-jitsu');
    return {
      name: item.title,
      freq: availabilityLabel,
      days: title.includes('kids 2') ? [1, 3] : ([1, 3, 5].includes(targetDate.getDay()) ? [1, 3, 5] : [2, 4]),
      time: item.time,
      price: isMma ? 'R$ 130,00 /mês' : (isMuay || isKids ? 'Consulte-nos' : (isBoxe ? 'R$ 90,00 /mês' : (isJiuJitsu ? 'R$ 100,00 /mês' : 'Consulte-nos'))),
      tag: isMma ? 'tag-mma' : (isMuay ? 'tag-muay' : (isKids ? 'tag-kids' : (isBoxe ? 'tag-boxe' : 'tag-bjj'))),
      tagLabel: isMma ? 'MMA' : (isMuay ? 'Muay Thai' : (isKids ? 'Kids' : (isBoxe ? 'Boxe' : 'Jiu-Jitsu')))
    };
  });
}

// Setup Schedule Filters
function setupScheduleFilters() {
  const filterBtns = document.querySelectorAll('.day-btn');
  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const day = btn.getAttribute('data-day');
      renderSchedule(day);
    });
  });
}

// Plan Select Buttons
function setupPlanButtons() {
  document.querySelectorAll('.select-plan-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const plan = btn.getAttribute('data-plan');
      openModalWithModality(plan);
    });
  });
}

// Dynamic 48h Schedule Generator Logic
function getClassesForDay(dayOfWeek) {
  if (dayOfWeek === 1 || dayOfWeek === 3) {
    return [
      { time: '06:00h', title: 'Boxe Matinal' },
      { time: '07:30h', title: 'Muay Thai' },
      { time: '11:30h', title: 'MMA Profissional' },
      { time: '16:00h', title: 'Jiu-Jitsu Kids 2' },
      { time: '17:00h', title: 'Jiu-Jitsu Tarde' },
      { time: '18:00h', title: 'Muay Thai' },
      { time: '19:00h', title: 'Jiu-Jitsu Noturno' }
    ];
  } else if (dayOfWeek === 5) {
    return [
      { time: '06:00h', title: 'Boxe Matinal' },
      { time: '07:30h', title: 'Muay Thai' },
      { time: '11:30h', title: 'MMA Profissional' },
      { time: '17:00h', title: 'Jiu-Jitsu Tarde' },
      { time: '18:00h', title: 'Muay Thai' },
      { time: '19:00h', title: 'Jiu-Jitsu Noturno' }
    ];
  } else if (dayOfWeek === 2 || dayOfWeek === 4) {
    return [
      { time: '12:00h', title: 'Jiu-Jitsu / Meio dia' },
      { time: '17:00h', title: 'Jiu-Jitsu Kids 1' },
      { time: '18:00h', title: 'MMA Amador / Iniciantes' },
      { time: '18:00h', title: 'Muay Thai Kids' },
      { time: '19:00h', title: 'Jiu-Jitsu / Boxe Noturno' },
      { time: '20:00h', title: 'Muay Thai' }
    ];
  }
  return [];
}

function formatDateBR(dateObj) {
  const day = String(dateObj.getDate()).padStart(2, '0');
  const month = String(dateObj.getMonth() + 1).padStart(2, '0');
  return `${day}/${month}`;
}

const dayNamesBR = ['Domingo', 'Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado'];

function populate48hScheduleOptions() {
  const select = document.getElementById('bookShift');
  const hint = document.getElementById('shift48hHint');
  if (!select) return;

  const now = new Date();
  const currentDay = now.getDay();
  const currentHour = now.getHours();

  let optionsHTML = '';

  if (currentDay === 6 || currentDay === 0) {
    const daysUntilMonday = (currentDay === 6) ? 2 : 1;
    const nextMonday = new Date(now);
    nextMonday.setDate(now.getDate() + daysUntilMonday);

    const formattedDate = formatDateBR(nextMonday);
    const classes = getClassesForDay(1);

    optionsHTML = classes.map(c => `
      <option value="Segunda-feira (${formattedDate}) — ${c.time} (${c.title})">
        Segunda-feira (${formattedDate}) — ${c.time} (${c.title})
      </option>
    `).join('');

    if (hint) {
      hint.textContent = `⚡ Fim de semana: Exibindo horários das aulas de Segunda-feira (${formattedDate}).`;
    }
  } else {
    const datesToEvaluate = [];
    datesToEvaluate.push({ date: new Date(now), isToday: true });
    const tomorrow = new Date(now);
    tomorrow.setDate(now.getDate() + 1);
    datesToEvaluate.push({ date: tomorrow, isToday: false });

    const availableOptions = [];

    datesToEvaluate.forEach(item => {
      const d = item.date;
      const dayW = d.getDay();
      if (dayW === 0 || dayW === 6) return;

      const dateStr = formatDateBR(d);
      const dayName = dayNamesBR[dayW];
      const classes = getClassesForDay(dayW);

      classes.forEach(c => {
        if (item.isToday) {
          const classHour = parseInt(c.time.split(':')[0], 10);
          if (currentHour >= classHour) return;
        }

        const label = `${dayName} (${dateStr}) — ${c.time} (${c.title})`;
        availableOptions.push(`<option value="${label}">${label}</option>`);
      });
    });

    if (availableOptions.length === 0) {
      const nextDay = new Date(now);
      nextDay.setDate(now.getDate() + (currentDay === 5 ? 3 : 1));
      const dateStr = formatDateBR(nextDay);
      const dayName = dayNamesBR[nextDay.getDay()];
      const classes = getClassesForDay(nextDay.getDay());

      optionsHTML = classes.map(c => `
        <option value="${dayName} (${dateStr}) — ${c.time} (${c.title})">
          ${dayName} (${dateStr}) — ${c.time} (${c.title})
        </option>
      `).join('');
    } else {
      optionsHTML = availableOptions.join('');
    }

    if (hint) {
      hint.textContent = `⏱️ Aulas disponíveis para agendamento nas próximas 48h.`;
    }
  }

  select.innerHTML = optionsHTML;
}

// Booking Modal Logic
let bookingAvailability = [];

async function loadBookingAvailability(preferredModality = '') {
  const modalitySelect = document.getElementById('bookModality');
  const shiftSelect = document.getElementById('bookShift');
  const hint = document.getElementById('shift48hHint');
  if (!modalitySelect || !shiftSelect) return;
  modalitySelect.replaceChildren(new Option('Carregando modalidades...', ''));
  shiftSelect.replaceChildren(new Option('Carregando aulas...', ''));
  shiftSelect.disabled = true;
  try {
    const response = await fetch('/api/bookings/availability', {headers: {'Accept': 'application/json'}});
    if (!response.ok) throw new Error('availability');
    bookingAvailability = (await response.json()).options || [];
    const modalities = [...new Set(bookingAvailability.map(item => item.modality))].sort((a, b) => a.localeCompare(b, 'pt-BR'));
    modalitySelect.replaceChildren(...modalities.map(item => new Option(item, item)));
    const related = modalities.find(item => preferredModality.toLowerCase().includes(item.toLowerCase())
      || item.toLowerCase().includes(preferredModality.toLowerCase()));
    if (related) modalitySelect.value = related;
    renderAvailableBookingClasses();
  } catch (error) {
    modalitySelect.replaceChildren(new Option('Indisponível', ''));
    shiftSelect.replaceChildren(new Option('Não foi possível consultar as vagas', ''));
    if (hint) hint.textContent = 'Não foi possível atualizar as vagas. Tente novamente.';
  }
}

function renderAvailableBookingClasses() {
  const modalitySelect = document.getElementById('bookModality');
  const shiftSelect = document.getElementById('bookShift');
  const hint = document.getElementById('shift48hHint');
  if (!modalitySelect || !shiftSelect) return;
  const options = bookingAvailability.filter(item => item.modality === modalitySelect.value);
  shiftSelect.replaceChildren(...options.map(item => {
    const option = new Option(`${item.label} — ${item.remaining} vaga(s)`, item.label);
    option.dataset.classGroupId = item.class_group_id;
    option.dataset.classDate = item.class_date;
    option.dataset.classTime = item.class_time;
    return option;
  }));
  if (!options.length) shiftSelect.add(new Option('Nenhuma aula com vaga disponível', ''));
  shiftSelect.disabled = !options.length;
  if (hint) hint.textContent = options.length
    ? 'Somente aulas com vaga aparecem nesta lista.'
    : 'Turmas lotadas não são exibidas. Consulte novamente mais tarde.';
}

function setupBookingModal() {
  const modal = document.getElementById('bookingModal');
  const openBtn = document.getElementById('openScheduleModal');
  const closeBtn = document.getElementById('closeBookingModal');
  const heroCTA = document.getElementById('heroCTA');
  const bookingForm = document.getElementById('bookingForm');
  const chkExperimental = document.getElementById('chkExperimental');
  const lblBookLogin = document.getElementById('lblBookLogin');
  const bookLoginInput = document.getElementById('bookLogin');
  const groupCpf3 = document.getElementById('groupCpf3');
  const bookCpf3Input = document.getElementById('bookCpf3');
  const bookingFeedback = document.getElementById('bookingFeedback');
  const bookingFeedbackTitle = document.getElementById('bookingFeedbackTitle');
  const bookingFeedbackMessage = document.getElementById('bookingFeedbackMessage');
  const bookingFeedbackAction = document.getElementById('bookingFeedbackAction');
  const closeBookingFeedback = document.getElementById('closeBookingFeedback');
  const modalitySelect = document.getElementById('bookModality');

  function hideBookingFeedback() {
    if (bookingFeedback) bookingFeedback.classList.add('hidden');
  }

  function showBookingFeedback(message, code) {
    if (!bookingFeedback) return;
    const isPaymentIssue = code === 'payment_required';
    bookingFeedback.classList.toggle('is-payment-warning', isPaymentIssue);
    bookingFeedback.classList.remove('is-success');
    bookingFeedbackTitle.textContent = isPaymentIssue ? 'Check-in temporariamente bloqueado' : 'Não foi possível fazer o check-in';
    bookingFeedbackMessage.textContent = message;
    bookingFeedbackAction?.classList.toggle('hidden', !isPaymentIssue);
    bookingFeedback.classList.remove('hidden');
    initIcons();
    bookingFeedback.scrollIntoView({behavior: 'smooth', block: 'nearest'});
  }

  closeBookingFeedback?.addEventListener('click', hideBookingFeedback);
  modalitySelect?.addEventListener('change', renderAvailableBookingClasses);

  if (modal) modal.classList.add('hidden');

  function openModal() {
    hideBookingFeedback();
    loadBookingAvailability();
    if (modal) modal.classList.remove('hidden');
  }

  function closeModal() {
    if (modal) modal.classList.add('hidden');
  }

  function toggleExperimentalMode() {
    if (chkExperimental && chkExperimental.checked) {
      if (lblBookLogin) lblBookLogin.textContent = 'Nome:';
      if (bookLoginInput) bookLoginInput.placeholder = 'Seu Nome Completo';
      if (groupCpf3) groupCpf3.classList.add('hidden');
      if (bookCpf3Input) {
        bookCpf3Input.removeAttribute('required');
        bookCpf3Input.value = '';
      }
    } else {
      if (lblBookLogin) lblBookLogin.textContent = 'Login:';
      if (bookLoginInput) bookLoginInput.placeholder = 'Bolivar';
      if (groupCpf3) groupCpf3.classList.remove('hidden');
      if (bookCpf3Input) bookCpf3Input.setAttribute('required', 'true');
    }
  }

  if (chkExperimental) {
    chkExperimental.addEventListener('change', toggleExperimentalMode);
  }

  if (openBtn) openBtn.addEventListener('click', openModal);
  if (heroCTA) heroCTA.addEventListener('click', openModal);
  if (closeBtn) closeBtn.addEventListener('click', closeModal);

  if (modal) {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) closeModal();
    });
  }

  if (bookingForm) {
    bookingForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const isExperimental = chkExperimental ? chkExperimental.checked : false;
      const loginOrName = document.getElementById('bookLogin').value;
      const cpf3 = bookCpf3Input ? bookCpf3Input.value : '';
      const modality = document.getElementById('bookModality').value;
      const shift = document.getElementById('bookShift').value;
      const selectedClass = document.getElementById('bookShift').selectedOptions[0];

      const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
      const response = await fetch('/api/bookings', {
        method: 'POST',
        headers: {'Content-Type': 'application/json', 'X-CSRF-Token': csrfToken},
        body: JSON.stringify({
          login_or_name: loginOrName, cpf3, modality, shift_time: shift,
          class_group_id: selectedClass?.dataset.classGroupId,
          class_date: selectedClass?.dataset.classDate,
          class_time: selectedClass?.dataset.classTime,
          is_experimental: isExperimental
        })
      });
      if (!response.ok) {
        const result = await response.json().catch(() => ({}));
        showBookingFeedback(
          result.error || 'Confira os dados informados e tente novamente.',
          result.code
        );
        return;
      }

      const result = await response.json();
      if (window.confetti) {
        window.confetti({ particleCount: 150, spread: 90, origin: { y: 0.5 } });
      }

      let msg = '';
      if (isExperimental) {
        msg += `*BJ SPORTS - AULA EXPERIMENTAL*\n`;
        msg += `*RESERVA CONFIRMADA*\n\n`;
        msg += `*Aluno:* ${loginOrName}\n`;
      } else {
        msg += `*BJ SPORTS - CHECK-IN*\n`;
        msg += `*RESERVA CONFIRMADA*\n\n`;
        msg += `*Aluno:* ${loginOrName}\n`;
        msg += `*CPF para conferência:* ${cpf3}...\n`;
      }
      msg += `*Modalidade:* ${modality}\n`;
      msg += `*Aula:* ${shift}\n`;
      msg += `*Status:* Vaga reservada pelo sistema\n\n`;
      msg += `*Local:* Av. Estrada do Amor, Cajazeiras-PB\n\n`;
      msg += `Esta mensagem confirma a reserva da aula selecionada.`;

      const encodedMsg = encodeURIComponent(msg);
      const waUrl = `https://wa.me/5583996527997?text=${encodedMsg}`;

      window.open(waUrl, '_blank');

      bookingForm.reset();
      toggleExperimentalMode();
      bookingFeedback?.classList.add('is-success');
      if (bookingFeedbackTitle) bookingFeedbackTitle.textContent = 'Reserva confirmada';
      if (bookingFeedbackMessage) bookingFeedbackMessage.textContent = `${result.message} Sua vaga está garantida na aula selecionada.`;
      bookingFeedbackAction?.classList.add('hidden');
      bookingFeedback?.classList.remove('hidden');
      await loadBookingAvailability();
      bookingFeedback?.scrollIntoView({behavior: 'smooth', block: 'nearest'});
    });
  }
}

function openModalWithModality(modalityName) {
  const modal = document.getElementById('bookingModal');
  const select = document.getElementById('bookModality');
  loadBookingAvailability(modalityName);
  if (modal) modal.classList.remove('hidden');
}

// Password Eye Toggle Handler
function setupPasswordEyeToggles() {
  document.querySelectorAll('.btn-toggle-eye').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const targetId = btn.getAttribute('data-target');
      const input = document.getElementById(targetId);
      if (!input) return;

      const isPassword = input.type === 'password';
      input.type = isPassword ? 'text' : 'password';

      const icon = btn.querySelector('i');
      if (icon) {
        if (isPassword) {
          icon.setAttribute('data-lucide', 'eye-off');
        } else {
          icon.setAttribute('data-lucide', 'eye');
        }
        initIcons();
      }
    });
  });
}

// Automatic CPF Mask Format (###.###.###-##)
function setupCpfMask() {
  const cpfInputs = [...document.querySelectorAll('#regCpf, [data-cpf-mask]')];
  cpfInputs.forEach(input => {
    input.setAttribute('inputmode', 'numeric');
    input.setAttribute('maxlength', '14');
    input.addEventListener('input', (e) => {
      let value = e.target.value.replace(/\D/g, '');
      if (value.length > 11) value = value.slice(0, 11);

      if (value.length > 9) {
        value = value.replace(/^(\d{3})(\d{3})(\d{3})(\d{1,2})$/, '$1.$2.$3-$4');
      } else if (value.length > 6) {
        value = value.replace(/^(\d{3})(\d{3})(\d{1,3})$/, '$1.$2.$3');
      } else if (value.length > 3) {
        value = value.replace(/^(\d{3})(\d{1,3})$/, '$1.$2');
      }
      e.target.value = value;
    });
  });
}

function setupRegistrationValidation() {
  if (document.body.dataset.registrationComplete === 'true') {
    try { sessionStorage.removeItem('bjSportsRegistrationDraft'); } catch (_) {}
  }
  const phone = document.getElementById('regPhoneNumber');
  phone?.addEventListener('input', () => {
    const digits = phone.value.replace(/\D/g, '').slice(0, 9);
    phone.value = digits.length > 5
      ? `${digits.slice(0, 1)} ${digits.slice(1, 5)} ${digits.slice(5)}`
      : (digits.length > 1 ? `${digits.slice(0, 1)} ${digits.slice(1)}` : digits);
  });

  const password = document.getElementById('regPass');
  const confirmation = document.getElementById('regPassConfirm');
  const rules = {
    length: value => value.length >= 8,
    number: value => /\d/.test(value),
    uppercase: value => /[A-Z]/.test(value),
    lowercase: value => /[a-z]/.test(value),
  };
  const validatePasswords = () => {
    if (!password || !confirmation) return;
    const states = Object.entries(rules).map(([name, validator]) => {
      const valid = validator(password.value);
      const item = document.querySelector(`[data-password-rule="${name}"]`);
      item?.classList.toggle('is-valid', valid);
      item?.classList.toggle('is-invalid', Boolean(password.value) && !valid);
      return valid;
    });
    password.setCustomValidity(states.every(Boolean) || !password.value
      ? '' : 'A senha ainda não cumpre todos os requisitos.');
    confirmation.setCustomValidity(!confirmation.value || confirmation.value === password.value
      ? '' : 'As senhas não coincidem.');
  };
  password?.addEventListener('input', validatePasswords);
  confirmation?.addEventListener('input', validatePasswords);
  validatePasswords();
}

// GPS Paraíba ERP Sidebar Toggle & Navigation Logic
function setupERPSidebar() {
  const sidebar = document.getElementById('erpSidebar');
  const hamburgerBtn = document.getElementById('erpHambergerBtn');
  const erpNavItems = document.querySelectorAll('.erp-nav-item[data-target-tab]');
  const tabContents = document.querySelectorAll('.member-tab-content');

  if (sidebar) {
    sidebar.querySelectorAll('.erp-nav-group').forEach((group, index) => {
      const title = group.querySelector(':scope > .erp-group-title');
      if (!title) return;

      const groupName = title.textContent.trim().toLowerCase();
      const categoryIcons = {
        aulas: 'calendar-days',
        financeiro: 'wallet-cards',
        'administração': 'shield-check',
        campeonatos: 'trophy',
        'integrações': 'plug-zap',
        'minha conta': 'circle-user-round'
      };
      const storageKey = `bjSportsSidebarGroup:${groupName}`;
      const controlledId = `erpNavGroup-${index}`;
      const categoryIcon = document.createElement('i');
      categoryIcon.setAttribute('data-lucide', categoryIcons[groupName] || 'folder');
      categoryIcon.className = 'erp-group-category-icon';
      categoryIcon.setAttribute('aria-hidden', 'true');
      const titleText = document.createElement('span');
      titleText.className = 'erp-group-title-text';
      titleText.textContent = groupName.toLocaleUpperCase('pt-BR');
      const icon = document.createElement('i');
      icon.setAttribute('data-lucide', 'chevron-down');
      icon.className = 'erp-group-toggle-icon';
      icon.setAttribute('aria-hidden', 'true');
      title.textContent = '';
      title.append(categoryIcon, titleText, icon);
      title.setAttribute('aria-label', titleText.textContent);
      title.setAttribute('role', 'button');
      title.setAttribute('tabindex', '0');
      title.setAttribute('aria-controls', controlledId);
      title.dataset.sidebarStorageKey = storageKey;
      group.id = controlledId;

      let isCollapsed = false;
      try {
        isCollapsed = localStorage.getItem(storageKey) === 'collapsed';
      } catch (_) {
        // O menu continua funcional mesmo quando o navegador bloqueia storage.
      }

      const updateGroup = (collapsed) => {
        group.classList.toggle('is-collapsed', collapsed);
        title.setAttribute('aria-expanded', String(!collapsed));
      };

      const toggleGroup = () => {
        const collapsed = !group.classList.contains('is-collapsed');
        updateGroup(collapsed);
        try {
          localStorage.setItem(storageKey, collapsed ? 'collapsed' : 'expanded');
        } catch (_) {
          // Sem persistência, o comportamento da sessão ainda é preservado.
        }
      };

      updateGroup(isCollapsed);
      title.addEventListener('click', toggleGroup);
      title.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault();
          toggleGroup();
        }
      });
    });
  }

  let sidebarOpenTimer = null;
  let sidebarCloseTimer = null;

  if (hamburgerBtn && sidebar) {
    hamburgerBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      if (sidebarOpenTimer) { clearTimeout(sidebarOpenTimer); sidebarOpenTimer = null; }
      if (sidebarCloseTimer) { clearTimeout(sidebarCloseTimer); sidebarCloseTimer = null; }
      sidebar.classList.toggle('collapsed');
    });
  }

  if (sidebar) {
    const supportsHover = window.matchMedia('(hover: hover) and (pointer: fine)');

    const expandSidebar = () => {
      if (sidebarCloseTimer) { clearTimeout(sidebarCloseTimer); sidebarCloseTimer = null; }
      sidebar.classList.remove('collapsed');
    };

    const collapseSidebar = () => {
      if (sidebarOpenTimer) { clearTimeout(sidebarOpenTimer); sidebarOpenTimer = null; }
      sidebar.classList.add('collapsed');

      sidebar.querySelectorAll('.erp-nav-group').forEach((group) => {
        const title = group.querySelector(':scope > .erp-group-title');
        group.classList.add('is-collapsed');
        if (title) {
          title.setAttribute('aria-expanded', 'false');
          try {
            localStorage.setItem(title.dataset.sidebarStorageKey, 'collapsed');
          } catch (_) {}
        }
      });
    };

    const requestOpenSidebar = () => {
      if (sidebarCloseTimer) { clearTimeout(sidebarCloseTimer); sidebarCloseTimer = null; }
      if (!sidebar.classList.contains('collapsed')) return;

      if (!sidebarOpenTimer) {
        sidebarOpenTimer = setTimeout(() => {
          expandSidebar();
          sidebarOpenTimer = null;
        }, 1500); // 1,5 segundos de mouse em cima para abrir
      }
    };

    const requestCloseSidebar = () => {
      if (sidebarOpenTimer) { clearTimeout(sidebarOpenTimer); sidebarOpenTimer = null; }

      if (sidebarCloseTimer) clearTimeout(sidebarCloseTimer);
      sidebarCloseTimer = setTimeout(() => {
        collapseSidebar();
        sidebarCloseTimer = null;
      }, 2000); // 2,0 segundos após se afastar para recolher obrigatoriamente
    };

    const enableAutomaticCollapse = () => {
      if (supportsHover.matches) {
        sidebar.classList.add('collapsed');
      } else {
        sidebar.classList.remove('collapsed');
      }
    };

    sidebar.addEventListener('mouseenter', () => {
      if (supportsHover.matches) {
        requestOpenSidebar();
      }
    });

    sidebar.addEventListener('mouseleave', () => {
      if (supportsHover.matches) {
        requestCloseSidebar();
      }
    });

    supportsHover.addEventListener('change', enableAutomaticCollapse);
    enableAutomaticCollapse();
  }

  erpNavItems.forEach(item => {
    item.addEventListener('click', (e) => {
      e.preventDefault();
      const targetId = item.getAttribute('data-target-tab');
      if (!targetId) return;

      erpNavItems.forEach(i => i.classList.remove('active'));
      item.classList.add('active');

      tabContents.forEach(content => {
        if (content.id === targetId) {
          content.classList.remove('hidden');
          content.classList.add('active');
        } else {
          content.classList.add('hidden');
          content.classList.remove('active');
        }
      });
    });
  });
}

function setupERPTopbar() {
  const topbar = document.querySelector('.erp-topbar');
  const actionsHost = topbar?.querySelector('.erp-topbar-right');
  if (!topbar || !actionsHost || actionsHost.querySelector('.erp-quick-actions')) return;

  const flashStack = document.querySelector('body.erp-page > .flash-stack');
  if (flashStack) {
    flashStack.classList.add('erp-flash-stack');
    topbar.insertAdjacentElement('afterend', flashStack);
  }

  const actions = document.createElement('nav');
  actions.className = 'erp-quick-actions';
  actions.setAttribute('aria-label', 'Ações rápidas');
  const contractPending = document.body.dataset.contractPending === 'true';
  const serverActions = actionsHost.querySelector('.topbar-actions-row');
  const trialBadge = serverActions?.querySelector('.student-trial-countdown-badge');
  const role = document.body.dataset.userRole;
  const pendingAttendanceCount = Number(document.body.dataset.pendingAttendanceCount || 0);
  const pendingPaymentsCount = Number(document.body.dataset.pendingPaymentsCount || 0);
  const statusAction = (href, icon, label, count, pendingLabel) => {
    const pending = count > 0;
    const status = pending ? `${count} ${pendingLabel}` : 'tudo em dia';
    return `<a class="topbar-action-square ${pending ? 'has-pending' : 'is-ok'}" href="${href}" title="${label} — ${status}" aria-label="${label} — ${status}"><i data-lucide="${icon}"></i>${pending ? '<span class="topbar-badge-icon">!</span>' : ''}</a>`;
  };
  const operationalActions = serverActions
    ? Array.from(serverActions.querySelectorAll('.topbar-action-square')).map(link => link.outerHTML).join('')
    : statusAction('/presencas.html', 'calendar-check', 'Registrar aula', pendingAttendanceCount, 'presença(s) pendente(s)')
      + (role === 'instrutor' ? statusAction('/mensalidades_admin.html', 'file-text', 'Dar baixa nas mensalidades', pendingPaymentsCount, 'pagamento(s) pendente(s)') : '');
  actions.innerHTML = `
    ${operationalActions}
    <a class="erp-topbar-icon" href="/configuracoes.html" title="Configurações"><i data-lucide="settings"></i></a>
    <a class="erp-topbar-icon" href="/" title="Ir para a landing page" aria-label="Ir para a landing page"><i data-lucide="house"></i></a>
  `;
  serverActions?.remove();
  actionsHost.prepend(actions);
  if (trialBadge) actionsHost.prepend(trialBadge);

  const avatar = actionsHost.querySelector('.erp-avatar');
  const userName = actionsHost.querySelector('.erp-user-name')?.textContent.trim() || 'Usuário';
  if (avatar) {
    avatar.textContent = userName.split(/\s+/).slice(0, 2).map(part => part[0]).join('').toUpperCase();
    avatar.setAttribute('title', userName);
  }
  const userBadge = actionsHost.querySelector('.erp-user-badge');
  if (userBadge && !userBadge.querySelector('.erp-account-menu')) {
    const beltNames = {branca: 'Faixa branca', azul: 'Faixa azul', roxa: 'Faixa roxa', marrom: 'Faixa marrom', preta: 'Faixa preta'};
    const beltColor = document.body.dataset.beltColor || 'branca';
    const beltDot = document.createElement('span');
    beltDot.className = `erp-belt-dot belt-${beltColor}`;
    beltDot.title = beltNames[beltColor] || 'Faixa no Jiu-Jitsu';

    const dropdownIcon = document.createElement('i');
    dropdownIcon.setAttribute('data-lucide', 'chevron-down');
    dropdownIcon.className = 'erp-account-chevron';
    userBadge.append(beltDot, dropdownIcon);
    userBadge.setAttribute('role', 'button');
    userBadge.setAttribute('tabindex', '0');
    userBadge.setAttribute('aria-haspopup', 'menu');
    userBadge.setAttribute('aria-expanded', 'false');

    const accountMenu = document.createElement('div');
    accountMenu.className = 'erp-account-menu';
    accountMenu.setAttribute('role', 'menu');
    accountMenu.innerHTML = `
      <div class="erp-account-summary"><strong></strong><small></small></div>
      <a href="/configuracoes.html" role="menuitem"><i data-lucide="user-round-cog"></i><span>Gerenciar informações</span></a>
      <a href="/minha-conta/contrato.html" role="menuitem" class="${contractPending ? 'is-pending' : ''}"><i data-lucide="file-signature"></i><span>Contrato${contractPending ? ' • Pendente' : ''}</span></a>
      <a href="/mensalidades_aluno.html" role="menuitem"><i data-lucide="wallet-cards"></i><span>Minhas mensalidades</span></a>
      <a href="/logout" role="menuitem" class="is-logout"><i data-lucide="log-out"></i><span>Sair da conta</span></a>
    `;
    accountMenu.querySelector('.erp-account-summary strong').textContent = userName;
    accountMenu.querySelector('.erp-account-summary small').textContent = beltNames[beltColor] || 'Jiu-Jitsu';
    userBadge.appendChild(accountMenu);

    const toggleAccountMenu = (force) => {
      const open = typeof force === 'boolean' ? force : !userBadge.classList.contains('is-open');
      userBadge.classList.toggle('is-open', open);
      userBadge.setAttribute('aria-expanded', String(open));
    };
    userBadge.addEventListener('click', (event) => {
      if (event.target.closest('.erp-account-menu a')) return;
      event.stopPropagation();
      toggleAccountMenu();
    });
    userBadge.addEventListener('keydown', (event) => {
      if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); toggleAccountMenu(); }
      if (event.key === 'Escape') toggleAccountMenu(false);
    });
    document.addEventListener('click', () => toggleAccountMenu(false));
  }

  try {
    if (localStorage.getItem('bjSportsTheme') === 'light') document.body.classList.add('erp-light-theme');
  } catch (_) {}

}

function setupPublicTheme() {
  const toggle = document.getElementById('publicThemeToggle');
  if (!toggle) return;

  const applyTheme = (light) => {
    document.body.classList.toggle('public-light-theme', light);
    toggle.setAttribute('aria-pressed', String(light));
    toggle.setAttribute('aria-label', light ? 'Ativar tema escuro' : 'Ativar tema claro');
    toggle.title = light ? 'Ativar tema escuro' : 'Ativar tema claro';
    const icon = toggle.querySelector('[data-lucide]');
    if (icon) icon.setAttribute('data-lucide', light ? 'moon' : 'sun');
    initIcons();
  };

  let light = false;
  try { light = localStorage.getItem('bjSportsTheme') === 'light'; } catch (_) {}
  applyTheme(light);

  toggle.addEventListener('click', () => {
    light = !document.body.classList.contains('public-light-theme');
    applyTheme(light);
    try { localStorage.setItem('bjSportsTheme', light ? 'light' : 'dark'); } catch (_) {}
  });
}

// Standalone Login & Member Portal Tabs
function setupPortalPage() {
  const tabLogin = document.getElementById('tabBtnLogin');
  const tabRegister = document.getElementById('tabBtnRegister');
  const formLogin = document.getElementById('portalLoginForm');
  const formRegister = document.getElementById('portalRegisterForm');
  const loginIntro = document.querySelector('[data-portal-login-intro]');
  const membershipContract = document.querySelector('[data-portal-membership-contract]');
  const planSelect = document.getElementById('regPlan');
  const dueDateSelect = document.getElementById('regDueDate');
  const contractPlan = document.querySelector('[data-contract-plan]');
  const contractDue = document.querySelector('[data-contract-due]');
  const imageConsentOptions = [...document.querySelectorAll('input[name="imageConsentScope"]')];
  const minorConsentFields = document.querySelector('[data-minor-consent-fields]');

  if (!tabLogin || !tabRegister) return;

  const updateContractSummary = () => {
    if (contractPlan && planSelect) contractPlan.textContent = planSelect.options[planSelect.selectedIndex]?.text || 'plano selecionado';
    if (contractDue && dueDateSelect) contractDue.textContent = dueDateSelect.value
      ? `dia ${dueDateSelect.value} de cada mês`
      : 'dia escolhido no cadastro';
  };

  const updateMinorConsentFields = () => {
    if (!minorConsentFields) return;
    const isMinorAuthorization = imageConsentOptions.some(option => option.checked && option.value === 'minor_guardian');
    minorConsentFields.classList.toggle('hidden', !isMinorAuthorization);
    minorConsentFields.querySelectorAll('input, select').forEach(field => {
      field.required = isMinorAuthorization;
      field.disabled = !isMinorAuthorization;
    });
  };

  const showLogin = () => {
    tabLogin.classList.add('active');
    tabRegister.classList.remove('active');
    if (formLogin) formLogin.classList.remove('hidden');
    if (formRegister) formRegister.classList.add('hidden');
    if (loginIntro) loginIntro.classList.remove('hidden');
    if (membershipContract) membershipContract.classList.add('hidden');
  };

  const showRegistration = () => {
    tabRegister.classList.add('active');
    tabLogin.classList.remove('active');
    if (formRegister) formRegister.classList.remove('hidden');
    if (formLogin) formLogin.classList.add('hidden');
    if (loginIntro) loginIntro.classList.add('hidden');
    if (membershipContract) membershipContract.classList.remove('hidden');
    updateContractSummary();
  };

  tabLogin.addEventListener('click', showLogin);
  tabRegister.addEventListener('click', showRegistration);
  planSelect?.addEventListener('change', updateContractSummary);
  dueDateSelect?.addEventListener('change', updateContractSummary);
  imageConsentOptions.forEach(option => option.addEventListener('change', updateMinorConsentFields));
  updateMinorConsentFields();
  if (new URLSearchParams(window.location.search).get('mode') === 'register') showRegistration();
}

// Global Keydown Listener for Escape key
function setupGlobalKeyListeners() {
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      const bookingModal = document.getElementById('bookingModal');
      if (bookingModal) bookingModal.classList.add('hidden');
    }
  });
}

function setupAttendanceRejectionConfirmation() {
  const forms = document.querySelectorAll('[data-confirm-rejection]');
  if (!forms.length) return;

  let activeNotice = null;
  const closeNotice = () => {
    if (!activeNotice) return;
    activeNotice.classList.add('is-leaving');
    const notice = activeNotice;
    activeNotice = null;
    window.setTimeout(() => notice.remove(), 180);
  };

  forms.forEach(form => {
    form.addEventListener('submit', event => {
      event.preventDefault();
      closeNotice();

      const studentName = form.dataset.studentName || 'este aluno';
      const notice = document.createElement('div');
      notice.className = 'attendance-confirm-toast';
      notice.setAttribute('role', 'alertdialog');
      notice.setAttribute('aria-modal', 'false');
      notice.setAttribute('aria-label', 'Confirmar recusa da presença');
      notice.innerHTML = `
        <span class="attendance-confirm-icon"><i data-lucide="user-x"></i></span>
        <div class="attendance-confirm-copy">
          <strong>Negar esta presença?</strong>
          <small>O check-in de ${escapeHtml(studentName)} não será contabilizado.</small>
          <div class="attendance-confirm-actions">
            <button type="button" data-rejection-cancel>Cancelar</button>
            <button type="button" class="is-danger" data-rejection-confirm>Negar presença</button>
          </div>
        </div>
      `;
      document.body.appendChild(notice);
      activeNotice = notice;
      initIcons();

      notice.querySelector('[data-rejection-cancel]')?.addEventListener('click', closeNotice);
      const confirmButton = notice.querySelector('[data-rejection-confirm]');
      confirmButton?.addEventListener('click', () => {
        confirmButton.disabled = true;
        confirmButton.textContent = 'Processando...';
        form.submit();
      });
      confirmButton?.focus();
    });
  });

  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && activeNotice) closeNotice();
  });
}

function setupClassManagementPreview() {
  const modal = document.querySelector('[data-class-modal]');
  if (!modal) return;

  const form = modal.querySelector('.class-editor-form');
  const title = modal.querySelector('[data-class-modal-title]');
  const actionInput = form?.elements.action;
  const idInput = form?.elements.class_id;
  const nameInput = form?.elements.class_name;
  const modalityInput = form?.elements.class_modality;
  const audienceInput = form?.elements.class_audience;
  const scheduleInput = form?.elements.class_schedule;
  const instructorInput = form?.elements.class_instructor;
  const responsibleMonitorInput = form?.elements.responsible_monitor_id;
  const capacityInput = form?.elements.class_capacity;
  const durationInput = form?.elements.class_duration;
  const statusInput = form?.elements.class_status;
  const publishedInput = form?.elements.publish_public;

  const closeModal = () => {
    modal.classList.add('hidden');
    document.body.style.overflow = '';
  };

  document.querySelectorAll('[data-class-modal-open]').forEach(button => {
    button.addEventListener('click', () => {
      const editing = Boolean(button.dataset.className);
      if (form) form.reset();
      if (title) title.textContent = editing ? `Editar ${button.dataset.className}` : 'Nova turma';
      if (actionInput) actionInput.value = editing ? 'update' : 'create';
      if (idInput) idInput.value = button.dataset.classId || '';
      if (nameInput) nameInput.value = button.dataset.className || '';
      if (modalityInput && button.dataset.classModality) modalityInput.value = button.dataset.classModality;
      if (audienceInput && button.dataset.classAudience) audienceInput.value = button.dataset.classAudience;
      if (scheduleInput) scheduleInput.value = button.dataset.classSchedule || '';
      if (instructorInput) instructorInput.value = button.dataset.classInstructor || 'Mestre Bolivar';
      if (responsibleMonitorInput) responsibleMonitorInput.value = button.dataset.responsibleMonitorId || '';
      if (capacityInput) capacityInput.value = button.dataset.classCapacity || '20';
      if (durationInput) durationInput.value = button.dataset.classDuration || '60';
      if (statusInput) statusInput.value = button.dataset.classStatus || 'ativa';
      const locationInput = form ? form.querySelector('[name="class_location_slug"]') : null;
      if (locationInput) locationInput.value = button.dataset.classLocationSlug || 'cajazeiras-sede';
      if (publishedInput) publishedInput.checked = button.dataset.classPublished !== '0';
      modal.classList.remove('hidden');
      document.body.style.overflow = 'hidden';
      window.setTimeout(() => nameInput?.focus(), 30);
    });
  });

  modal.querySelectorAll('[data-class-modal-close]').forEach(button => {
    button.addEventListener('click', closeModal);
  });
  modal.addEventListener('click', event => {
    if (event.target === modal) closeModal();
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && !modal.classList.contains('hidden')) closeModal();
  });
}

function setupSpecialClassEventModal() {
  const modal = document.querySelector('[data-special-event-modal]');
  const openButton = document.querySelector('[data-special-event-open]');
  if (!modal || !openButton) return;

  const firstInput = modal.querySelector('input[name="title"]');
  const closeModal = () => {
    modal.classList.add('hidden');
    document.body.style.overflow = '';
  };
  const openModal = () => {
    modal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
    window.setTimeout(() => firstInput?.focus(), 30);
  };

  openButton.addEventListener('click', openModal);
  modal.querySelectorAll('[data-special-event-close]').forEach(button => {
    button.addEventListener('click', closeModal);
  });
  modal.addEventListener('click', event => {
    if (event.target === modal) closeModal();
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && !modal.classList.contains('hidden')) closeModal();
  });
}

function urlBase64ToUint8Array(value) {
  const padding = '='.repeat((4 - (value.length % 4)) % 4);
  const base64 = (value + padding).replace(/-/g, '+').replace(/_/g, '/');
  const raw = window.atob(base64);
  return Uint8Array.from([...raw].map(character => character.charCodeAt(0)));
}

function setupCalendarSyncModal() {
  const modal = document.querySelector('[data-calendar-sync-modal]');
  const openButton = document.querySelector('[data-calendar-sync-open]');
  if (!modal || !openButton) return;

  const content = modal.querySelector('.calendar-sync-content');
  const feedback = modal.querySelector('[data-calendar-sync-feedback]');
  const pushButton = modal.querySelector('[data-push-toggle]');
  const testButton = modal.querySelector('[data-push-test]');
  const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content || '';
  let pushEnabled = content?.dataset.pushEnabled === 'true';

  const showFeedback = (message, isError = false) => {
    if (!feedback) return;
    feedback.textContent = message;
    feedback.classList.toggle('is-error', isError);
    feedback.classList.remove('hidden');
  };
  const closeModal = () => {
    modal.classList.add('hidden');
    document.body.style.overflow = '';
  };
  openButton.addEventListener('click', () => {
    modal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
  });
  modal.querySelectorAll('[data-calendar-sync-close]').forEach(button => button.addEventListener('click', closeModal));
  modal.addEventListener('click', event => {
    if (event.target === modal) closeModal();
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && !modal.classList.contains('hidden')) closeModal();
  });

  pushButton?.addEventListener('click', async () => {
    pushButton.disabled = true;
    try {
      const registration = await navigator.serviceWorker.register('/static/js/calendar-sw.js');
      if (pushEnabled) {
        const currentSubscription = await registration.pushManager.getSubscription();
        await fetch('/api/calendario/push', {
          method: 'DELETE', headers: {'Content-Type': 'application/json', 'X-CSRF-Token': csrfToken},
          body: JSON.stringify({endpoint: currentSubscription?.endpoint || ''})
        });
        await currentSubscription?.unsubscribe();
        showFeedback('Notificações desativadas neste navegador.');
        window.setTimeout(() => window.location.reload(), 700);
        return;
      }
      if (!('Notification' in window) || !('PushManager' in window)) throw new Error('Este navegador não oferece suporte a notificações push.');
      const permission = await Notification.requestPermission();
      if (permission !== 'granted') throw new Error('A permissão de notificação não foi concedida.');
      const subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(content.dataset.vapidPublicKey)
      });
      const response = await fetch('/api/calendario/push', {
        method: 'POST', headers: {'Content-Type': 'application/json', 'X-CSRF-Token': csrfToken},
        body: JSON.stringify(subscription.toJSON())
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.error || 'Não foi possível ativar o push.');
      pushEnabled = true;
      showFeedback('Push ativado. Enviando uma notificação de teste…');
      const testResponse = await fetch('/api/calendario/push/teste', {
        method: 'POST', headers: {'Content-Type': 'application/json', 'X-CSRF-Token': csrfToken}, body: '{}'
      });
      const testResult = await testResponse.json();
      if (!testResponse.ok) throw new Error(testResult.error || 'Push ativo, mas o teste falhou.');
      window.setTimeout(() => window.location.reload(), 1000);
    } catch (error) {
      showFeedback(error.message || 'Não foi possível alterar as notificações.', true);
      pushButton.disabled = false;
    }
  });

  testButton?.addEventListener('click', async () => {
    testButton.disabled = true;
    try {
      const response = await fetch('/api/calendario/push/teste', {
        method: 'POST', headers: {'Content-Type': 'application/json', 'X-CSRF-Token': csrfToken}, body: '{}'
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.error || 'Falha no teste.');
      showFeedback('Notificação de teste enviada.');
    } catch (error) {
      showFeedback(error.message, true);
    } finally {
      testButton.disabled = false;
    }
  });
}

function setupChampionshipCreateModal() {
  const modal = document.querySelector('[data-championship-create-modal]');
  const openButton = document.querySelector('[data-championship-create-open]');
  if (!modal || !openButton) return;
  const firstInput = modal.querySelector('input[name="name"]');
  const closeModal = () => {
    modal.classList.add('hidden');
    document.body.style.overflow = '';
  };
  openButton.addEventListener('click', () => {
    modal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
    window.setTimeout(() => firstInput?.focus(), 30);
  });
  modal.querySelectorAll('[data-championship-create-close]').forEach(button => button.addEventListener('click', closeModal));
  modal.addEventListener('click', event => {
    if (event.target === modal) closeModal();
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && !modal.classList.contains('hidden')) closeModal();
  });
}

function setupChampionshipWeightTabs() {
  const tabsRoot = document.querySelector('[data-weight-tabs]');
  if (!tabsRoot) return;
  const tabs = [...tabsRoot.querySelectorAll('[data-weight-tab]')];
  const panels = [...tabsRoot.querySelectorAll('[data-weight-panel]')];
  const available = tabs.map(tab => tab.dataset.weightTab);
  let savedGender = 'masculino';
  try {
    savedGender = window.localStorage.getItem('bj-sports-weight-tab') || savedGender;
  } catch (_error) {
    // A tabela continua funcional mesmo quando o navegador bloqueia o armazenamento local.
  }

  const activateTab = (gender, moveFocus = false) => {
    if (!available.includes(gender)) gender = 'masculino';
    tabs.forEach(tab => {
      const isActive = tab.dataset.weightTab === gender;
      tab.classList.toggle('active', isActive);
      tab.setAttribute('aria-selected', String(isActive));
      tab.tabIndex = isActive ? 0 : -1;
      if (isActive && moveFocus) tab.focus();
    });
    panels.forEach(panel => {
      const isActive = panel.dataset.weightPanel === gender;
      panel.classList.toggle('active', isActive);
      panel.hidden = !isActive;
    });
    try {
      window.localStorage.setItem('bj-sports-weight-tab', gender);
    } catch (_error) {
      // Sem persistência, a navegação entre as abas ainda funciona normalmente.
    }
  };

  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => activateTab(tab.dataset.weightTab));
    tab.addEventListener('keydown', event => {
      if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
      event.preventDefault();
      let nextIndex = index;
      if (event.key === 'ArrowLeft') nextIndex = (index - 1 + tabs.length) % tabs.length;
      if (event.key === 'ArrowRight') nextIndex = (index + 1) % tabs.length;
      if (event.key === 'Home') nextIndex = 0;
      if (event.key === 'End') nextIndex = tabs.length - 1;
      activateTab(tabs[nextIndex].dataset.weightTab, true);
    });
  });
  activateTab(savedGender);
}

function setupChampionshipScoreboard() {
  let timerSoundContext = null;
  let serverWarningSoundPlayed = false;
  let serverEndSoundPlayed = false;
  const prepareTimerSound = () => {
    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    if (!AudioContextClass) return null;
    try {
      if (!timerSoundContext) timerSoundContext = new AudioContextClass();
      if (timerSoundContext.state === 'suspended') timerSoundContext.resume().catch(() => {});
      return timerSoundContext;
    } catch (_) {
      return null;
    }
  };
  const audioMap = {
    start: '/static/audio/time_start.mp3',
    warning: '/static/audio/time_30.mp3',
    end: '/static/audio/time_end.mp3'
  };

  const playSynthHorn = signal => {
    const context = prepareTimerSound();
    if (!context) return;
    const startAt = context.currentTime + 0.02;

    const hornBlasts = {
      start: [{ offset: 0, duration: 0.7 }],
      warning: [{ offset: 0, duration: 0.4 }, { offset: 0.55, duration: 0.4 }],
      end: [{ offset: 0, duration: 1.8 }]
    };

    const blasts = hornBlasts[signal] || [{ offset: 0, duration: 1.2 }];
    const hornFrequencies = [108, 136, 162, 216, 272];

    blasts.forEach(blast => {
      const blastStart = startAt + blast.offset;
      const blastEnd = blastStart + blast.duration;

      const masterGain = context.createGain();
      masterGain.gain.setValueAtTime(0.0001, blastStart);
      masterGain.gain.exponentialRampToValueAtTime(0.85, blastStart + 0.015);
      masterGain.gain.setValueAtTime(0.85, blastEnd - 0.06);
      masterGain.gain.exponentialRampToValueAtTime(0.0001, blastEnd);
      masterGain.connect(context.destination);

      hornFrequencies.forEach((freq, idx) => {
        const osc = context.createOscillator();
        osc.type = 'sawtooth';
        const detuneAmount = (idx % 2 === 0 ? 1 : -1) * (idx * 3.5);
        
        osc.frequency.setValueAtTime(freq, blastStart);
        osc.frequency.exponentialRampToValueAtTime(freq * 0.94, blastEnd);
        osc.detune.setValueAtTime(detuneAmount, blastStart);

        const oscGain = context.createGain();
        const layerGain = idx === 0 ? 0.35 : (idx === 1 ? 0.30 : 0.20);
        oscGain.gain.setValueAtTime(layerGain, blastStart);

        osc.connect(oscGain);
        oscGain.connect(masterGain);

        osc.start(blastStart);
        osc.stop(blastEnd + 0.05);
      });
    });
  };

  const playTimerSignal = signal => {
    const audioPath = audioMap[signal];
    if (audioPath) {
      const audio = new Audio(audioPath);
      audio.play().catch(() => {
        playSynthHorn(signal);
      });
    } else {
      playSynthHorn(signal);
    }
  };

  // Botões manuais para testar cada som individualmente (Início, 30s, Fim)
  document.querySelectorAll('[data-test-sound], [data-test-truck-horn], .btn-test-horn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const soundType = btn.dataset.testSound || 'end';
      playTimerSignal(soundType);
    });
  });
  const viewTabs = [...document.querySelectorAll('[data-scoreboard-tab]')];
  const viewPanels = [...document.querySelectorAll('[data-scoreboard-panel]')];
  const activateView = (view, focus = false) => {
    viewTabs.forEach(tab => {
      const active = tab.dataset.scoreboardTab === view;
      tab.classList.toggle('active', active);
      tab.setAttribute('aria-selected', String(active));
      tab.setAttribute('tabindex', active ? '0' : '-1');
      if (active && focus) tab.focus();
    });
    viewPanels.forEach(panel => {
      const active = panel.dataset.scoreboardPanel === view;
      panel.classList.toggle('active', active);
      panel.hidden = !active;
    });
    const url = new URL(window.location.href);
    url.searchParams.set('view', view);
    window.history.replaceState({}, '', url);
  };
  viewTabs.forEach((tab, index) => {
    tab.addEventListener('click', () => activateView(tab.dataset.scoreboardTab));
    tab.addEventListener('keydown', event => {
      if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
      event.preventDefault();
      let nextIndex = index;
      if (event.key === 'ArrowLeft') nextIndex = (index - 1 + viewTabs.length) % viewTabs.length;
      if (event.key === 'ArrowRight') nextIndex = (index + 1) % viewTabs.length;
      if (event.key === 'Home') nextIndex = 0;
      if (event.key === 'End') nextIndex = viewTabs.length - 1;
      activateView(viewTabs[nextIndex].dataset.scoreboardTab, true);
    });
  });

  const setupServerClock = (root = document) => {
    root.querySelectorAll('[data-score-clock]').forEach(clock => {
      if (clock.dataset.running !== 'true' || clock.dataset.clockBound === 'true') return;
      clock.dataset.clockBound = 'true';
      let seconds = Number(clock.dataset.seconds) || 0;
      const renderClock = () => {
        const minutes = Math.floor(seconds / 60);
        clock.textContent = `${String(minutes).padStart(2, '0')}:${String(seconds % 60).padStart(2, '0')}`;
        clock.classList.toggle('is-ending', seconds > 0 && seconds <= 30);
      };
      renderClock();
      const interval = window.setInterval(() => {
        const previousSeconds = seconds;
        seconds = Math.max(0, seconds - 1);
        renderClock();
        if (previousSeconds > 30 && seconds <= 30 && seconds > 0 && !serverWarningSoundPlayed) {
          serverWarningSoundPlayed = true;
          playTimerSignal('warning');
        }
        if (seconds === 0) {
          window.clearInterval(interval);
          if (previousSeconds > 0 && !serverEndSoundPlayed) {
            serverEndSoundPlayed = true;
            playTimerSignal('end');
          }
        }
      }, 1000);
    });
  };
  setupServerClock();

  const standaloneClock = document.querySelector('[data-standalone-clock]');
  const cronTabsList = document.getElementById('cronTabsList');
  const btnAddCronTimer = document.getElementById('btnAddCronTimer');

  if (standaloneClock) {
    let cronTimers = [
      { id: 1, name: 'Cron 1', duration: 300, seconds: 300, deadline: 0, running: false, warningSoundPlayed: false, endSoundPlayed: false }
    ];
    let activeCronId = 1;
    let nextCronNum = 2;

    const getActiveTimer = () => cronTimers.find(t => t.id === activeCronId) || cronTimers[0];

    const renderCronTabs = () => {
      if (!cronTabsList) return;
      cronTabsList.innerHTML = '';
      cronTimers.forEach(timer => {
        const tab = document.createElement('button');
        tab.type = 'button';
        tab.className = `cron-tab-item ${timer.id === activeCronId ? 'active' : ''}`;
        const isActive = timer.id === activeCronId;
        tab.style.cssText = `
          display: inline-flex; align-items: center; gap: 6px; padding: 6px 12px;
          background: ${isActive ? 'rgba(229, 9, 20, 0.85)' : 'rgba(255, 255, 255, 0.05)'};
          border: 1px solid ${isActive ? '#f87171' : 'rgba(255, 255, 255, 0.12)'};
          color: ${isActive ? '#ffffff' : '#94a3b8'};
          border-radius: 6px; font-weight: 700; font-size: 0.82rem; cursor: pointer; transition: all 0.2s ease;
          box-shadow: ${isActive ? '0 0 12px rgba(229, 9, 20, 0.4)' : 'none'};
        `;
        
        const isLiveDot = timer.running ? '<span style="width: 7px; height: 7px; border-radius: 50%; background: #4ade80; display: inline-block; box-shadow: 0 0 8px #4ade80;"></span>' : '';
        const closeBtn = cronTimers.length > 1 ? `<span class="btn-del-cron" data-cron-id="${timer.id}" title="Remover este cronômetro" style="margin-left: 4px; padding: 0 4px; border-radius: 3px; background: rgba(0,0,0,0.3); font-size: 0.85rem;">&times;</span>` : '';

        tab.innerHTML = `${isLiveDot} ⏱️ ${timer.name} ${closeBtn}`;

        tab.addEventListener('click', (e) => {
          if (e.target.classList.contains('btn-del-cron')) {
            e.stopPropagation();
            deleteCronTimer(timer.id);
            return;
          }
          activeCronId = timer.id;
          renderCronTabs();
          syncUIWithActiveTimer();
        });

        cronTabsList.appendChild(tab);
      });
    };

    const syncUIWithActiveTimer = () => {
      const current = getActiveTimer();
      if (!current) return;

      const mins = Math.floor(current.seconds / 60);
      const secs = current.seconds % 60;
      standaloneClock.textContent = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
      standaloneClock.classList.toggle('is-ending', current.seconds > 0 && current.seconds <= 30);

      const status = document.querySelector('[data-standalone-status]');
      if (status) {
        status.textContent = current.seconds === 0 ? 'TEMPO ENCERRADO' : (current.running ? 'EM ANDAMENTO' : 'CRONÔMETRO PAUSADO');
        status.classList.toggle('is-live', current.running);
      }

      const toggleButton = document.querySelector('[data-standalone-action="toggle"]');
      if (toggleButton) {
        const toggleLabel = toggleButton.querySelector('span');
        if (toggleLabel) toggleLabel.textContent = current.running ? 'Pausar cronômetro' : (current.seconds === 0 ? 'Iniciar novamente' : 'Iniciar cronômetro');
        toggleButton.classList.toggle('is-running', current.running);
      }

      document.querySelectorAll('[data-standalone-duration]').forEach(btn => {
        const btnMins = Number(btn.dataset.standaloneDuration);
        btn.classList.toggle('active', btnMins * 60 === current.duration);
      });
    };

    const deleteCronTimer = (id) => {
      if (cronTimers.length <= 1) return;
      cronTimers = cronTimers.filter(t => t.id !== id);
      if (activeCronId === id) {
        activeCronId = cronTimers[0].id;
      }
      renderCronTabs();
      syncUIWithActiveTimer();
    };

    if (btnAddCronTimer) {
      btnAddCronTimer.addEventListener('click', () => {
        const newId = Date.now();
        const newName = `Cron ${nextCronNum++}`;
        cronTimers.push({
          id: newId, name: newName, duration: 300, seconds: 300, deadline: 0, running: false, warningSoundPlayed: false, endSoundPlayed: false
        });
        activeCronId = newId;
        renderCronTabs();
        syncUIWithActiveTimer();
      });
    }

    // Intervalo único para atualização de TODOS os cronômetros ativos
    window.setInterval(() => {
      cronTimers.forEach(t => {
        if (t.running) {
          const prevSecs = t.seconds;
          t.seconds = Math.max(0, Math.ceil((t.deadline - Date.now()) / 1000));
          if (prevSecs > 30 && t.seconds <= 30 && t.seconds > 0 && !t.warningSoundPlayed) {
            t.warningSoundPlayed = true;
            playTimerSignal('warning');
          }
          if (t.seconds === 0) {
            t.running = false;
            if (prevSecs > 0 && !t.endSoundPlayed) {
              t.endSoundPlayed = true;
              playTimerSignal('end');
            }
          }
        }
      });
      renderCronTabs();
      syncUIWithActiveTimer();
    }, 400);

    // Botão Iniciar / Pausar
    document.querySelector('[data-standalone-action="toggle"]')?.addEventListener('click', () => {
      prepareTimerSound();
      const current = getActiveTimer();
      if (current.running) {
        current.running = false;
      } else {
        if (current.seconds === 0) current.seconds = current.duration;
        current.warningSoundPlayed = false;
        current.endSoundPlayed = false;
        current.deadline = Date.now() + (current.seconds * 1000);
        current.running = true;
        playTimerSignal('start');
      }
      renderCronTabs();
      syncUIWithActiveTimer();
    });

    // Botão Reiniciar
    document.querySelector('[data-standalone-action="reset"]')?.addEventListener('click', () => {
      const current = getActiveTimer();
      current.running = false;
      current.seconds = current.duration;
      current.warningSoundPlayed = false;
      current.endSoundPlayed = false;
      renderCronTabs();
      syncUIWithActiveTimer();
    });

    // Botoes de Presets (2, 3, 4, 5, 6, 10 min)
    document.querySelectorAll('[data-standalone-duration]').forEach(btn => {
      btn.addEventListener('click', () => {
        const current = getActiveTimer();
        const mins = Number(btn.dataset.standaloneDuration);
        current.duration = mins * 60;
        current.seconds = current.duration;
        current.running = false;
        current.warningSoundPlayed = false;
        current.endSoundPlayed = false;
        renderCronTabs();
        syncUIWithActiveTimer();
      });
    });

    // Form de Tempo Personalizado
    const customForm = document.querySelector('[data-standalone-custom]');
    if (customForm) {
      customForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const current = getActiveTimer();
        const m = Number(customForm.querySelector('input[name="custom_minutes"]').value) || 0;
        const s = Number(customForm.querySelector('input[name="custom_seconds"]').value) || 0;
        current.duration = Math.max(1, (m * 60) + s);
        current.seconds = current.duration;
        current.running = false;
        current.warningSoundPlayed = false;
        current.endSoundPlayed = false;
        renderCronTabs();
        syncUIWithActiveTimer();
      });
    }

    renderCronTabs();
    syncUIWithActiveTimer();
  }

  const scoreboardContent = document.querySelector('.championship-scoreboard-content');
  scoreboardContent?.addEventListener('click', async event => {
    if (event.target.closest('button[value="start_timer"]')) {
      serverWarningSoundPlayed = false;
      serverEndSoundPlayed = false;
      prepareTimerSound();
      playTimerSignal('start');
    }
    const disqualifyButton = event.target.closest('[data-disqualify]');
    if (disqualifyButton && disqualifyButton.dataset.confirmed !== 'true') {
      event.preventDefault();
      disqualifyButton.dataset.confirmed = 'true';
      disqualifyButton.classList.add('is-confirming');
      const copy = disqualifyButton.querySelector('[data-disqualify-copy]');
      if (copy) copy.textContent = 'Clique novamente para confirmar';
      window.setTimeout(() => {
        if (!disqualifyButton.isConnected) return;
        delete disqualifyButton.dataset.confirmed;
        disqualifyButton.classList.remove('is-confirming');
        if (copy) copy.textContent = 'Exige confirmação';
      }, 4500);
      return;
    }
    const toggleGameThemeBtn = event.target.closest('[data-toggle-game-theme]');
    if (toggleGameThemeBtn) {
      const main = document.getElementById('scoreboardMainContent');
      const stg = document.querySelector('.scoreboard-stage');
      const isGameMode = main?.classList.toggle('theme-area-game');
      stg?.classList.toggle('theme-area-game-stage');

      document.querySelectorAll('.hud-graffiti-score').forEach(el => el.classList.toggle('hidden', !isGameMode));
      document.querySelectorAll('.hud-plain-score').forEach(el => el.classList.toggle('hidden', isGameMode));
      return;
    }
    const timerFullscreen = event.target.closest('[data-timer-fullscreen]');
    const stageFullscreen = event.target.closest('[data-scoreboard-stage-fullscreen]');
    const target = timerFullscreen?.closest('[data-scoreboard-panel="timer"]') || stageFullscreen?.closest('.scoreboard-stage');
    if (!target) return;
    try {
      if (document.fullscreenElement) await document.exitFullscreen();
      else await target.requestFullscreen();
    } catch (_) {}
  });

  if ('wakeLock' in navigator) {
    try { navigator.wakeLock.request('screen'); } catch (_) {}
  }

  scoreboardContent?.addEventListener('submit', async event => {
    const form = event.target.closest('.scoreboard-stage form[method="post"]');
    if (!form || form.matches('[data-standalone-custom]')) return;
    event.preventDefault();
    if (!form.checkValidity()) { form.reportValidity(); return; }
    const submitter = event.submitter;
    const formData = new FormData(form);
    if (submitter?.name) formData.set(submitter.name, submitter.value);
    const stage = form.closest('.scoreboard-stage');
    if (!stage || stage.dataset.submitting === 'true') return;
    stage.dataset.submitting = 'true';
    submitter?.classList.add('is-processing');
    if (submitter) submitter.disabled = true;
    try {
      const response = await fetch(form.getAttribute('action') || window.location.href, {
        method: 'POST', body: formData, credentials: 'same-origin',
        headers: {'X-Requested-With': 'scoreboard-fetch'},
      });
      if (!response.ok) throw new Error('Falha ao atualizar o placar.');
      const parsed = new DOMParser().parseFromString(await response.text(), 'text/html');
      const updatedStage = parsed.querySelector('.scoreboard-stage');
      if (!updatedStage) throw new Error('Resposta do placar incompleta.');
      stage.className = updatedStage.className;
      stage.innerHTML = updatedStage.innerHTML;
      const currentMatchTabs = scoreboardContent.querySelector('.scoreboard-match-tabs');
      const updatedMatchTabs = parsed.querySelector('.scoreboard-match-tabs');
      if (currentMatchTabs && updatedMatchTabs) currentMatchTabs.innerHTML = updatedMatchTabs.innerHTML;
      stage.classList.add('is-just-updated');
      const redCorner = stage.querySelector('.scoreboard-corner.is-red');
      const blueCorner = stage.querySelector('.scoreboard-corner.is-blue');
      if (submitter?.name?.startsWith('red_')) redCorner?.classList.add('is-point-flash');
      if (submitter?.name?.startsWith('blue_')) blueCorner?.classList.add('is-point-flash');
      window.setTimeout(() => {
        stage.classList.remove('is-just-updated');
        redCorner?.classList.remove('is-point-flash');
        blueCorner?.classList.remove('is-point-flash');
      }, 550);
      const responseFlash = parsed.querySelector('.flash-stack');
      if (responseFlash) {
        document.querySelector('.flash-stack')?.remove();
        document.querySelector('.erp-topbar')?.insertAdjacentElement('afterend', responseFlash);
        setupFlashMessages();
      }
      setupServerClock(stage);
      initIcons();
    } catch (_) {
      window.location.reload();
    } finally {
      delete stage.dataset.submitting;
      submitter?.classList.remove('is-processing');
      if (submitter) submitter.disabled = false;
    }
  });
  document.addEventListener('keydown', event => {
    const panel = document.querySelector('[data-scoreboard-panel="timer"].active');
    if (!panel || event.target.matches('input, select, textarea') || event.repeat) return;
    const key = event.key.toLowerCase();
    if (key === 'f') panel.querySelector('[data-timer-fullscreen]')?.click();
    if (key === 'r') {
      const reset = panel.querySelector('[data-standalone-action="reset"], button[value="reset_timer"]');
      if (reset) { event.preventDefault(); reset.click(); }
    }
    if (event.code === 'Space') {
      const toggle = panel.querySelector('[data-standalone-action="toggle"], button[value="start_timer"], button[value="pause_timer"]');
      if (toggle) { event.preventDefault(); toggle.click(); }
    }
  });

  const modal = document.querySelector('[data-scoreboard-create-modal]');
  const openButton = document.querySelector('[data-scoreboard-create-open]');
  if (!modal || !openButton) return;
  const closeModal = () => {
    modal.classList.add('hidden');
    document.body.style.overflow = '';
  };
  openButton.addEventListener('click', () => {
    if (openButton.disabled) return;
    modal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
    window.setTimeout(() => modal.querySelector('select[name="championship_id"]')?.focus(), 30);
  });
  modal.querySelectorAll('[data-scoreboard-create-close]').forEach(button => button.addEventListener('click', closeModal));
  modal.addEventListener('click', event => {
    if (event.target === modal) closeModal();
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && !modal.classList.contains('hidden')) closeModal();
  });
}

function setupContractPage() {
  const printButton = document.querySelector('[data-contract-print]');
  if (printButton) printButton.addEventListener('click', () => window.print());
  const imageChoice = document.querySelector('[data-contract-image-choice]');
  const minorFields = document.querySelector('[data-contract-minor-fields]');
  if (!imageChoice || !minorFields) return;
  const options = [...imageChoice.querySelectorAll('input[name="imageConsentScope"]')];
  const updateMinorFields = () => {
    const isMinor = options.some(option => option.checked && option.value === 'minor_guardian');
    minorFields.classList.toggle('hidden', !isMinor);
    minorFields.querySelectorAll('input, select').forEach(field => {
      field.required = isMinor;
      field.disabled = !isMinor;
    });
  };
  options.forEach(option => option.addEventListener('change', updateMinorFields));
  updateMinorFields();
}

// UNIVERSAL CUSTOM CONFIRMATION MODAL (SUBSTITUI PROMPT NATIVO DO NAVEGADOR)
function showCustomConfirm(options = {}) {
  return new Promise((resolve) => {
    const modal = document.getElementById('customConfirmModal');
    const titleEl = document.getElementById('customConfirmTitle');
    const messageEl = document.getElementById('customConfirmMessage');
    const okBtn = document.getElementById('customConfirmOkBtn');
    const cancelBtn = document.getElementById('customConfirmCancelBtn');
    const iconBox = document.getElementById('customConfirmIcon');

    if (!modal || !okBtn || !cancelBtn) {
      resolve(window.confirm(options.message || 'Confirmar ação?'));
      return;
    }

    if (titleEl) titleEl.textContent = options.title || 'Confirmar Ação';
    if (messageEl) messageEl.textContent = options.message || 'Você tem certeza que deseja realizar esta operação?';

    if (options.isDanger) {
      okBtn.style.background = 'linear-gradient(135deg, #ef4444, #b91c1c)';
      okBtn.style.color = '#ffffff';
      okBtn.textContent = options.okText || 'Sim, Excluir';
      if (iconBox) {
        iconBox.style.borderColor = '#ef4444';
        iconBox.style.background = 'rgba(239, 68, 68, 0.15)';
        iconBox.style.color = '#ef4444';
        iconBox.innerHTML = '<i data-lucide="alert-triangle" style="width:28px;height:28px;"></i>';
      }
    } else if (options.isReset) {
      okBtn.style.background = 'linear-gradient(135deg, #3b82f6, #1d4ed8)';
      okBtn.style.color = '#ffffff';
      okBtn.textContent = options.okText || 'Redefinir Senha';
      if (iconBox) {
        iconBox.style.borderColor = '#60a5fa';
        iconBox.style.background = 'rgba(59, 130, 246, 0.15)';
        iconBox.style.color = '#60a5fa';
        iconBox.innerHTML = '<i data-lucide="key-round" style="width:28px;height:28px;"></i>';
      }
    } else {
      okBtn.style.background = 'linear-gradient(135deg, var(--accent-gold), #d97706)';
      okBtn.style.color = '#0f172a';
      okBtn.textContent = options.okText || 'Confirmar';
      if (iconBox) {
        iconBox.style.borderColor = 'var(--accent-gold)';
        iconBox.style.background = 'rgba(245, 158, 11, 0.15)';
        iconBox.style.color = 'var(--accent-gold)';
        iconBox.innerHTML = '<i data-lucide="help-circle" style="width:28px;height:28px;"></i>';
      }
    }
    if (window.lucide) lucide.createIcons();

    modal.classList.remove('hidden');

    const cleanup = () => {
      modal.classList.add('hidden');
      okBtn.removeEventListener('click', onOk);
      cancelBtn.removeEventListener('click', onCancel);
    };

    const onOk = () => { cleanup(); resolve(true); };
    const onCancel = () => { cleanup(); resolve(false); };

    okBtn.addEventListener('click', onOk);
    cancelBtn.addEventListener('click', onCancel);
  });
}

function setupCustomConfirmForms() {
  document.addEventListener('submit', (e) => {
    const form = e.target;
    if (!form || form.dataset.customConfirmBypassed === 'true') return;

    const confirmMsg = form.getAttribute('data-confirm');
    const isResetForm = form.classList.contains('student-password-reset') || form.dataset.confirmReset === 'true';

    if (confirmMsg || isResetForm) {
      e.preventDefault();
      const message = confirmMsg || 'Deseja redefinir a senha deste usuário para "bemvindo"?';
      const isDanger = form.dataset.confirmDanger === 'true';
      const title = form.dataset.confirmTitle || (isResetForm ? '🔑 Redefinir Senha' : (isDanger ? '⚠️ Confirmar Exclusão' : 'Confirmar Ação'));
      const okText = form.dataset.confirmOkText || (isResetForm ? 'Sim, Redefinir Senha' : (isDanger ? 'Sim, Excluir' : 'Confirmar'));

      showCustomConfirm({
        title: title,
        message: message,
        isDanger: isDanger,
        isReset: isResetForm,
        okText: okText
      }).then((confirmed) => {
        if (confirmed) {
          form.dataset.customConfirmBypassed = 'true';
          form.submit();
        }
      });
    }
  });
}

function setupMobileNavDrawer() {
  const mobileNavToggle = document.getElementById('mobileNavToggle');
  const mobileNavDrawer = document.getElementById('mobileNavDrawer');
  const mobileNavOverlay = document.getElementById('mobileNavOverlay');
  const mobileDrawerClose = document.getElementById('mobileDrawerClose');
  const mobileLocaisTrigger = document.getElementById('mobileLocaisTrigger');
  const mobileLocaisSubitems = document.getElementById('mobileLocaisSubitems');

  function openMobileDrawer() {
    if (mobileNavDrawer && mobileNavOverlay) {
      mobileNavDrawer.classList.add('active');
      mobileNavOverlay.classList.add('active');
      document.body.style.overflow = 'hidden';
      if (window.lucide) window.lucide.createIcons();
    }
  }

  function closeMobileDrawer() {
    if (mobileNavDrawer && mobileNavOverlay) {
      mobileNavDrawer.classList.remove('active');
      mobileNavOverlay.classList.remove('active');
      document.body.style.overflow = '';
    }
  }

  if (mobileNavToggle) mobileNavToggle.addEventListener('click', openMobileDrawer);
  if (mobileDrawerClose) mobileDrawerClose.addEventListener('click', closeMobileDrawer);
  if (mobileNavOverlay) mobileNavOverlay.addEventListener('click', closeMobileDrawer);

  if (mobileLocaisTrigger && mobileLocaisSubitems) {
    mobileLocaisTrigger.addEventListener('click', () => {
      mobileLocaisTrigger.classList.toggle('active');
      mobileLocaisSubitems.classList.toggle('hidden');
    });
  }
}

// DOM Loaded
document.addEventListener('DOMContentLoaded', () => {
  const trialCountdowns = [...document.querySelectorAll('[data-trial-countdown]')];
  if (trialCountdowns.length) {
    const startedAt = Date.now();
    const initialSeconds = Math.max(0, Number(trialCountdowns[0].dataset.trialCountdown) || 0);
    const renderTrialCountdown = () => {
      const elapsed = Math.floor((Date.now() - startedAt) / 1000);
      const remaining = Math.max(0, initialSeconds - elapsed);
      const hours = Math.floor(remaining / 3600);
      const minutes = Math.floor((remaining % 3600) / 60);
      const seconds = remaining % 60;
      const formatted = [hours, minutes, seconds].map(value => String(value).padStart(2, '0')).join(':');
      trialCountdowns.forEach(element => { element.textContent = formatted; });
      if (remaining === 0) window.location.reload();
    };
    renderTrialCountdown();
    window.setInterval(renderTrialCountdown, 1000);
  }

  setupCsrfProtection();
  setupFlashMessages();
  setupDueDateProrationPreview();
  renderSchedule('seg');
  loadScheduleCapacity();
  setupScheduleFilters();
  setupPlanButtons();
  setupBookingModal();
  setupPortalPage();
  setupERPSidebar();
  setupERPTopbar();
  setupPublicTheme();
  setupPasswordEyeToggles();
  setupCpfMask();
  setupRegistrationValidation();
  setupGlobalKeyListeners();
  setupAttendanceRejectionConfirmation();
  setupClassManagementPreview();
  setupSpecialClassEventModal();
  setupCalendarSyncModal();
  setupChampionshipCreateModal();
  setupChampionshipWeightTabs();
  setupChampionshipScoreboard();
  setupContractPage();
  setupCustomConfirmForms();
  setupMobileNavDrawer();
  initIcons();
});

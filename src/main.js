import confetti from 'canvas-confetti';
import { 
  createIcons, 
  Clock, 
  CalendarCheck, 
  Zap, 
  ShieldCheck, 
  Dumbbell, 
  Swords, 
  Trophy, 
  Target, 
  CheckCircle, 
  UserCheck,
  UserPlus,
  LogIn,
  Instagram,
  Phone,
  Tag,
  Check,
  MapPin,
  User,
  MessageSquare,
  Sparkles,
  Award,
  AlertTriangle,
  ChevronDown,
  Building2,
  Eye,
  EyeOff
} from 'lucide';

// Initialize Lucide Icons
function initIcons() {
  createIcons({
    icons: {
      Clock,
      CalendarCheck,
      Zap,
      ShieldCheck,
      Dumbbell,
      Swords,
      Trophy,
      Target,
      CheckCircle,
      UserCheck,
      UserPlus,
      LogIn,
      Instagram,
      Phone,
      Tag,
      Check,
      MapPin,
      User,
      MessageSquare,
      Sparkles,
      Award,
      AlertTriangle,
      ChevronDown,
      Building2,
      Eye,
      EyeOff
    }
  });
}

// Schedule Data based on Mestre Bolivar's exact parameters (Clean table items)
const scheduleData = {
  seg: [
    { name: 'Boxe Matinal', freq: '3x / semana (Seg, Qua, Sex)', time: '06:00h', price: 'R$ 90,00 /mês', tag: 'tag-boxe', tagLabel: 'Boxe' },
    { name: 'Jiu-Jitsu Tarde', freq: '3x / semana (Seg, Qua, Sex)', time: '17:00h', price: 'R$ 100,00 /mês', tag: 'tag-bjj', tagLabel: 'Jiu-Jitsu' },
    { name: 'Jiu-Jitsu Noturno', freq: '3x / semana (Seg, Qua, Sex)', time: '19:00h', price: 'R$ 100,00 /mês', tag: 'tag-bjj', tagLabel: 'Jiu-Jitsu' }
  ],
  ter: [
    { name: 'Jiu-Jitsu Almoço', freq: '2x / semana (Ter, Qui)', time: '12:00h', price: 'R$ 90,00 /mês', tag: 'tag-bjj', tagLabel: 'Jiu-Jitsu' },
    { name: 'Jiu-Jitsu Noturno', freq: '2x / semana (Ter, Qui)', time: '19:00h', price: 'R$ 90,00 /mês', tag: 'tag-bjj', tagLabel: 'Jiu-Jitsu' },
    { name: 'Boxe Noturno', freq: '2x / semana (Ter, Qui)', time: '19:00h', price: 'R$ 90,00 /mês', tag: 'tag-boxe', tagLabel: 'Boxe' }
  ],
  todos: [
    { name: 'Plano Passe Livre (BJJ & Boxe)', freq: 'Diário (Livre Acesso)', time: 'Todos os Horários', price: 'R$ 120,00 /mês', tag: 'tag-func', tagLabel: 'Livre Acesso' },
    { name: 'Plano Família (3 pessoas)', freq: 'Livre Escolha', time: 'Todos os Horários', price: 'R$ 280,00 /mês', tag: 'tag-bjj', tagLabel: 'Família' },
    { name: 'Plano Casal (2 pessoas)', freq: 'Livre Escolha', time: 'Todos os Horários', price: 'R$ 190,00 /mês', tag: 'tag-boxe', tagLabel: 'Casal' }
  ]
};

// Render Schedule Table
function renderSchedule(day = 'seg') {
  const tbody = document.getElementById('scheduleTableBody');
  if (!tbody) return;

  const rows = scheduleData[day] || [];
  if (rows.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5" class="text-center">Nenhum treino listado.</td></tr>`;
    return;
  }

  tbody.innerHTML = rows.map(item => `
    <tr>
      <td>
        <span class="tag-badge ${item.tag}">${item.tagLabel}</span>
        <strong style="margin-left: 8px;">${item.name}</strong>
      </td>
      <td>${item.freq}</td>
      <td><span class="badge-pill">${item.time}</span></td>
      <td><span class="price-highlight">${item.price}</span></td>
      <td>
        <button class="btn btn-secondary btn-sm quick-book-btn" data-modality="${item.name}">
          Reservar
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
  // 0 = Sun, 1 = Mon, 2 = Tue, 3 = Wed, 4 = Thu, 5 = Fri, 6 = Sat
  if (dayOfWeek === 1 || dayOfWeek === 3 || dayOfWeek === 5) {
    return [
      { time: '06:00h', title: 'Boxe Matinal' },
      { time: '17:00h', title: 'Jiu-Jitsu Tarde' },
      { time: '19:00h', title: 'Jiu-Jitsu Noturno' }
    ];
  } else if (dayOfWeek === 2 || dayOfWeek === 4) {
    return [
      { time: '12:00h', title: 'Jiu-Jitsu Almoço' },
      { time: '19:00h', title: 'Jiu-Jitsu / Boxe Noturno' }
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

  // Rule: If today is Saturday (6) or Sunday (0), show ONLY Monday's classes!
  if (currentDay === 6 || currentDay === 0) {
    const daysUntilMonday = (currentDay === 6) ? 2 : 1;
    const nextMonday = new Date(now);
    nextMonday.setDate(now.getDate() + daysUntilMonday);

    const formattedDate = formatDateBR(nextMonday);
    const classes = getClassesForDay(1); // Monday classes

    optionsHTML = classes.map(c => `
      <option value="Segunda-feira (${formattedDate}) — ${c.time} (${c.title})">
        Segunda-feira (${formattedDate}) — ${c.time} (${c.title})
      </option>
    `).join('');

    if (hint) {
      hint.textContent = `⚡ Fim de semana: Exibindo horários das aulas de Segunda-feira (${formattedDate}).`;
    }
  } else {
    // Weekday: Calculate available classes for Today and Tomorrow (48h window)
    const datesToEvaluate = [];
    
    // Today
    datesToEvaluate.push({ date: new Date(now), isToday: true });

    // Tomorrow (+24h)
    const tomorrow = new Date(now);
    tomorrow.setDate(now.getDate() + 1);
    datesToEvaluate.push({ date: tomorrow, isToday: false });

    const availableOptions = [];

    datesToEvaluate.forEach(item => {
      const d = item.date;
      const dayW = d.getDay();
      if (dayW === 0 || dayW === 6) return; // Skip Sat & Sun

      const dateStr = formatDateBR(d);
      const dayName = dayNamesBR[dayW];
      const classes = getClassesForDay(dayW);

      classes.forEach(c => {
        // If class is today, check if time has not passed
        if (item.isToday) {
          const classHour = parseInt(c.time.split(':')[0], 10);
          if (currentHour >= classHour) return; // Passed
        }

        const label = `${dayName} (${dateStr}) — ${c.time} (${c.title})`;
        availableOptions.push(`<option value="${label}">${label}</option>`);
      });
    });

    if (availableOptions.length === 0) {
      // Fallback if all classes for today passed, show next valid weekday
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

// Booking Modal
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

  if (modal) modal.classList.add('hidden');

  function openModal() {
    populate48hScheduleOptions();
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
    bookingForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const isExperimental = chkExperimental ? chkExperimental.checked : false;
      const loginOrName = document.getElementById('bookLogin').value;
      const cpf3 = document.getElementById('bookCpf3') ? document.getElementById('bookCpf3').value : '';
      const modality = document.getElementById('bookModality').value;
      const shift = document.getElementById('bookShift').value;

      confetti({
        particleCount: 150,
        spread: 90,
        origin: { y: 0.5 }
      });

      // Format WhatsApp Message
      let msg = '';
      if (isExperimental) {
        msg += `*RESERVA — AULA EXPERIMENTAL GRÁTIS*\n\n`;
        msg += `👤 *Nome Completo:* ${loginOrName}\n`;
      } else {
        msg += `*RESERVA DE VAGA NA AULA — BJ SPORTS*\n\n`;
        msg += `👤 *Login:* ${loginOrName}\n`;
        msg += `🛡️ *3 Primeiros Dígitos CPF:* ${cpf3}\n`;
      }
      msg += `🥋 *Modalidade:* ${modality}\n`;
      msg += `🕒 *Aula Desejada:* ${shift}\n`;
      msg += `⏱️ *Janela:* Agendamento para as próximas 48h\n\n`;
      msg += `📍 *Local:* Av. Estrada do Amor, Cajazeiras-PB\n`;
      msg += `Olá Mestre Bolivar, gostaria de confirmar minha reserva!`;

      const encodedMsg = encodeURIComponent(msg);
      const waUrl = `https://wa.me/5583996527997?text=${encodedMsg}`;

      window.open(waUrl, '_blank');

      bookingForm.reset();
      toggleExperimentalMode();
      closeModal();
    });
  }
}

function openModalWithModality(modalityName) {
  const modal = document.getElementById('bookingModal');
  const select = document.getElementById('bookModality');
  populate48hScheduleOptions();
  if (select) {
    for (let option of select.options) {
      if (option.value.toLowerCase().includes(modalityName.toLowerCase()) || modalityName.toLowerCase().includes(option.value.toLowerCase())) {
        option.selected = true;
        break;
      }
    }
  }
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

// Standalone Login & Cadastro Page Handler (login.html)
function setupPortalPage() {
  const tabLogin = document.getElementById('tabBtnLogin');
  const tabRegister = document.getElementById('tabBtnRegister');
  const formLogin = document.getElementById('portalLoginForm');
  const formRegister = document.getElementById('portalRegisterForm');
  const dashView = document.getElementById('portalDashboardView');
  const logoutBtn = document.getElementById('logoutPortalBtn');
  const dashNameDisplay = document.getElementById('dashNameDisplay');
  const dashPlanDisplay = document.getElementById('dashPlanDisplay');

  if (!tabLogin || !tabRegister) return;

  tabLogin.addEventListener('click', () => {
    tabLogin.classList.add('active');
    tabRegister.classList.remove('active');
    if (formLogin) formLogin.classList.remove('hidden');
    if (formRegister) formRegister.classList.add('hidden');
  });

  tabRegister.addEventListener('click', () => {
    tabRegister.classList.add('active');
    tabLogin.classList.remove('active');
    if (formRegister) formRegister.classList.remove('hidden');
    if (formLogin) formLogin.classList.add('hidden');
  });

  if (formLogin) {
    formLogin.addEventListener('submit', (e) => {
      e.preventDefault();
      const loginVal = document.getElementById('portalCpf').value;
      confetti({ particleCount: 100, spread: 80, origin: { y: 0.5 } });
      
      if (dashNameDisplay) dashNameDisplay.textContent = loginVal || 'Aluno BJ Sports';
      if (formLogin) formLogin.classList.add('hidden');
      if (formRegister) formRegister.classList.add('hidden');
      document.getElementById('portalTabs').classList.add('hidden');
      if (dashView) dashView.classList.remove('hidden');
    });
  }

  if (formRegister) {
    formRegister.addEventListener('submit', (e) => {
      e.preventDefault();
      const usernameVal = document.getElementById('regUsername').value;
      const nameVal = document.getElementById('regName').value;
      const dddVal = document.getElementById('regDDD').value;
      const phoneVal = document.getElementById('regPhoneNumber').value;
      const planVal = document.getElementById('regPlan').value;
      const passVal = document.getElementById('regPass').value;
      const passConfirmVal = document.getElementById('regPassConfirm').value;

      if (phoneVal.length !== 9 || !/^\d{9}$/.test(phoneVal)) {
        alert('O número do celular deve conter exatamente 9 dígitos (ex: 996527997).');
        return;
      }

      if (passVal !== passConfirmVal) {
        alert('As senhas não coincidem. Por favor, verifique a senha informada.');
        return;
      }

      confetti({ particleCount: 150, spread: 90, origin: { y: 0.5 } });

      if (dashNameDisplay) dashNameDisplay.textContent = `${nameVal} (@${usernameVal})`;
      if (dashPlanDisplay) dashPlanDisplay.textContent = `${planVal} • WhatsApp: (${dddVal}) ${phoneVal}`;

      if (formLogin) formLogin.classList.add('hidden');
      if (formRegister) formRegister.classList.add('hidden');
      document.getElementById('portalTabs').classList.add('hidden');
      if (dashView) dashView.classList.remove('hidden');
    });
  }

  if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
      if (dashView) dashView.classList.add('hidden');
      document.getElementById('portalTabs').classList.remove('hidden');
      tabLogin.click();
    });
  }
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

// DOM Loaded
document.addEventListener('DOMContentLoaded', () => {
  renderSchedule('seg');
  setupScheduleFilters();
  setupPlanButtons();
  setupBookingModal();
  setupPortalPage();
  setupPasswordEyeToggles();
  setupGlobalKeyListeners();
  initIcons();
});

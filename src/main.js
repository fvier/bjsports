import confetti from 'canvas-confetti';
import { 
  createIcons, 
  Flame, 
  Clock, 
  CalendarCheck, 
  Zap, 
  ShieldCheck, 
  Dumbbell, 
  Swords, 
  Trophy, 
  Target, 
  CheckCircle, 
  Moon,
  UserCheck,
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
  AlertTriangle
} from 'lucide';

// Initialize Lucide Icons
function initIcons() {
  createIcons({
    icons: {
      Flame,
      Clock,
      CalendarCheck,
      Zap,
      ShieldCheck,
      Dumbbell,
      Swords,
      Trophy,
      Target,
      CheckCircle,
      Moon,
      UserCheck,
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
      AlertTriangle
    }
  });
}

// Schedule Data based on Mestre Bolivar's exact parameters
const scheduleData = {
  seg: [
    { name: 'Boxe Matinal', freq: '3x / semana (Seg, Qua, Sex)', time: '06:00h', price: 'R$ 90,00 /mês', teacher: 'Mestre Bolivar', tag: 'tag-boxe', tagLabel: 'Boxe' },
    { name: 'Jiu-Jitsu Tarde (Vagas Restritas!)', freq: '3x / semana (Seg, Qua, Sex)', time: '17:00h', price: 'R$ 100,00 /mês', teacher: 'Mestre Bolivar', tag: 'tag-bjj', tagLabel: 'Jiu-Jitsu' },
    { name: 'Jiu-Jitsu Noturno', freq: '3x / semana (Seg, Qua, Sex)', time: '19:00h', price: 'R$ 100,00 /mês', teacher: 'Mestre Bolivar', tag: 'tag-bjj', tagLabel: 'Jiu-Jitsu' }
  ],
  ter: [
    { name: 'Jiu-Jitsu Almoço', freq: '2x / semana (Ter, Qui)', time: '12:00h', price: 'R$ 90,00 /mês', teacher: 'Mestre Bolivar', tag: 'tag-bjj', tagLabel: 'Jiu-Jitsu' },
    { name: 'Jiu-Jitsu Noturno', freq: '2x / semana (Ter, Qui)', time: '19:00h', price: 'R$ 90,00 /mês', teacher: 'Mestre Bolivar', tag: 'tag-bjj', tagLabel: 'Jiu-Jitsu' },
    { name: 'Boxe Noturno', freq: '2x / semana (Ter, Qui)', time: '19:00h', price: 'R$ 90,00 /mês', teacher: 'Mestre Bolivar', tag: 'tag-boxe', tagLabel: 'Boxe' }
  ],
  todos: [
    { name: 'Plano Passe Livre (BJJ & Boxe)', freq: 'Diário (Livre Acesso)', time: 'Todos os Horários', price: 'R$ 120,00 /mês', teacher: 'Mestre Bolivar', tag: 'tag-func', tagLabel: 'Livre Acesso' },
    { name: 'Plano Família (3 pessoas)', freq: 'Livre Escolha', time: 'Todos os Horários', price: 'R$ 280,00 /mês', teacher: 'Mestre Bolivar', tag: 'tag-bjj', tagLabel: 'Família' },
    { name: 'Plano Casal (2 pessoas)', freq: 'Livre Escolha', time: 'Todos os Horários', price: 'R$ 190,00 /mês', teacher: 'Mestre Bolivar', tag: 'tag-boxe', tagLabel: 'Casal' }
  ]
};

// Render Schedule Table
function renderSchedule(day = 'seg') {
  const tbody = document.getElementById('scheduleTableBody');
  if (!tbody) return;

  const rows = scheduleData[day] || [];
  if (rows.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" class="text-center">Nenhum treino listado.</td></tr>`;
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
      <td>${item.teacher}</td>
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

// Booking Modal
function setupBookingModal() {
  const modal = document.getElementById('bookingModal');
  const openBtn = document.getElementById('openScheduleModal');
  const closeBtn = document.getElementById('closeBookingModal');
  const heroCTA = document.getElementById('heroCTA');
  const bookingForm = document.getElementById('bookingForm');

  if (modal) modal.classList.add('hidden');

  function openModal() {
    if (modal) modal.classList.remove('hidden');
  }

  function closeModal() {
    if (modal) modal.classList.add('hidden');
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
      const name = document.getElementById('bookName').value;
      const phone = document.getElementById('bookPhone').value;
      const modality = document.getElementById('bookModality').value;
      const shift = document.getElementById('bookShift').value;

      confetti({
        particleCount: 150,
        spread: 90,
        origin: { y: 0.5 }
      });

      // Format WhatsApp Message
      let msg = `*GARANTIA DE VAGA — BJ SPORTS CAJAZEIRAS*\n\n`;
      msg += `👤 *Nome:* ${name}\n`;
      msg += `📞 *WhatsApp:* ${phone}\n`;
      msg += `🥋 *Modalidade/Plano:* ${modality}\n`;
      msg += `🕒 *Horário/Frequência:* ${shift}\n\n`;
      msg += `📍 *Local:* Av. Estrada do Amor, Cajazeiras-PB\n`;
      msg += `Olá Mestre Bolivar, solicito a confirmação e reserva da minha vaga na turma!`;

      const encodedMsg = encodeURIComponent(msg);
      const waUrl = `https://wa.me/5583996527997?text=${encodedMsg}`;

      window.open(waUrl, '_blank');

      bookingForm.reset();
      closeModal();
    });
  }
}

function openModalWithModality(modalityName) {
  const modal = document.getElementById('bookingModal');
  const select = document.getElementById('bookModality');
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

// Login Modal Setup
function setupLoginModal() {
  const loginModal = document.getElementById('loginModal');
  const openLoginBtn = document.getElementById('openLoginModalBtn');
  const closeLoginBtn = document.getElementById('closeLoginModal');
  const loginForm = document.getElementById('loginForm');
  const dashView = document.getElementById('studentDashboardView');
  const logoutBtn = document.getElementById('logoutStudentBtn');

  if (loginModal) loginModal.classList.add('hidden');

  function openLogin() {
    if (loginModal) loginModal.classList.remove('hidden');
  }

  function closeLogin() {
    if (loginModal) loginModal.classList.add('hidden');
  }

  if (openLoginBtn) openLoginBtn.addEventListener('click', openLogin);
  if (closeLoginBtn) closeLoginBtn.addEventListener('click', closeLogin);

  if (loginModal) {
    loginModal.addEventListener('click', (e) => {
      if (e.target === loginModal) closeLogin();
    });
  }

  if (loginForm) {
    loginForm.addEventListener('submit', (e) => {
      e.preventDefault();
      confetti({ particleCount: 80, spread: 70, origin: { y: 0.5 } });
      loginForm.classList.add('hidden');
      if (dashView) dashView.classList.remove('hidden');
    });
  }

  if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
      if (dashView) dashView.classList.add('hidden');
      if (loginForm) loginForm.classList.remove('hidden');
      closeLogin();
    });
  }
}

// Theme Toggle
function setupThemeToggle() {
  const btn = document.getElementById('themeToggleBtn');
  if (!btn) return;

  btn.addEventListener('click', () => {
    document.body.classList.toggle('light-theme');
  });
}

// Global Keydown Listener for Escape key
function setupGlobalKeyListeners() {
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      const bookingModal = document.getElementById('bookingModal');
      const loginModal = document.getElementById('loginModal');
      if (bookingModal) bookingModal.classList.add('hidden');
      if (loginModal) loginModal.classList.add('hidden');
    }
  });
}

// DOM Loaded
document.addEventListener('DOMContentLoaded', () => {
  renderSchedule('seg');
  setupScheduleFilters();
  setupPlanButtons();
  setupBookingModal();
  setupLoginModal();
  setupThemeToggle();
  setupGlobalKeyListeners();
  initIcons();
});

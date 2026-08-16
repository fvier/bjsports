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
  Calculator, 
  Cpu, 
  Activity, 
  Sparkles, 
  CheckCircle2, 
  CheckCircle, 
  Moon,
  MessageSquare,
  UserCheck,
  LogIn,
  Instagram,
  Phone,
  Tag,
  Check
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
      Calculator,
      Cpu,
      Activity,
      Sparkles,
      CheckCircle2,
      CheckCircle,
      Moon,
      MessageSquare,
      UserCheck,
      LogIn,
      Instagram,
      Phone,
      Tag,
      Check
    }
  });
}

// Data: Modalidades
const modalidadesData = [
  {
    icon: 'swords',
    title: 'Jiu-Jitsu (BJJ)',
    desc: 'Sob orientação do Mestre Bolivar. Aulas técnicas de defesa pessoal, raspagens e finalizações.',
    intensity: 'Alta',
    target: 'Seg, Qua, Sex | Ter e Qui'
  },
  {
    icon: 'target',
    title: 'Boxe Tradicional',
    desc: 'Treinos focados na nobre arte: esquiva, jogo de pernas e golpes precisos.',
    intensity: 'Muito Alta',
    target: 'Seg, Qua, Sex 06h | Ter, Qui 19h'
  },
  {
    icon: 'flame',
    title: 'Muay Thai & Striking',
    desc: 'Condicionamento físico intenso com cotovelos, joelhadas e combinações de chute.',
    intensity: 'Muito Alta',
    target: 'Seg a Sex'
  },
  {
    icon: 'shield-check',
    title: 'Jiu-Jitsu Kids',
    desc: 'Formação marcial e autoconfiança para crianças com incentivo no Plano Kids 2 Irmãos.',
    intensity: 'Moderada',
    target: 'Terças e Quintas'
  }
];

// Schedule Data based on Mestre Bolivar's exact parameters
const scheduleData = {
  seg: [
    { name: 'Boxe Matinal', days: 'Segunda, Quarta e Sexta', time: '06:00h', price: 'R$ 90,00 /mês', teacher: 'Mestre Bolivar', tag: 'tag-boxe', tagLabel: 'Boxe' },
    { name: 'Jiu-Jitsu Tarde', days: 'Segunda, Quarta e Sexta', time: '17:00h', price: 'R$ 100,00 /mês', teacher: 'Mestre Bolivar', tag: 'tag-bjj', tagLabel: 'Jiu-Jitsu' },
    { name: 'Jiu-Jitsu Noturno', days: 'Segunda, Quarta e Sexta', time: '19:00h', price: 'R$ 100,00 /mês', teacher: 'Mestre Bolivar', tag: 'tag-bjj', tagLabel: 'Jiu-Jitsu' }
  ],
  ter: [
    { name: 'Jiu-Jitsu Almoço', days: 'Terças e Quintas', time: '12:00h', price: 'R$ 90,00 /mês', teacher: 'Mestre Bolivar', tag: 'tag-bjj', tagLabel: 'Jiu-Jitsu' },
    { name: 'Jiu-Jitsu Noturno', days: 'Terças e Quintas', time: '19:00h', price: 'R$ 90,00 /mês', teacher: 'Mestre Bolivar', tag: 'tag-bjj', tagLabel: 'Jiu-Jitsu' },
    { name: 'Boxe Noturno', days: 'Terças e Quintas', time: '19:00h', price: 'R$ 90,00 /mês', teacher: 'Mestre Bolivar', tag: 'tag-boxe', tagLabel: 'Boxe' }
  ],
  todos: [
    { name: 'Plano Passe Livre (BJJ & Boxe)', days: 'Segunda a Sexta (Todos os dias)', time: 'Todos os Horários', price: 'R$ 120,00 /mês', teacher: 'Mestre Bolivar', tag: 'tag-func', tagLabel: 'Livre Acesso' },
    { name: 'Plano Família (3 pessoas)', days: 'Livre Escolha', time: 'Todos os Horários', price: 'R$ 280,00 /mês', teacher: 'Mestre Bolivar', tag: 'tag-bjj', tagLabel: 'Família' },
    { name: 'Plano Casal (2 pessoas)', days: 'Livre Escolha', time: 'Todos os Horários', price: 'R$ 190,00 /mês', teacher: 'Mestre Bolivar', tag: 'tag-boxe', tagLabel: 'Casal' }
  ]
};

// Render Modalidades Cards
function renderModalidades() {
  const container = document.getElementById('modalidadesGrid');
  if (!container) return;

  container.innerHTML = modalidadesData.map(item => `
    <div class="modality-card">
      <div class="modality-icon">
        <i data-lucide="${item.icon}"></i>
      </div>
      <h3 class="modality-title">${item.title}</h3>
      <p class="modality-desc">${item.desc}</p>
      <div class="modality-meta">
        <span>⚡ Intensidade: <strong>${item.intensity}</strong></span>
        <span>🕒 <strong>${item.target}</strong></span>
      </div>
    </div>
  `).join('');
}

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
      <td>${item.days}</td>
      <td><span class="badge-pill">${item.time}</span></td>
      <td><span class="price-highlight">${item.price}</span></td>
      <td>${item.teacher}</td>
      <td>
        <button class="btn btn-secondary btn-sm quick-book-btn" data-modality="${item.name}">
          Agendar
        </button>
      </td>
    </tr>
  `).join('');

  // Attach click listeners to quick book buttons
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

// Calculator Logic (Lab Section)
function setupCalculator() {
  const form = document.getElementById('labForm');
  if (!form) return;

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const weight = parseFloat(document.getElementById('userWeight').value);
    const height = parseFloat(document.getElementById('userHeight').value) / 100;
    const goal = document.getElementById('userGoal').value;

    if (!weight || !height) return;

    const bmi = (weight / (height * height)).toFixed(1);
    let category = 'Atleta em Potencial';
    let calories = '750 - 950 kcal';
    let recommendedModality = 'Jiu-Jitsu (BJJ)';
    let recDesc = 'Excelente para queima calórica intensa, fortalecimento funcional e agilidade.';

    if (goal === 'perda_peso') {
      recommendedModality = 'Boxe & Muay Thai';
      calories = '850 - 1100 kcal';
      recDesc = 'Treino aeróbico de alta intensidade e gasto calórico máximo.';
    } else if (goal === 'defesa') {
      recommendedModality = 'Jiu-Jitsu (BJJ) Mestre Bolivar';
      calories = '700 - 900 kcal';
      recDesc = 'Técnica de alavanca, raspagem e controle no solo.';
    }

    document.getElementById('resultPlaceholder').classList.add('hidden');
    document.getElementById('resultContent').classList.remove('hidden');

    document.getElementById('resBMI').textContent = bmi;
    document.getElementById('resCalories').textContent = calories;
    document.getElementById('resCategory').textContent = category;
    document.getElementById('resModalidade').textContent = recommendedModality;
    document.getElementById('resDesc').textContent = recDesc;

    confetti({ particleCount: 50, spread: 60, origin: { y: 0.7 } });
  });

  const bookRecBtn = document.getElementById('bookRecommendedBtn');
  if (bookRecBtn) {
    bookRecBtn.addEventListener('click', () => {
      const rec = document.getElementById('resModalidade').textContent;
      openModalWithModality(rec);
    });
  }
}

// Booking Modal
function setupBookingModal() {
  const modal = document.getElementById('bookingModal');
  const openBtn = document.getElementById('openScheduleModal');
  const closeBtn = document.getElementById('closeBookingModal');
  const heroCTA = document.getElementById('heroCTA');
  const bookingForm = document.getElementById('bookingForm');

  function openModal() {
    modal.classList.remove('hidden');
  }

  function closeModal() {
    modal.classList.add('hidden');
  }

  if (openBtn) openBtn.addEventListener('click', openModal);
  if (heroCTA) heroCTA.addEventListener('click', openModal);
  if (closeBtn) closeBtn.addEventListener('click', closeModal);

  modal.addEventListener('click', (e) => {
    if (e.target === modal) closeModal();
  });

  if (bookingForm) {
    bookingForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const name = document.getElementById('bookName').value;
      const modality = document.getElementById('bookModality').value;

      confetti({
        particleCount: 120,
        spread: 80,
        origin: { y: 0.6 }
      });

      alert(`OSS! 🥋 Parabéns, ${name}! Seu agendamento para ${modality} foi realizado com sucesso! Nossa equipe do Mestre Bolivar entrará em contato via WhatsApp.`);
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
  modal.classList.remove('hidden');
}

// Login Modal Setup
function setupLoginModal() {
  const loginModal = document.getElementById('loginModal');
  const openLoginBtn = document.getElementById('openLoginModalBtn');
  const closeLoginBtn = document.getElementById('closeLoginModal');
  const loginForm = document.getElementById('loginForm');
  const dashView = document.getElementById('studentDashboardView');
  const logoutBtn = document.getElementById('logoutStudentBtn');

  function openLogin() {
    loginModal.classList.remove('hidden');
  }

  function closeLogin() {
    loginModal.classList.add('hidden');
  }

  if (openLoginBtn) openLoginBtn.addEventListener('click', openLogin);
  if (closeLoginBtn) closeLoginBtn.addEventListener('click', closeLogin);

  loginModal.addEventListener('click', (e) => {
    if (e.target === loginModal) closeLogin();
  });

  if (loginForm) {
    loginForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const cpf = document.getElementById('loginCpf').value;
      
      // Simulate authentication
      confetti({ particleCount: 80, spread: 70, origin: { y: 0.5 } });
      loginForm.classList.add('hidden');
      dashView.classList.remove('hidden');
    });
  }

  if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
      dashView.classList.add('hidden');
      loginForm.classList.remove('hidden');
    });
  }
}

// DOM Loaded
document.addEventListener('DOMContentLoaded', () => {
  renderModalidades();
  renderSchedule('seg');
  setupScheduleFilters();
  setupPlanButtons();
  setupCalculator();
  setupBookingModal();
  setupLoginModal();
  initIcons();
});

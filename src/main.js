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
  Sun
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
      Sun
    }
  });
}

// Data: Modalidades
const modalidadesData = [
  {
    icon: 'swords',
    title: 'Jiu-Jitsu (BJJ)',
    desc: 'Arte suave focada em alavancagens, raspagens, quedas e finalizações no solo (Gi & No-Gi).',
    intensity: 'Alta',
    target: 'Defesa & Combate'
  },
  {
    icon: 'flame',
    title: 'Muay Thai & Kickboxing',
    desc: 'A arte das 8 armas: punhos, cotovelos, joelhos e canelas para condicionamento extremo.',
    intensity: 'Muito Alta',
    target: 'Queima Calórica'
  },
  {
    icon: 'target',
    title: 'Boxe Tradicional',
    desc: 'Nobre arte dos punhos. Melhore reflexo, esquivas, agilidade e força de impacto.',
    intensity: 'Alta',
    target: 'Agilidade & Foco'
  },
  {
    icon: 'dumbbell',
    title: 'Treino Funcional & CT',
    desc: 'Preparação física específica para luta, estabilidade de core, força explosiva e cárdio.',
    intensity: 'Personalizada',
    target: 'Condicionamento'
  },
  {
    icon: 'trophy',
    title: 'MMA & Submissão',
    desc: 'Integração de grappling e trocação para transição completa de combate.',
    intensity: 'Máxima',
    target: 'Atletas & Avançado'
  },
  {
    icon: 'shield-check',
    title: 'Jiu-Jitsu Kids & Teen',
    desc: 'Formação marcial focada em disciplina, respeito, desenvolvimento motor e bullying-proof.',
    intensity: 'Moderada',
    target: 'Crianças & Jovens'
  }
];

// Data: Grade de Horários
const scheduleData = {
  seg: [
    { time: '06:00 - 07:15', name: 'Jiu-Jitsu (Matinal)', teacher: 'Mestre Bruno V.', level: 'Todos os Níveis', tag: 'tag-bjj', tagLabel: 'BJJ', seats: '4 vagas' },
    { time: '07:30 - 08:30', name: 'Treino Funcional CT', teacher: 'Prof. Carlos A.', level: 'Livre', tag: 'tag-func', tagLabel: 'Funcional', seats: '6 vagas' },
    { time: '12:00 - 13:00', name: 'Boxe Almoço', teacher: 'Prof. Marcos T.', level: 'Iniciante / Interm.', tag: 'tag-boxe', tagLabel: 'Boxe', seats: '2 vagas' },
    { time: '18:30 - 19:45', name: 'Muay Thai Noturno', teacher: 'Mestre Anderson R.', level: 'Todos os Níveis', tag: 'tag-muay', tagLabel: 'Muay Thai', seats: '5 vagas' },
    { time: '20:00 - 21:30', name: 'Jiu-Jitsu Avançado / Competition', teacher: 'Mestre Bruno V.', level: 'Graduados', tag: 'tag-bjj', tagLabel: 'BJJ', seats: 'Livre' }
  ],
  ter: [
    { time: '06:30 - 07:30', name: 'Muay Thai Matinal', teacher: 'Mestre Anderson R.', level: 'Todos os Níveis', tag: 'tag-muay', tagLabel: 'Muay Thai', seats: '3 vagas' },
    { time: '08:00 - 09:15', name: 'Jiu-Jitsu No-Gi (Sem Kimono)', teacher: 'Mestre Bruno V.', level: 'Interm. / Avançado', tag: 'tag-bjj', tagLabel: 'BJJ', seats: '5 vagas' },
    { time: '17:30 - 18:30', name: 'Jiu-Jitsu Kids', teacher: 'Profª. Fernanda S.', level: 'Infantil (5 a 12 anos)', tag: 'tag-bjj', tagLabel: 'Kids', seats: '4 vagas' },
    { time: '19:00 - 20:15', name: 'Boxe & Striking', teacher: 'Prof. Marcos T.', level: 'Todos os Níveis', tag: 'tag-boxe', tagLabel: 'Boxe', seats: '6 vagas' },
    { time: '20:30 - 21:45', name: 'Treino Funcional & Core', teacher: 'Prof. Carlos A.', level: 'Livre', tag: 'tag-func', tagLabel: 'Funcional', seats: '8 vagas' }
  ],
  qua: [
    { time: '06:00 - 07:15', name: 'Jiu-Jitsu (Matinal)', teacher: 'Mestre Bruno V.', level: 'Todos os Níveis', tag: 'tag-bjj', tagLabel: 'BJJ', seats: '5 vagas' },
    { time: '12:00 - 13:00', name: 'Muay Thai Express', teacher: 'Mestre Anderson R.', level: 'Iniciante', tag: 'tag-muay', tagLabel: 'Muay Thai', seats: '3 vagas' },
    { time: '18:30 - 19:45', name: 'Jiu-Jitsu Fundamental', teacher: 'Profª. Fernanda S.', level: 'Iniciantes / Faixa Branca', tag: 'tag-bjj', tagLabel: 'BJJ', seats: '7 vagas' },
    { time: '20:00 - 21:30', name: 'MMA & Wrestling Submissão', teacher: 'Mestre Bruno V.', level: 'Avançado', tag: 'tag-bjj', tagLabel: 'MMA', seats: '4 vagas' }
  ],
  qui: [
    { time: '06:30 - 07:30', name: 'Boxe Matinal', teacher: 'Prof. Marcos T.', level: 'Todos os Níveis', tag: 'tag-boxe', tagLabel: 'Boxe', seats: '4 vagas' },
    { time: '17:30 - 18:30', name: 'Jiu-Jitsu Teen', teacher: 'Profª. Fernanda S.', level: '13 a 17 anos', tag: 'tag-bjj', tagLabel: 'Teen', seats: '5 vagas' },
    { time: '19:00 - 20:15', name: 'Muay Thai Clinch & Sparring', teacher: 'Mestre Anderson R.', level: 'Interm. / Avançado', tag: 'tag-muay', tagLabel: 'Muay Thai', seats: '2 vagas' },
    { time: '20:30 - 21:45', name: 'Jiu-Jitsu All Belts', teacher: 'Mestre Bruno V.', level: 'Todos os Níveis', tag: 'tag-bjj', tagLabel: 'BJJ', seats: '8 vagas' }
  ],
  sex: [
    { time: '06:00 - 07:15', name: 'Jiu-Jitsu No-Gi', teacher: 'Mestre Bruno V.', level: 'Todos os Níveis', tag: 'tag-bjj', tagLabel: 'BJJ', seats: '6 vagas' },
    { time: '12:00 - 13:00', name: 'Treino Funcional de Sexta', teacher: 'Prof. Carlos A.', level: 'Livre', tag: 'tag-func', tagLabel: 'Funcional', seats: '10 vagas' },
    { time: '18:30 - 20:00', name: 'Open Mat (Treino Livre BJJ & Thai)', teacher: 'Equipe BJ Sports', level: 'Livre para Alunos', tag: 'tag-bjj', tagLabel: 'Open Mat', seats: 'Livre' }
  ],
  sab: [
    { time: '09:00 - 10:30', name: 'Aulão Especial de Sábado (BJJ)', teacher: 'Mestre Bruno V.', level: 'Todos os Níveis', tag: 'tag-bjj', tagLabel: 'BJJ', seats: 'Livre' },
    { time: '10:45 - 12:00', name: 'Sparring Sparring Striking (Boxe / Thai)', teacher: 'Mestre Anderson R.', level: 'Graduados', tag: 'tag-muay', tagLabel: 'Striking', seats: '4 vagas' }
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
        <span>🎯 Foco: <strong>${item.target}</strong></span>
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
    tbody.innerHTML = `<tr><td colspan="6" class="text-center">Nenhum treino agendado para este dia.</td></tr>`;
    return;
  }

  tbody.innerHTML = rows.map(item => `
    <tr>
      <td><strong>${item.time}</strong></td>
      <td>
        <span class="tag-badge ${item.tag}">${item.tagLabel}</span>
        <span style="margin-left: 8px;">${item.name}</span>
      </td>
      <td>${item.teacher}</td>
      <td><small class="text-muted">${item.level}</small></td>
      <td><span style="color: #4ade80; font-weight: 600;">${item.seats}</span></td>
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
    let calories = '650 - 850 kcal';
    let recommendedModality = 'Jiu-Jitsu (BJJ)';
    let recDesc = 'Excelente para queima calórica intensa, fortalecimento funcional e agilidade.';

    if (goal === 'perda_peso') {
      recommendedModality = 'Muay Thai & Treino Funcional';
      calories = '800 - 1050 kcal';
      recDesc = 'A combinação perfeita entre treinos aeróbicos intensos e fortalecimento de core.';
    } else if (goal === 'defesa') {
      recommendedModality = 'Jiu-Jitsu (BJJ) & Boxe';
      calories = '700 - 900 kcal';
      recDesc = 'Foco em controle de distância, gerenciamento de crise e submissão rápida.';
    } else if (goal === 'ganho_massa') {
      recommendedModality = 'Treino Funcional CT & Judo';
      calories = '600 - 750 kcal';
      recDesc = 'Treinamento de força explosiva, estabilização articular e hipertrofia funcional.';
    } else if (goal === 'competicao') {
      recommendedModality = 'MMA & Submissão Avançada';
      calories = '900 - 1200 kcal';
      recDesc = 'Preparação de alto rendimento com simulado de luta e periodização atlética.';
    }

    document.getElementById('resultPlaceholder').classList.add('hidden');
    document.getElementById('resultContent').classList.remove('hidden');

    document.getElementById('resBMI').textContent = bmi;
    document.getElementById('resCalories').textContent = calories;
    document.getElementById('resCategory').textContent = category;
    document.getElementById('resModalidade').textContent = recommendedModality;
    document.getElementById('resDesc').textContent = recDesc;

    // Trigger subtle confetti
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

// Modal Management
function setupModal() {
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

      // Celebrate booking with full confetti burst
      confetti({
        particleCount: 120,
        spread: 80,
        origin: { y: 0.6 }
      });

      alert(`OSS! 🎉 Parabéns, ${name}! Seu agendamento para a aula de ${modality} foi realizado com sucesso! Nossa equipe entrará em contato via WhatsApp.`);
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

// Theme Toggle
function setupThemeToggle() {
  const btn = document.getElementById('themeToggleBtn');
  if (!btn) return;

  btn.addEventListener('click', () => {
    document.body.classList.toggle('light-theme');
  });
}

// DOM Content Loaded
document.addEventListener('DOMContentLoaded', () => {
  renderModalidades();
  renderSchedule('seg');
  setupScheduleFilters();
  setupCalculator();
  setupModal();
  setupThemeToggle();
  initIcons();
});

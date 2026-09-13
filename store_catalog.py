"""Catálogo conceitual e oficial da loja BJ Sports."""

STORE_PRODUCTS = [
    {
        'id': 'BJJ-001',
        'sport': 'jiu-jitsu',
        'category': 'Kimonos',
        'name': 'Kimono BJ Sports Competition',
        'price': 439.90,
        'old_price': 479.90,
        'icon': '🥋',
        'image': 'img/store/kimono_preto.jpg',
        'badge': 'Oficial',
        'sizes': ['A0', 'A1', 'A2', 'A3', 'A4'],
        'description': 'Kimono de Jiu-Jitsu oficial BJ Sports. Modelagem anatômica para competição em trama leve trançada de alta durabilidade, lapela em EVA e bordados oficiais do CT Bolivar-JR.',
        'colors': [
            {
                'id': 'preto',
                'name': 'Preto',
                'hex': '#141416',
                'image': 'img/store/kimono_preto.jpg',
                'price': 459.90,
                'old_price': 499.90,
                'badge': 'Destaque'
            },
            {
                'id': 'branco',
                'name': 'Branco',
                'hex': '#ffffff',
                'image': 'img/store/kimono_branco.jpg',
                'price': 439.90,
                'old_price': 479.90,
                'badge': 'Oficial'
            },
            {
                'id': 'azul',
                'name': 'Azul Royal',
                'hex': '#0f34a2',
                'image': 'img/store/kimono_azul.jpg',
                'price': 449.90,
                'old_price': 489.90,
                'badge': 'Oficial'
            }
        ]
    },
    {
        'id': 'BJJ-004',
        'sport': 'jiu-jitsu',
        'category': 'No-Gi',
        'name': 'Rashguard Ranked Eagle (Manga Longa)',
        'price': 139.90,
        'old_price': 159.90,
        'icon': '👕',
        'image': 'img/store/rashguard_manga_longa.jpg',
        'badge': 'Lançamento',
        'sizes': ['P', 'M', 'G', 'GG', 'XG'],
        'description': 'Rashguard de alta compressão em vermelho e preto. Estampa exclusiva da águia no abdômen, marca BJ Sports e triângulo Bolivar-JR.',
        'colors': [
            {
                'id': 'preto-vermelho',
                'name': 'Preto / Vermelho',
                'hex': '#e50914',
                'image': 'img/store/rashguard_manga_longa.jpg',
                'price': 139.90,
                'old_price': 159.90,
                'badge': 'Lançamento'
            }
        ]
    },
    {
        'id': 'BJJ-005',
        'sport': 'jiu-jitsu',
        'category': 'No-Gi',
        'name': 'Fight Shorts Grappling (Preto/Vermelho)',
        'price': 129.90,
        'old_price': 149.90,
        'icon': '🩳',
        'image': 'img/store/fight_shorts_grappling.jpg',
        'badge': 'Destaque',
        'sizes': ['36', '38', '40', '42', '44', '46'],
        'description': 'Bermuda de luta sem bolsos, com logo soco no cós, grafismo lateral BJ Sports e fenda reforçada para mobilidade no No-Gi.'
    },
    {
        'id': 'BJJ-006',
        'sport': 'jiu-jitsu',
        'category': 'No-Gi',
        'name': 'Fight Shorts Pro Brasil BJ Sports',
        'price': 139.90,
        'old_price': 159.90,
        'icon': '🩳',
        'image': 'img/store/fight_shorts_pro.jpg',
        'badge': 'Edição Especial',
        'sizes': ['36', '38', '40', '42', '44', '46'],
        'description': 'Bermuda pro com faixas laterais em vermelho, inscrição JIU-JITSU, bandeira do Brasil e ajuste com cordão duplo.'
    },
    {
        'id': 'BJJ-007',
        'sport': 'jiu-jitsu',
        'category': 'Vestuário',
        'name': 'Camiseta de Treino Camuflada BJ Sports',
        'price': 89.90,
        'old_price': 109.90,
        'icon': '👕',
        'image': 'img/store/camisa_treino_camuflada.jpg',
        'badge': 'Novo',
        'sizes': ['P', 'M', 'G', 'GG', 'XG'],
        'description': 'Camiseta dry-fit oficial com detalhes camuflados em vermelho e preto. Respirabilidade máxima para o condicionamento físico.'
    },
    {
        'id': 'BJJ-008',
        'sport': 'jiu-jitsu',
        'category': 'Vestuário',
        'name': 'Camiseta Casual BJ Sports (Preta)',
        'price': 79.90,
        'old_price': 99.90,
        'icon': '👕',
        'image': 'img/store/camiseta_preta_mockup.jpg',
        'badge': 'Casual',
        'sizes': ['P', 'M', 'G', 'GG', 'XG'],
        'description': 'Camiseta 100% algodão penteado com corte moderno e branding minimalista BJ Sports.'
    },
    {
        'id': 'BJJ-009',
        'sport': 'jiu-jitsu',
        'category': 'Acessórios BJJ',
        'name': 'Faixa de Graduação BJJ',
        'price': 79.90,
        'icon': '🎗️',
        'badge': 'Oficial',
        'sizes': ['A0', 'A1', 'A2', 'A3', 'A4'],
        'description': 'Faixa resistente com tarja oficial adequada ao sistema de graduação IBJJF.'
    },
    {
        'id': 'BJJ-010',
        'sport': 'jiu-jitsu',
        'category': 'Acessórios BJJ',
        'name': 'Bolsa Tatame 35L BJ Sports',
        'price': 189.90,
        'old_price': 219.90,
        'icon': '🎒',
        'badge': 'Tático',
        'sizes': ['Único (35L)'],
        'description': 'Mochila tática 35L com compartimento ventilado para kimono e bolsos impermeáveis para acessórios.'
    },
    {
        'id': 'BOX-001',
        'sport': 'boxe',
        'category': 'Luvas',
        'name': 'Luva Pro Sparring 16oz',
        'price': 399.90,
        'old_price': 449.90,
        'icon': '🥊',
        'badge': 'Destaque',
        'sizes': ['12 oz', '14 oz', '16 oz'],
        'description': 'Proteção multicamadas com espuma injetada e fecho em velcro reforçado para treinos pesados de sparring.'
    },
    {
        'id': 'BOX-002',
        'sport': 'boxe',
        'category': 'Luvas',
        'name': 'Luva Training Fit 12oz',
        'price': 249.90,
        'old_price': 289.90,
        'icon': '🥊',
        'badge': '',
        'sizes': ['10 oz', '12 oz', '14 oz'],
        'description': 'Modelo versátil para treinos em saco de pancadas, manoplas e aulas técnicas de Boxe e Muay Thai.'
    },
    {
        'id': 'BOX-003',
        'sport': 'boxe',
        'category': 'Proteção',
        'name': 'Capacete de Sparring Pro',
        'price': 279.90,
        'old_price': 319.90,
        'icon': '🪖',
        'badge': 'Segurança',
        'sizes': ['P', 'M', 'G'],
        'description': 'Proteção anatômica para queixo, pômulo e orelhas com regulagem tripla na nuca e topo.'
    },
    {
        'id': 'BOX-004',
        'sport': 'boxe',
        'category': 'Proteção',
        'name': 'Bandagem Elástica 4,5m (Par)',
        'price': 39.90,
        'icon': '🩹',
        'badge': '',
        'sizes': ['Par (4,5m)'],
        'description': 'Bandagens de alta elasticidade e respirabilidade para fixação das articulações da mão e punho.'
    },
    {
        'id': 'BOX-005',
        'sport': 'boxe',
        'category': 'Proteção',
        'name': 'Protetor Bucal Moldável Dual Density',
        'price': 59.90,
        'icon': '🛡️',
        'badge': '',
        'sizes': ['Adulto'],
        'description': 'Moldagem térmica dual density com canal de respiração frontal e estojo protetor antibacteriano.'
    },
    {
        'id': 'BOX-006',
        'sport': 'boxe',
        'category': 'Treinamento',
        'name': 'Manopla Curva Focus Pad (Par)',
        'price': 189.90,
        'icon': '🎯',
        'badge': '',
        'sizes': ['Par'],
        'description': 'Alvo curvo em P.U. reforçado para treinos de velocidade, combinação de golpes e manopla.'
    },
    {
        'id': 'BOX-007',
        'sport': 'boxe',
        'category': 'Treinamento',
        'name': 'Corda Speed Rope Pro',
        'price': 69.90,
        'icon': '⚡',
        'badge': '',
        'sizes': ['Ajustável (3m)'],
        'description': 'Corda de pular com rolamento rápido e cabo metálico encapado ajustável para alto rendimento.'
    },
    {
        'id': 'BOX-008',
        'sport': 'boxe',
        'category': 'Treinamento',
        'name': 'Saco de Pancadas 90cm Heavy Bag',
        'price': 649.90,
        'old_price': 699.90,
        'icon': '💥',
        'badge': 'Sob encomenda',
        'sizes': ['90 × 30 cm'],
        'description': 'Estrutura ultra-resistente em couro ecológico com correntes e giratório de aço.'
    },
]

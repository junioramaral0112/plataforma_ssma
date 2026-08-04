"""
Plataforma SSMA — Configuração Centralizada
============================================
Todas as constantes, IDs de Google Sheets, dados das unidades e paths
de templates ficam centralizados aqui para facilitar manutenção.
"""

import os

# ---------------------------------------------------------------------------
# Google Sheets — ID da planilha central
# ---------------------------------------------------------------------------
# Esta é a ÚNICA planilha que o sistema consulta.
# Abas internas esperadas:
#   Colaboradores | Cargos | ASOs | Banco_APRs | [futuras...]
SHEET_ID: str = "SEU_SHEET_ID_CENTRAL_AQUI"

# ---------------------------------------------------------------------------
# Abas da planilha (nomes exatos conforme aparecem no Google Sheets)
# ---------------------------------------------------------------------------
ABA_COLABORADORES: str = "Colaboradores"
ABA_CARGOS: str = "Cargos"
ABA_ASOS: str = "ASOs"
ABA_BANCO_APRS: str = "Banco_APRs"

# Colunas esperadas em cada aba (para validação e mapeamento):
COLS_COLABORADORES: list[str] = [
    "Nome", "Cargo", "Setor", "Unidade", "Matrícula", "CPF", "Filial"
]
COLS_CARGOS: list[str] = [
    "Cargo", "EPI_Obrigatorio", "NR_Associada", "Ficha_EPI_Aba"
]
COLS_ASOS: list[str] = [
    "Nome", "Cargo", "Setor", "Unidade", "Tipo_Exame", "Data_Exame",
    "Vencimento", "Status"
]
COLS_BANCO_APRS: list[str] = [
    "Atividade", "Tarefa", "Risco", "Acoes"
]

# ---------------------------------------------------------------------------
# Unidades / Filiais
# ---------------------------------------------------------------------------
UNIDADES: dict[str, dict[str, str]] = {
    "SÃO JOSÉ": {
        "cnpj": "00.000.000/0001-01",
        "endereco": "Rua Exemplo, 123 — São José/SC",
    },
    "CHAPECÓ": {
        "cnpj": "00.000.000/0002-02",
        "endereco": "Av. Chapecó, 456 — Chapecó/SC",
    },
    "SÃO LEOPOLDO": {
        "cnpj": "00.000.000/0003-03",
        "endereco": "Rua São Leopoldo, 789 — São Leopoldo/RS",
    },
    "JOINVILLE": {
        "cnpj": "00.000.000/0004-04",
        "endereco": "Rua Joinville, 101 — Joinville/SC",
    },
    "PARANÁ": {
        "cnpj": "00.000.000/0005-05",
        "endereco": "Av. Paraná, 202 — Curitiba/PR",
    },
    "SÃO PAULO": {
        "cnpj": "00.000.000/0006-06",
        "endereco": "Rua SP, 303 — São Paulo/SP",
    },
    "MINAS GERAIS": {
        "cnpj": "00.000.000/0007-07",
        "endereco": "Av. Minas, 404 — Belo Horizonte/MG",
    },
    "ITAJAÍ": {
        "cnpj": "00.000.000/0008-08",
        "endereco": "Rua Itajaí, 505 — Itajaí/SC",
    },
}

# ---------------------------------------------------------------------------
# Templates de documentos (relativos à raiz do projeto)
# ---------------------------------------------------------------------------
BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR: str = os.path.join(BASE_DIR, "assets", "templates")

TEMPLATE_FICHA_EPI: str = os.path.join(TEMPLATES_DIR, "template_ficha.docx")
TEMPLATE_OS_JUNIOR: str = os.path.join(TEMPLATES_DIR, "template_os_junior.docx")
TEMPLATE_OS_SIMONE: str = os.path.join(TEMPLATES_DIR, "template_os_simone.docx")
TEMPLATE_NR06_JUNIOR: str = os.path.join(TEMPLATES_DIR, "template_nr06_junior.pptx")
TEMPLATE_NR06_SIMONE: str = os.path.join(TEMPLATES_DIR, "template_nr06_simone.pptx")
TEMPLATE_ATS: str = os.path.join(TEMPLATES_DIR, "template_ats.docx")
TEMPLATE_ASO: str = os.path.join(TEMPLATES_DIR, "template_aso.docx")

# ---------------------------------------------------------------------------
# Histórico / persistência local
# ---------------------------------------------------------------------------
DATA_DIR: str = os.path.join(BASE_DIR, "data")
HISTORICO_AGENDADOS_PATH: str = os.path.join(DATA_DIR, "historico_agendados.json")

# ---------------------------------------------------------------------------
# Técnicos (para assinatura nos documentos)
# ---------------------------------------------------------------------------
TECNICOS: dict[str, dict[str, str]] = {
    "Junior": {
        "nome": "Dilceu Amaral Jr",
        "registro": "TST-XXXX",
        "template_os": TEMPLATE_OS_JUNIOR,
        "template_nr06": TEMPLATE_NR06_JUNIOR,
    },
    "Simone": {
        "nome": "Simone",
        "registro": "TST-YYYY",
        "template_os": TEMPLATE_OS_SIMONE,
        "template_nr06": TEMPLATE_NR06_SIMONE,
    },
}

# ---------------------------------------------------------------------------
# Checklist de equipamentos (para módulo APR)
# ---------------------------------------------------------------------------
BANCO_EQUIPAMENTOS: dict[str, list[str]] = {
    "Compressor de Ar": [
        "Filtro de ar limpo e em bom estado",
        "Válvula de segurança funcionando",
        "Mangueiras sem rachaduras ou vazamentos",
        "Manômetro calibrado e legível",
        "Dreno do tanque funcionando",
        "Conexões elétricas seguras (ausência de fios expostos)",
        "Proteção de polias e correias instalada",
        "Nível de óleo adequado (se aplicável)",
        "Base estável e fixação adequada",
        "Ruído dentro dos limites aceitáveis",
    ],
    "Extensão Elétrica": [
        "Cabo sem emendas ou reparos inadequados",
        "Plugues e tomadas sem sinais de aquecimento",
        "Bitola compatível com a carga",
        "Isolação íntegra, sem cortes ou ressecamento",
        "Comprimento adequado à aplicação",
        "Dispositivo DR (diferencial residual) presente",
        "Aterramento funcional",
        "Identificação/etiqueta de inspeção visível",
    ],
    "Furadeira a Bateria": [
        "Bateria carregando corretamente e sem estufamento",
        "Gatilho de acionamento com retorno automático",
        "Mandril firme, sem folga excessiva",
        "Carcaça sem rachaduras ou danos",
        "Luz indicadora de funcionamento ativa",
        "Sistema de freio motor operante",
        "Botão de reversão funcional",
        "Empunhadura antiderrapante íntegra",
    ],
    "Furadeira Elétrica": [
        "Cabo de alimentação sem cortes ou reparos",
        "Plugue de três pinos (aterramento presente)",
        "Gatilho com retorno automático",
        "Mandril centralizado e sem folga",
        "Escovas do motor dentro da vida útil",
        "Carcaça isolante sem rachaduras",
        "Dispositivo de fixação de brocas funcional",
        "Ruído e vibração dentro do normal",
    ],
    "Lavadora de Alta Pressão": [
        "Mangueira de alta pressão sem bolhas ou cortes",
        "Gatilho da pistola com trava de segurança",
        "Bicos de pulverização desobstruídos",
        "Filtro de entrada de água limpo",
        "Conexão elétrica com DR",
        "Válvula de alívio (bypass) operante",
        "Carcaça e rodízios em bom estado",
        "Nível de óleo da bomba verificado",
    ],
    "Macaco Hidráulico Garrafa": [
        "Cilindro sem vazamento de óleo",
        "Haste de elevação sem corrosão ou riscos profundos",
        "Válvula de alívio calibrada",
        "Base de apoio firme e nivelada",
        "Capacidade nominal legível na etiqueta",
        "Alavanca de acionamento presente e reta",
        "Sistema de retorno lento controlado",
        "Gaxetas e retentores sem desgaste visível",
    ],
    "Macaco Hidráulico Jacaré": [
        "Chassis e rodas em bom estado",
        "Braço de elevação sem trincas",
        "Cilindro hidráulico sem vazamentos",
        "Válvula de segurança operante",
        "Pedal de acionamento firme",
        "Alavanca de liberação controlada",
        "Etiqueta de capacidade visível",
        "Giro livre das rodas dianteiras",
    ],
    "Parafusadeira": [
        "Bateria sem deformações ou superaquecimento",
        "Mandril de encaixe rápido funcional",
        "Gatilho com controle de velocidade",
        "Seletor de torque operante",
        "Luz LED de indicação funcionando",
        "Carcaça sem danos estruturais",
        "Empunhadura emborrachada íntegra",
    ],
    "Prensa Hidráulica": [
        "Manômetro calibrado e dentro do prazo",
        "Mangueiras sem trincas ou bolhas",
        "Válvula de controle com retorno suave",
        "Proteção contra sobrepressão ativa",
        "Base da prensa nivelada e fixada",
        "Guias da mesa sem folga excessiva",
        "Cilindro sem vazamentos aparentes",
        "Sistema elétrico com botão de emergência",
    ],
    "Talha": [
        "Corrente de carga sem elos abertos ou desgastados",
        "Gancho superior com trava de segurança",
        "Gancho inferior com trava de segurança",
        "Catraca e lingueta de retenção funcionando",
        "Teste de carga atualizado (etiqueta)",
        "Trilho ou viga de sustentação íntegro",
        "Roldanas e polias sem folga excessiva",
        "Carcaça da talha sem trincas ou corrosão",
        "Comando remoto (se elétrica) com botoeira íntegra",
        "Freio de retenção de carga operante",
    ],
}

# ---------------------------------------------------------------------------
# Módulo Asaas (Assinatura) — endpoints e chaves (placeholder)
# ---------------------------------------------------------------------------
ASAAS_API_KEY: str = os.getenv("ASAAS_API_KEY", "sua-chave-aqui")
ASAAS_BASE_URL: str = "https://api.asaas.com/v3"

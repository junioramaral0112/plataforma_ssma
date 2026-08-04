# 🛡️ Plataforma SSMA

**Gestão Integrada de Segurança, Saúde e Meio Ambiente**

Plataforma corporativa unificada em Streamlit para gerenciamento de ASOs,
emissão de kits documentais e geração de APR/ATS.

---

## 📦 Módulos

| # | Módulo | Descrição |
|---|--------|-----------|
| 📊 | **Dashboard de ASOs** | Alertas de vencimento, KPI por unidade, busca ativa, fichas de agendamento |
| 📄 | **Kits Documentais** | Emissão de OS, Ficha de EPI e Certificado NR-06 por colaborador |
| 🛠️ | **Gerador APR/ATS** | Análise Preliminar de Risco com dados do Google Sheets + Checklist Excel |

---

## 🚀 Instalação

### 1. Clone o repositório

```bash
git clone <seu-repo> D:\projetos\plataforma_ssma
cd D:\projetos\plataforma_ssma
```

### 2. Crie o ambiente virtual

```bash
python -m venv venv
venv\Scripts\activate     # Windows
# ou
source venv/bin/activate  # Linux/Mac
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure a planilha Google Sheets

Edite `config.py` e defina o **SHEET_ID** da sua planilha central:

```python
SHEET_ID = "1ABCxyz123SeuIDaqui789"
```

A planilha deve conter as seguintes **abas**:

| Aba | Colunas Esperadas |
|-----|-------------------|
| `Colaboradores` | Nome, Cargo, Setor, Unidade, Matrícula, CPF, Filial |
| `Cargos` | Cargo, EPI_Obrigatorio, NR_Associada, Ficha_EPI_Aba |
| `ASOs` | Nome, Cargo, Setor, Unidade, Tipo_Exame, Data_Exame, Vencimento, Status |
| `Banco_APRs` | Atividade, Tarefa, Risco, Ações |

> 🔒 **Importante:** A planilha deve estar pública (Anyone with the link can view)
> ou usar o endpoint CSV/GVIZ que não requer autenticação OAuth.

### 5. Adicione os templates

Coloque os arquivos de template em `assets/templates/`:

```
assets/templates/
├── template_ficha.docx
├── template_os_junior.docx
├── template_os_simone.docx
├── template_nr06_junior.pptx
├── template_nr06_simone.pptx
└── template_ats.docx
```

### 6. Execute

```bash
streamlit run app.py
```

Ou use o atalho: **`iniciar_plataforma.bat`** (Windows)

---

## 📁 Estrutura do Projeto

```
plataforma_ssma/
├── app.py                          # Entrada principal (Home)
├── config.py                       # Configurações centralizadas
├── requirements.txt                # Dependências
├── iniciar_plataforma.bat          # Launcher Windows
├── .gitignore
│
├── pages/                          # Streamlit auto-detecta
│   ├── 01_📊_Dashboard.py
│   ├── 02_📄_Kits_Documentais.py
│   └── 03_🛠️_Gerador_APR.py
│
├── src/
│   ├── data/
│   │   └── sheets.py              # Camada de dados (Google Sheets)
│   ├── services/
│   │   ├── aso_service.py         # Lógica de ASOs
│   │   ├── docs_service.py        # Geração de documentos
│   │   ├── apr_service.py         # APR/ATS e Checklist
│   │   └── asaas_service.py       # Integração Asaas (assinaturas)
│   ├── components/
│   │   ├── sidebar.py             # Sidebar unificada
│   │   ├── kpi_cards.py           # Cards de métricas
│   │   └── docx_utils.py          # Utilitários DOCX/PPTX
│   └── pages/
│       ├── dashboard.py           # Lógica do Dashboard
│       ├── kits_documentais.py    # Lógica dos Kits
│       └── gerador_apr.py         # Lógica do APR/ATS
│
├── assets/
│   ├── images/                    # Logos e ícones
│   └── templates/                 # Templates .docx/.pptx
│
├── data/
│   └── historico_agendados.json   # Persistência local de agendamentos
│
└── .streamlit/
    └── config.toml                # Tema e configurações Streamlit
```

---

## 🔐 Modelo de Curadoria

O **administrador** mantém controle exclusivo sobre:

- 🗂️ **Planilha Central** — Todas as abas (Colaboradores, Cargos, ASOs, Banco_APRs)
- 📄 **Templates** — Arquivos .docx/.pptx corporativos
- ⚙️ **Configurações** — SHEET_ID, unidades, planos no `config.py`

O **usuário final** (cliente) apenas:
- Seleciona unidade e colaboradores
- Gera documentos e checklists
- Acompanha vencimentos de ASOs via dashboard

---

## 💳 Integração Asaas

A plataforma está preparada para **assinatura via Asaas** (API v3).

### Configurar

1. Crie uma conta no [Asaas](https://www.asaas.com)
2. Obtenha a API Key em: Configurações → Integrações → API
3. Defina a variável de ambiente:

```bash
set ASAAS_API_KEY=sua-chave-aqui    # Windows
export ASAAS_API_KEY=sua-chave-aqui  # Linux/Mac
```

### Planos

| Plano | Valor | Módulos | Trial |
|-------|-------|---------|-------|
| Completo | R$ 590/mês | Todos (Dashboard + Kits + APR/ATS + Checklist) | 7 dias |

**Sem taxa de implantação.** Acesso ilimitado a todos os módulos.

---

## 🛠️ Stack Tecnológica

- **Streamlit** — Framework da interface web
- **Pandas** — Manipulação de dados
- **python-docx** / **python-pptx** — Geração de documentos Office
- **openpyxl** — Geração de planilhas Excel
- **Google Sheets (CSV/GVIZ)** — Base de dados central
- **Asaas API v3** — Gestão de assinaturas e cobranças

---

## 📝 Licença

Uso proprietário. Desenvolvido por **Dilceu Junior**.

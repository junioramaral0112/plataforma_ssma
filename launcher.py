"""
🛡️ Plataforma SSMA — Vitrine Central
======================================
Launcher corporativo que serve como portal de acesso aos 3 módulos
independentes:

  1. 📊 Gestão de ASOs — Monitoramento de exames ocupacionais
  2. 📄 Kits Documentais — OS, Ficha EPI e Certificado NR-06
  3. 🛠️ Gerador APR/ATS — Análise de Risco + Checklist

Cada módulo roda no seu próprio repositório/deploy.
Este launcher é apenas a "vitrine" de acesso.
"""

from __future__ import annotations

import streamlit as st

# ---------------------------------------------------------------------------
# Configuração da página
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Plataforma SSMA — Gestão Integrada",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# CSS Corporativo
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Esconde sidebar */
    [data-testid="stSidebar"] { display: none; }
    [data-testid="stSidebarCollapsedControl"] { display: none; }

    /* Fundo */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
    }

    /* Header */
    .launcher-header {
        text-align: center;
        padding: 40px 20px 20px;
    }
    .launcher-header h1 {
        font-size: 2.5rem;
        font-weight: 800;
        color: #f1f5f9;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .launcher-header .subtitle {
        font-size: 1.1rem;
        color: #94a3b8;
        margin-top: 8px;
    }

    /* Grid de cards */
    .cards-grid {
        display: flex;
        gap: 24px;
        justify-content: center;
        flex-wrap: wrap;
        padding: 20px 40px;
        max-width: 1100px;
        margin: 0 auto;
    }

    /* Card individual */
    .card {
        flex: 1;
        min-width: 280px;
        max-width: 340px;
        background: rgba(255,255,255,0.06);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 16px;
        padding: 32px 28px;
        text-align: center;
        transition: all 0.3s ease;
        cursor: pointer;
        text-decoration: none;
        color: inherit;
    }
    .card:hover {
        transform: translateY(-6px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.3);
        border-color: rgba(255,255,255,0.25);
    }
    .card-icon {
        font-size: 3.5rem;
        margin-bottom: 16px;
        display: block;
    }
    .card h3 {
        color: #f1f5f9;
        font-size: 1.3rem;
        margin: 0 0 12px;
        font-weight: 700;
    }
    .card p {
        color: #94a3b8;
        font-size: 0.9rem;
        line-height: 1.5;
        margin: 0 0 16px;
    }
    .card .features {
        text-align: left;
        color: #94a3b8;
        font-size: 0.8rem;
        padding-left: 1.2rem;
        margin: 0 0 20px;
    }
    .card .features li {
        margin-bottom: 4px;
    }

    /* Botão do card */
    .card-btn {
        display: inline-block;
        padding: 10px 24px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.9rem;
        text-decoration: none;
        transition: all 0.2s;
        border: none;
    }
    .btn-blue {
        background: #3b82f6;
        color: white;
    }
    .btn-blue:hover { background: #2563eb; }
    .btn-green {
        background: #10b981;
        color: white;
    }
    .btn-green:hover { background: #059669; }
    .btn-amber {
        background: #f59e0b;
        color: #1e293b;
    }
    .btn-amber:hover { background: #d97706; }

    /* Badge */
    .badge {
        display: inline-block;
        background: rgba(255,255,255,0.1);
        color: #94a3b8;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.7rem;
        margin-bottom: 16px;
    }

    /* Footer */
    .launcher-footer {
        text-align: center;
        padding: 40px 20px;
        color: #475569;
        font-size: 0.75rem;
    }
    .launcher-footer strong { color: #64748b; }

    /* Plano info */
    .plano-bar {
        text-align: center;
        padding: 12px 20px;
        margin: 0 40px;
        border-radius: 10px;
        background: rgba(59,130,246,0.1);
        border: 1px solid rgba(59,130,246,0.2);
        max-width: 500px;
        margin-left: auto;
        margin-right: auto;
    }
    .plano-bar span {
        color: #60a5fa;
        font-weight: 600;
        font-size: 0.95rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# URLs dos módulos (atualize com os links reais de deploy)
# ---------------------------------------------------------------------------
URL_ASO = "https://seu-app-aso.streamlit.app"
URL_DOCS = "https://seu-app-docs.streamlit.app"
URL_APR = "https://seu-app-apr.streamlit.app"

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="launcher-header">
        <h1>🛡️ Plataforma SSMA</h1>
        <p class="subtitle">
            Gestão Integrada de Segurança, Saúde e Meio Ambiente<br>
            <span style="font-size:0.85rem;">Escolha o módulo desejado abaixo</span>
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Barra de plano
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="plano-bar">
        <span>💳 Plano Único: R$ 590/mês</span> &nbsp;·&nbsp;
        <span style="color:#94a3b8;font-weight:400;">Sem taxa de implantação</span> &nbsp;·&nbsp;
        <span style="color:#34d399;font-weight:400;">7 dias de trial</span>
    </div>
    <br>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Cards dos Módulos
# ---------------------------------------------------------------------------
st.markdown('<div class="cards-grid">', unsafe_allow_html=True)

# ----- Card 1: ASO -----
st.markdown(
    f"""
    <a href="{URL_ASO}" target="_blank" class="card">
        <span class="card-icon">📊</span>
        <h3>Gestão de ASOs</h3>
        <span class="badge">Saúde Ocupacional</span>
        <p>Monitoramento completo de exames ocupacionais com alertas de vencimento.</p>
        <ul class="features">
            <li>🔴 Alertas de vencimento (vermelho/âmbar/verde)</li>
            <li>📋 KPIs por unidade</li>
            <li>📝 Fichas de agendamento</li>
            <li>🔎 Busca ativa de colaboradores</li>
        </ul>
        <span class="card-btn btn-blue">Acessar →</span>
    </a>
    """,
    unsafe_allow_html=True,
)

# ----- Card 2: Kits Documentais -----
st.markdown(
    f"""
    <a href="{URL_DOCS}" target="_blank" class="card">
        <span class="card-icon">📄</span>
        <h3>Kits Documentais</h3>
        <span class="badge">Documentação</span>
        <p>Emissão automática de OS, Ficha de EPI e Certificado NR-06.</p>
        <ul class="features">
            <li>📋 Ordem de Serviço</li>
            <li>🦺 Ficha de EPI por cargo</li>
            <li>📜 Certificado NR-06</li>
            <li>📦 Download em ZIP</li>
        </ul>
        <span class="card-btn btn-green">Acessar →</span>
    </a>
    """,
    unsafe_allow_html=True,
)

# ----- Card 3: APR/ATS -----
st.markdown(
    f"""
    <a href="{URL_APR}" target="_blank" class="card">
        <span class="card-icon">🛠️</span>
        <h3>Gerador APR / ATS</h3>
        <span class="badge">Segurança do Trabalho</span>
        <p>Análise Preliminar de Risco com banco de dados integrado.</p>
        <ul class="features">
            <li>📄 ATS em Word (tabela dinâmica)</li>
            <li>📋 Checklist de equipamentos</li>
            <li>🗂️ Banco de APRs no Google Sheets</li>
            <li>📥 Download Excel/Word</li>
        </ul>
        <span class="card-btn btn-amber">Acessar →</span>
    </a>
    """,
    unsafe_allow_html=True,
)

st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="launcher-footer">
        <strong>🛡️ Plataforma SSMA</strong> — Desenvolvido por <strong>Dilceu Junior</strong><br>
        Sistema Integrado de Segurança, Saúde e Meio Ambiente<br>
        © 2026 · Todos os direitos reservados · Assinatura via Asaas
    </div>
    """,
    unsafe_allow_html=True,
)

"""
Plataforma SSMA — Aplicação Principal
======================================
Plataforma unificada de Gestão de Segurança, Saúde e Meio Ambiente.

Módulos:
  1. 📊 Dashboard de ASOs — Monitoramento de exames ocupacionais
  2. 📄 Kits Documentais — Emissão de OS, Ficha EPI e NR-06
  3. 🛠️ Gerador APR/ATS — Análise de Risco e Checklist

Uso:
    streamlit run app.py
"""

from __future__ import annotations

import streamlit as st

# ---------------------------------------------------------------------------
# Configuração da página (DEVE ser a primeira chamada Streamlit)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Plataforma SSMA — Gestão Integrada",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# CSS Global
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Esconde a navegação padrão de páginas (usamos navegação customizada) */
    div[data-testid="stSidebarNav"] { display: none; }

    /* Scrollbar customizada */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #f1f5f9; }
    ::-webkit-scrollbar-thumb { background: #94a3b8; border-radius: 4px; }

    /* Links nos expanders */
    .stExpander a { color: #1a73e8; text-decoration: none; }

    /* Métricas */
    [data-testid="stMetricValue"] { font-size: 1.5rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Página Inicial (Home)
# ---------------------------------------------------------------------------
def main() -> None:
    """Renderiza a página inicial da plataforma."""

    # --- Sidebar ---
    with st.sidebar:
        st.markdown(
            """
            <div style="text-align:center; margin-bottom:20px;">
                <h1 style="color:#1a73e8; margin-bottom:2px; font-size:2rem;">🛡️ SSMA</h1>
                <p style="font-size:0.8rem; color:#64748b; margin:0;">
                    Segurança, Saúde e Meio Ambiente
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.divider()

        st.markdown("### 📌 Módulos Disponíveis")

        st.page_link("app.py", label="🏠 Início", use_container_width=True)
        st.page_link("pages/01_📊_Dashboard.py", label="📊 Dashboard de ASOs", use_container_width=True)
        st.page_link("pages/02_📄_Kits_Documentais.py", label="📄 Kits Documentais", use_container_width=True)
        st.page_link("pages/03_🛠️_Gerador_APR.py", label="🛠️ Gerador APR/ATS", use_container_width=True)

        st.divider()

        # Status da planilha
        from config import SHEET_ID
        sheet_ok = bool(SHEET_ID and SHEET_ID != "SEU_SHEET_ID_CENTRAL_AQUI")
        if sheet_ok:
            st.success("📊 Planilha conectada")
        else:
            st.warning("⚠️ Configure SHEET_ID")

        st.divider()

        st.markdown(
            """
            <div style="font-size:0.7rem; color:#94a3b8; text-align:center;">
            Desenvolvido por <strong>Dilceu Junior</strong><br>
            © 2026 Plataforma SSMA<br>
            <span style="font-size:0.6rem;">v1.0 — Assinatura via Asaas | R$ 590/mês</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ==================================================================
    # CONTEÚDO PRINCIPAL
    # ==================================================================
    st.title("🛡️ Plataforma SSMA")
    st.caption(
        "Gestão Integrada de Segurança, Saúde e Meio Ambiente — "
        "Solução corporativa completa para emissão de documentos, "
        "monitoramento de exames e análise de riscos. "
        "**Plano Único: R$ 590/mês · Sem taxa de implantação.**"
    )

    st.divider()

    # --- Cards dos Módulos ---
    col1, col2, col3 = st.columns(3, gap="medium")

    with col1:
        st.markdown(
            """
            <div style="
                background: linear-gradient(135deg, #1a73e8, #1557b0);
                border-radius: 12px;
                padding: 24px;
                color: white;
                min-height: 220px;
            ">
                <div style="font-size:2.5rem; margin-bottom:8px;">📊</div>
                <h3 style="color:white; margin:0 0 8px;">Dashboard de ASOs</h3>
                <p style="font-size:0.9rem; opacity:0.9;">
                    Alertas de vencimento, métricas por unidade,
                    busca ativa de colaboradores e fichas de agendamento.
                </p>
                <ul style="font-size:0.8rem; opacity:0.85; padding-left:1.2rem;">
                    <li>Cards de vencimento (vermelho/âmbar/verde)</li>
                    <li>KPIs por unidade</li>
                    <li>Histórico de agendamentos</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Acessar Dashboard", use_container_width=True, key="btn_dash"):
            st.switch_page("pages/01_📊_Dashboard.py")

    with col2:
        st.markdown(
            """
            <div style="
                background: linear-gradient(135deg, #10b981, #059669);
                border-radius: 12px;
                padding: 24px;
                color: white;
                min-height: 220px;
            ">
                <div style="font-size:2.5rem; margin-bottom:8px;">📄</div>
                <h3 style="color:white; margin:0 0 8px;">Kits Documentais</h3>
                <p style="font-size:0.9rem; opacity:0.9;">
                    Emissão de Ordem de Serviço, Ficha de EPI e
                    Certificado NR-06 por colaborador.
                </p>
                <ul style="font-size:0.8rem; opacity:0.85; padding-left:1.2rem;">
                    <li>Preenchimento automático via Google Sheets</li>
                    <li>Templates Junior / Simone</li>
                    <li>Download em ZIP com todos os docs</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Acessar Kits", use_container_width=True, key="btn_kits"):
            st.switch_page("pages/02_📄_Kits_Documentais.py")

    with col3:
        st.markdown(
            """
            <div style="
                background: linear-gradient(135deg, #f59e0b, #d97706);
                border-radius: 12px;
                padding: 24px;
                color: white;
                min-height: 220px;
            ">
                <div style="font-size:2.5rem; margin-bottom:8px;">🛠️</div>
                <h3 style="color:white; margin:0 0 8px;">Gerador APR/ATS</h3>
                <p style="font-size:0.9rem; opacity:0.9;">
                    Análise Preliminar de Risco com dados do Google Sheets,
                    geração de Word e Checklist de Equipamentos.
                </p>
                <ul style="font-size:0.8rem; opacity:0.85; padding-left:1.2rem;">
                    <li>Banco de APRs integrado à planilha</li>
                    <li>Checklist de equipamentos em Excel</li>
                    <li>Tabela dinâmica de tarefas/riscos/ações</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Acessar Gerador APR", use_container_width=True, key="btn_apr"):
            st.switch_page("pages/03_🛠️_Gerador_APR.py")

    st.divider()

    # --- Seção "Como Funciona" ---
    st.subheader("🔐 Como Funciona")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown(
            """
            **1. Planilha Central**
            Toda a base de dados (Colaboradores, Cargos, ASOs,
            Banco de APRs) fica no Google Sheets sob sua curadoria.
            O app apenas consulta — nunca altera a fonte.
            """
        )
    with col_b:
        st.markdown(
            """
            **2. Templates Protegidos**
            Os templates .docx/.pptx ficam no servidor,
            inacessíveis ao usuário final. Só o administrador
            mantém a curadoria dos documentos corporativos.
            """
        )
    with col_c:
        st.markdown(
            """
            **3. Assinatura via Asaas**
            Plano único de **R$ 590/mês** sem taxa de implantação.
            Acesso completo a todos os módulos com trial de 7 dias.
            Gestão de cobranças automatizada pelo Asaas.
            """
        )

    # --- Rodapé ---
    st.divider()
    st.markdown(
        """
        <div style="text-align:center; color:#94a3b8; font-size:0.75rem; margin-top:20px;">
        🛡️ <strong>Plataforma SSMA</strong> — Desenvolvido por <strong>Dilceu Junior</strong> |
        Sistema Integrado de Segurança, Saúde e Meio Ambiente | © 2026
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()

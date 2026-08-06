"""
Portal Central SSMA Macromaq — Launcher com Autenticação
==========================================================
- Login com senha padrão + troca obrigatória no primeiro acesso
- Validação financeira via API do Asaas (bloqueio por inadimplência)
- "Esqueci minha senha" para restaurar senha padrão
- Portal com 4 cards de acesso aos módulos (visível só se adimplente)
- Múltiplos acessos simultâneos permitidos
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
from datetime import datetime

import requests
import streamlit as st

# ==========================================================================
# CONFIGURAÇÃO DA PÁGINA (DEVE ser a primeira chamada Streamlit)
# ==========================================================================
st.set_page_config(
    page_title="Portal SSMA Macromaq",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ==========================================================================
# CONSTANTES
# ==========================================================================
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_DATA_DIR = os.path.join(_BASE_DIR, "data")
_USERS_FILE = os.path.join(_DATA_DIR, "usuarios.json")
_IMAGES_DIR = os.path.join(_BASE_DIR, "assets", "images")
_FUNDO_JPG = os.path.join(_IMAGES_DIR, "fundo.jpg")
_LOGO_PNG = os.path.join(_IMAGES_DIR, "logo.png")

# Credenciais padrão
DEFAULT_USER = "admin"
DEFAULT_PASS = "macromaq2026"

# Trial (dias de teste gratuito)
TRIAL_DIAS = 15

# Asaas
# --- LEITURA SEGURA DA API KEY DO ASAAS ---
try:
    ASAAS_API_KEY = os.getenv("ASAAS_API_KEY", st.secrets.get("ASAAS_API_KEY", ""))
except Exception:
    ASAAS_API_KEY = os.getenv("ASAAS_API_KEY", "")
ASAAS_BASE_URL = "https://api.asaas.com/v3"

# Links dos módulos
URL_ASO = "https://aso-gendamento.streamlit.app/"
URL_DOCS = "https://automacaodoc-macromaq.streamlit.app/"
URL_APR = "https://aprmacromaq.streamlit.app/"
URL_AUDIT = "https://riscos.streamlit.app/"


# ==========================================================================
# PERSISTÊNCIA DE USUÁRIOS (JSON)
# ==========================================================================
def _carregar_usuarios() -> dict:
    """Carrega o dicionário de usuários do arquivo JSON."""
    os.makedirs(_DATA_DIR, exist_ok=True)
    if not os.path.exists(_USERS_FILE):
        # Cria com usuário padrão
        default_data = {
            DEFAULT_USER: {
                "senha_hash": _hash_senha(DEFAULT_PASS),
                "senha_padrao": True,
                "criado_em": datetime.now().isoformat(),
            }
        }
        _salvar_usuarios(default_data)
        return default_data
    with open(_USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _salvar_usuarios(data: dict) -> None:
    """Persiste o dicionário de usuários em disco."""
    os.makedirs(_DATA_DIR, exist_ok=True)
    with open(_USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _hash_senha(senha: str) -> str:
    """Hash SHA-256 simples da senha."""
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()


def _verificar_senha(usuario: str, senha: str) -> bool:
    """Verifica se a senha confere para o usuário."""
    usuarios = _carregar_usuarios()
    user_data = usuarios.get(usuario)
    if not user_data:
        return False
    return user_data["senha_hash"] == _hash_senha(senha)


def _senha_eh_padrao(usuario: str) -> bool:
    """Retorna True se o usuário ainda estiver com a senha padrão."""
    usuarios = _carregar_usuarios()
    return usuarios.get(usuario, {}).get("senha_padrao", True)


def _alterar_senha(usuario: str, nova_senha: str) -> None:
    """Altera a senha do usuário e marca como não-padrão."""
    usuarios = _carregar_usuarios()
    if usuario in usuarios:
        usuarios[usuario]["senha_hash"] = _hash_senha(nova_senha)
        usuarios[usuario]["senha_padrao"] = False
        usuarios[usuario]["alterado_em"] = datetime.now().isoformat()
    _salvar_usuarios(usuarios)


def _restaurar_senha_padrao(usuario: str) -> None:
    """Restaura a senha para o valor padrão e marca como pendente de troca."""
    usuarios = _carregar_usuarios()
    if usuario in usuarios:
        usuarios[usuario]["senha_hash"] = _hash_senha(DEFAULT_PASS)
        usuarios[usuario]["senha_padrao"] = True
        usuarios[usuario]["restaurado_em"] = datetime.now().isoformat()
    _salvar_usuarios(usuarios)


def _dias_desde_cadastro(usuario: str) -> int:
    """Retorna quantos dias se passaram desde o cadastro do usuário."""
    usuarios = _carregar_usuarios()
    user_data = usuarios.get(usuario, {})
    criado_str = user_data.get("criado_em", "")
    if not criado_str:
        return 999  # sem data = assume fora do trial
    try:
        criado = datetime.fromisoformat(criado_str)
        return (datetime.now() - criado).days
    except Exception:
        return 999


def _dentro_do_trial(usuario: str) -> bool:
    """Retorna True se o usuário ainda está no período de trial gratuito."""
    return _dias_desde_cadastro(usuario) < TRIAL_DIAS


# ==========================================================================
# INTEGRAÇÃO ASAAS
# ==========================================================================
def _asaas_headers() -> dict:
    return {"access_token": ASAAS_API_KEY, "Content-Type": "application/json"}


@st.cache_data(ttl=120, show_spinner=False)
def _asaas_get(endpoint: str, params: dict | None = None) -> dict:
    """GET na API do Asaas com cache curto."""
    if not ASAAS_API_KEY:
        return {}
    try:
        resp = requests.get(
            f"{ASAAS_BASE_URL}/{endpoint}",
            headers=_asaas_headers(),
            params=params or {},
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return {}


def verificar_adimplencia(cpf_cnpj: str = "", email: str = "") -> dict:
    """Verifica se o cliente está adimplente na plataforma.

    VALIDAÇÃO ESTRITA: só libera acesso se a API do Asaas retornar
    pelo menos uma fatura com status RECEIVED ou CONFIRMED.
    Sem tolerância de trial, sem fallback de acesso.

    Returns
    -------
    dict com chaves:
        adimplente: bool
        status: str
        mensagem: str
        link_pagamento: str | None (URL do boleto/Pix mais recente)
    """
    if not ASAAS_API_KEY:
        # Sem chave configurada = BLOQUEIA acesso
        return {
            "adimplente": False,
            "status": "API_KEY_NAO_CONFIGURADA",
            "mensagem": "Erro de configuração do sistema de pagamento. "
                        "Entre em contato com o administrador.",
            "link_pagamento": None,
        }

    # Busca pagamentos (últimos 50, ordenados por data)
    pagamentos = _asaas_get("payments", {"limit": "50", "order": "desc"})

    if not pagamentos or "data" not in pagamentos:
        # Sem resposta da API = BLOQUEIA acesso
        return {
            "adimplente": False,
            "status": "API_INDISPONIVEL",
            "mensagem": "Não foi possível verificar seu status financeiro no momento. "
                        "Tente novamente em alguns instantes.",
            "link_pagamento": None,
        }

    data = pagamentos.get("data", [])

    # Únicos status que comprovam adimplência
    status_pagos = {"RECEIVED", "CONFIRMED"}

    # Verifica se há pelo menos um pagamento pago
    tem_pago = any(p.get("status") in status_pagos for p in data)

    if tem_pago:
        return {
            "adimplente": True,
            "status": "PAGO",
            "mensagem": "",
            "link_pagamento": None,
        }

    # Nenhum pagamento pago — busca o mais recente para link de regularização
    status_bloqueio = {"OVERDUE", "PENDING", "AWAITING_RISK_ANALYSIS"}

    link = None
    status_atual = "SEM_PAGAMENTOS"

    for p in data:
        if p.get("status") in status_bloqueio:
            status_atual = p["status"]
            link = (
                p.get("invoiceUrl")
                or p.get("bankSlipUrl")
                or p.get("pixCopiaECola")
                or p.get("identificationField")
            )
            break

    return {
        "adimplente": False,
        "status": status_atual,
        "mensagem": _mensagem_status(status_atual),
        "link_pagamento": link,
    }


def _mensagem_status(status: str) -> str:
    mensagens = {
        "OVERDUE": "Sua assinatura está **vencida**. Regularize o pagamento para retomar o acesso à plataforma.",
        "PENDING": "Seu pagamento está **pendente** de confirmação. O acesso será liberado assim que for confirmado.",
        "SEM_PAGAMENTOS": "Nenhum pagamento registrado. Entre em contato para ativar sua assinatura.",
    }
    return mensagens.get(status, f"Status: {status}. Entre em contato para regularizar.")


# ==========================================================================
# CSS E LAYOUT (reutilizável)
# ==========================================================================
def _para_base64(caminho: str) -> str:
    if not os.path.exists(caminho):
        return ""
    with open(caminho, "rb") as f:
        return base64.b64encode(f.read()).decode()


def _injetar_css(modo: str = "login") -> None:
    """Injeta CSS global. modo = 'login' | 'portal' | 'bloqueio'."""
    b64_fundo = _para_base64(_FUNDO_JPG)
    b64_logo = _para_base64(_LOGO_PNG)

    if b64_fundo:
        fundo_css = (
            "background: linear-gradient(rgba(15,23,42,0.88), rgba(15,23,42,0.92)), "
            f"url(data:image/jpeg;base64,{b64_fundo});"
            "background-size: cover; background-position: center; background-attachment: fixed;"
        )
    else:
        fundo_css = "background: linear-gradient(135deg, #0f172a, #1e293b);"

    st.markdown(
        f"""
        <style>
        [data-testid="stSidebar"],
        [data-testid="stSidebarNav"],
        [data-testid="collapsedControl"]        {{ display: none !important; }}
        header[data-testid="stHeader"]         {{ display: none !important; }}

        /* Força conteúdo a ocupar 100% da tela */
        section[data-testid="stSidebar"]        {{ display: none !important; }}
        div[data-testid="stAppViewContainer"]  {{ max-width: 100vw !important; padding: 0 !important; }}
        .stMainBlockContainer                  {{ max-width: 100% !important; padding-top: 1rem !important; }}
        .stApp {{ {fundo_css} }}

        /* Header */
        .portal-header {{
            display: flex; align-items: center; gap: 20px;
            background: rgba(255,255,255,0.95); backdrop-filter: blur(10px);
            border-radius: 16px; padding: 18px 24px; margin-bottom: 28px;
            box-shadow: 0 4px 24px rgba(0,0,0,0.2);
        }}
        .portal-header h1 {{ font-size: 1.6rem; font-weight: 800; color: #1e293b; margin: 0; }}
        .portal-header .sub {{ font-size: 0.85rem; color: #64748b; margin: 2px 0 0; }}

        /* Cards */
        .card {{
            background: rgba(255,255,255,0.95); backdrop-filter: blur(8px);
            border-radius: 16px; padding: 26px 18px; text-align: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15); transition: all 0.3s;
            height: 100%; display: flex; flex-direction: column; justify-content: space-between;
        }}
        .card:hover {{ transform: translateY(-6px); box-shadow: 0 12px 32px rgba(0,0,0,0.3); }}
        .card-icon {{ font-size: 2.8rem; margin-bottom: 10px; display: block; }}
        .card h3 {{ font-size: 1.1rem; font-weight: 700; color: #1e293b; margin: 0 0 8px; }}
        .card p {{ font-size: 0.8rem; color: #64748b; line-height: 1.45; margin: 0 0 16px; flex-grow: 1; }}

        .card-btn {{
            display: inline-block; padding: 10px 20px; border-radius: 10px;
            font-weight: 700; font-size: 0.85rem; text-decoration: none; transition: all 0.2s;
        }}
        .card-btn:hover {{ transform: scale(1.04); }}
        .btn-aso {{ background: linear-gradient(135deg,#3b82f6,#2563eb); color: white; box-shadow: 0 4px 12px rgba(59,130,246,0.4); }}
        .btn-aso:hover {{ box-shadow: 0 6px 18px rgba(59,130,246,0.55); color: white; text-decoration: none; }}
        .btn-docs {{ background: linear-gradient(135deg,#10b981,#059669); color: white; box-shadow: 0 4px 12px rgba(16,185,129,0.4); }}
        .btn-docs:hover {{ box-shadow: 0 6px 18px rgba(16,185,129,0.55); color: white; text-decoration: none; }}
        .btn-apr {{ background: linear-gradient(135deg,#f59e0b,#d97706); color: #1e293b; box-shadow: 0 4px 12px rgba(245,158,11,0.4); }}
        .btn-apr:hover {{ box-shadow: 0 6px 18px rgba(245,158,11,0.55); color: #1e293b; text-decoration: none; }}
        .btn-audit {{ background: linear-gradient(135deg,#8b5cf6,#6d28d9); color: white; box-shadow: 0 4px 12px rgba(139,92,246,0.4); }}
        .btn-audit:hover {{ box-shadow: 0 6px 18px rgba(139,92,246,0.55); color: white; text-decoration: none; }}

        /* Footer fixo */
        .portal-footer {{
            position: fixed; bottom: 0; left: 0; right: 0; text-align: center;
            padding: 12px 20px; background: rgba(15,23,42,0.95); backdrop-filter: blur(6px);
            color: #94a3b8; font-size: 0.75rem; z-index: 100;
            border-top: 1px solid rgba(255,255,255,0.08);
        }}

        /* Expander "Esqueci minha senha" — visível no fundo escuro */
        [data-testid="stExpander"] {{
            background: rgba(255,255,255,0.08) !important;
            border: 1px solid rgba(255,255,255,0.15) !important;
            border-radius: 12px !important;
            max-width: 420px;
            margin: 12px auto 0;
            color: #f1f5f9 !important;
        }}
        [data-testid="stExpander"] summary {{
            color: #f9cc0b !important;
            font-weight: 600 !important;
        }}
        [data-testid="stExpander"] .stMarkdown,
        [data-testid="stExpander"] p,
        [data-testid="stExpander"] li {{
            color: #e2e8f0 !important;
        }}
        [data-testid="stExpander"] input[type="text"] {{
            background: rgba(255,255,255,0.12) !important;
            border: 1px solid rgba(255,255,255,0.2) !important;
            color: #f1f5f9 !important;
        }}
        [data-testid="stExpander"] button {{
            background: #f59e0b !important;
            color: #1e293b !important;
            font-weight: 700 !important;
            border: none !important;
        }}

        /* Login / Bloqueio */
        .login-box {{
            max-width: 420px; margin: 80px auto 0; background: rgba(255,255,255,0.96);
            border-radius: 16px; padding: 36px 32px; box-shadow: 0 8px 32px rgba(0,0,0,0.25);
            text-align: center;
        }}
        .login-box h2 {{ color: #1e293b; margin-bottom: 6px; }}
        .bloqueio-box {{
            max-width: 560px; margin: 60px auto 0; background: rgba(255,255,255,0.96);
            border-radius: 16px; padding: 36px 32px; box-shadow: 0 8px 32px rgba(0,0,0,0.25);
            text-align: center;
        }}
        .plano-bar {{
            text-align: center; padding: 12px 20px; margin-bottom: 28px; border-radius: 12px;
            background: rgba(59,130,246,0.12); border: 1px solid rgba(59,130,246,0.25);
        }}
        .plano-bar .plano-valor {{ color: #60a5fa; font-weight: 700; font-size: 0.95rem; }}

        /* Botão logout */
        .logout-btn {{
            display: inline-block; padding: 8px 18px; border-radius: 8px;
            background: rgba(255,255,255,0.1); color: #94a3b8;
            text-decoration: none; font-size: 0.8rem; font-weight: 600;
            border: 1px solid rgba(255,255,255,0.15); transition: all 0.2s;
        }}
        .logout-btn:hover {{ background: rgba(239,68,68,0.2); color: #fca5a5; border-color: rgba(239,68,68,0.3); }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ==========================================================================
# TELA DE LOGIN
# ==========================================================================
def tela_login() -> None:
    """Exibe o formulário de login."""
    _injetar_css("login")

    b64_logo = _para_base64(_LOGO_PNG)
    logo_tag = (
        f'<img src="data:image/png;base64,{b64_logo}" style="height:60px; margin-bottom:12px;" alt="Logo">'
        if b64_logo
        else '<span style="font-size:3rem;">🛡️</span>'
    )

    st.markdown(
        f"""
        <div class="login-box">
            {logo_tag}
            <h2>Portal Central - SSMA</h2>
            <p style="color:#64748b; font-size:0.85rem; margin-bottom:20px;">Gestão Integrada de Segurança, Saúde e Meio Ambiente</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Campos de login — tudo centralizado
    col_center = st.columns([1, 2, 1])
    with col_center[1]:
        with st.form("form_login", clear_on_submit=False):
            usuario = st.text_input("Usuário", placeholder="Digite seu usuário", label_visibility="collapsed")
            senha = st.text_input("Senha", type="password", placeholder="Digite sua senha", label_visibility="collapsed")

            submitted = st.form_submit_button("🔐 Entrar", use_container_width=True, type="primary")

            if submitted:
                if not usuario.strip():
                    st.error("Informe o usuário.")
                elif _verificar_senha(usuario.strip(), senha):
                    st.session_state["usuario"] = usuario.strip()
                    st.session_state["autenticado"] = True
                    st.session_state["senha_padrao"] = _senha_eh_padrao(usuario.strip())
                    st.rerun()
                else:
                    st.error("Usuário ou senha inválidos.")

        # Esqueci minha senha — dentro da coluna central
        with st.expander("🔑 Esqueci minha senha", expanded=False):
            st.markdown(
                """
                **Procedimento de redefinição:**
                1. Informe seu **usuário** abaixo
                2. A senha será restaurada para a senha padrão temporária
                3. No próximo login, você deverá definir uma nova senha pessoal
                """
            )
            user_reset = st.text_input("Usuário para redefinir", key="reset_user")
            if st.button("🔄 Restaurar Senha Padrão", key="btn_reset", use_container_width=True):
                if user_reset.strip():
                    usuarios = _carregar_usuarios()
                    if user_reset.strip() in usuarios:
                        _restaurar_senha_padrao(user_reset.strip())
                        st.success(
                            f"✅ Senha restaurada para o padrão. "
                            f"Faça login com o usuário **{user_reset.strip()}** "
                            f"e a senha padrão. Você deverá trocá-la no primeiro acesso."
                        )
                    else:
                        st.error("Usuário não encontrado.")
                else:
                    st.warning("Informe o usuário.")


# ==========================================================================
# TELA DE TROCA DE SENHA (obrigatória no 1º login)
# ==========================================================================
def tela_trocar_senha() -> None:
    """Força o usuário a trocar a senha padrão antes de acessar o portal."""
    _injetar_css("login")

    st.markdown(
        """
        <div class="login-box">
            <span style="font-size:3rem;">🔐</span>
            <h2>Troca de Senha Obrigatória</h2>
            <p style="color:#64748b; font-size:0.85rem;">
                Você está usando a senha padrão temporária.<br>
                <strong>Defina uma nova senha pessoal</strong> para continuar.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_center = st.columns([1, 2, 1])
    with col_center[1]:
        with st.form("form_troca_senha"):
            nova = st.text_input("Nova Senha", type="password", key="nova_senha")
            confirmar = st.text_input("Confirmar Nova Senha", type="password", key="conf_senha")
            submitted = st.form_submit_button("💾 Salvar Nova Senha", use_container_width=True, type="primary")

            if submitted:
                if not nova or len(nova) < 6:
                    st.error("A senha deve ter pelo menos 6 caracteres.")
                elif nova != confirmar:
                    st.error("As senhas não conferem.")
                elif nova == DEFAULT_PASS:
                    st.error("A nova senha não pode ser igual à senha padrão.")
                else:
                    usuario = st.session_state.get("usuario", DEFAULT_USER)
                    _alterar_senha(usuario, nova)
                    st.session_state["senha_padrao"] = False
                    st.success("✅ Senha alterada com sucesso! Redirecionando...")
                    st.rerun()


# ==========================================================================
# TELA DE BLOQUEIO (inadimplente)
# ==========================================================================
def tela_bloqueio(resultado: dict) -> None:
    """Exibe mensagem de bloqueio e opções de regularização."""
    _injetar_css("bloqueio")

    link = resultado.get("link_pagamento")
    status = resultado.get("status", "")

    st.markdown(
        f"""
        <div class="bloqueio-box">
            <span style="font-size:4rem;">🚫</span>
            <h2 style="color:#dc2626;">Acesso Suspenso</h2>
            <p style="color:#475569; font-size:0.95rem; margin:12px 0;">
                {resultado.get("mensagem", "Acesso bloqueado por inadimplência.")}
            </p>
            {"<p style='color:#64748b; font-size:0.8rem;'>Status Asaas: <strong>" + status + "</strong></p>" if status else ""}
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_center = st.columns([1, 2, 1])
    with col_center[1]:
        if link:
            st.markdown(
                f"""
                <div style="text-align:center; margin:16px 0;">
                    <a href="{link}" target="_blank" style="
                        display:inline-block; padding:14px 32px; border-radius:10px;
                        background:linear-gradient(135deg,#22c55e,#16a34a); color:white;
                        font-weight:700; text-decoration:none; font-size:1rem;
                        box-shadow: 0 4px 12px rgba(34,197,94,0.4);
                    ">💳 Regularizar Pagamento →</a>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.warning("📧 Entre em contato com o administrador para regularizar sua assinatura.")

        st.caption("Após o pagamento, a liberação pode levar até 3 dias úteis (compensação bancária).")

        if st.button("🔁 Já paguei — Verificar Novamente", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.clear()
            st.rerun()


# ==========================================================================
# TELA PRINCIPAL — PORTAL (4 cards)
# ==========================================================================
def tela_portal() -> None:
    """Portal principal com 4 cards de acesso."""
    _injetar_css("portal")

    b64_logo = _para_base64(_LOGO_PNG)
    logo_tag = (
        f'<img src="data:image/png;base64,{b64_logo}" style="height:55px; width:auto;" alt="Logo">'
        if b64_logo
        else '<span style="font-size:2.5rem;">🛡️</span>'
    )

    # Header com botão de logout + indicador de trial
    usuario = st.session_state.get("usuario", "")
    dias_trial = _dias_desde_cadastro(usuario)
    dias_restantes = max(0, TRIAL_DIAS - dias_trial)
    no_trial = dias_restantes > 0

    trial_badge = ""
    if no_trial:
        trial_badge = (
            f'<span style="display:inline-block; background:rgba(16,185,129,0.15); '
            f'color:#10b981; padding:4px 12px; border-radius:20px; font-size:0.7rem; '
            f'font-weight:600; margin-top:4px;">🟢 Trial: {dias_restantes} dia(s) restante(s)</span>'
        )

    st.markdown(
        f"""
        <div class="portal-header">
            {logo_tag}
            <div style="flex-grow:1;">
                <h1>Portal Central - SSMA</h1>
                <p class="sub">Gestão Integrada de Segurança, Saúde e Meio Ambiente</p>
            </div>
            <div style="text-align:right;">
                <span style="color:#64748b; font-size:0.75rem;">👤 {usuario}</span><br>
                {trial_badge}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Botão de logout funcional no Streamlit
    col_logout = st.columns([9, 1])
    with col_logout[1]:
        if st.button("🚪 Sair", key="btn_logout", use_container_width=True):
            st.session_state.clear()
            st.cache_data.clear()
            st.rerun()

    # Container principal
    st.markdown('<div style="max-width:1250px; margin:0 auto; padding:0 20px 80px;">', unsafe_allow_html=True)

    # 4 Cards ajustados em colunas
    col1, col2, col3, col4 = st.columns(4, gap="medium")

    with col1:
        st.markdown(
            f"""
            <div class="card">
                <div>
                    <span class="card-icon">🏥</span>
                    <h3>Gestão de ASOs</h3>
                    <p>Controle, agendamento e gerenciamento de Atestados de Saúde Ocupacional.</p>
                </div>
                <a href="{URL_ASO}" target="_blank" class="card-btn btn-aso">Acessar Sistema →</a>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class="card">
                <div>
                    <span class="card-icon">📄</span>
                    <h3>Kits Documentais</h3>
                    <p>Emissão automatizada de Ordens de Serviço, Fichas de EPI e Certificados NR06.</p>
                </div>
                <a href="{URL_DOCS}" target="_blank" class="card-btn btn-docs">Acessar Sistema →</a>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div class="card">
                <div>
                    <span class="card-icon">🛠️</span>
                    <h3>Gerador de APR / ATS</h3>
                    <p>Elaboração de Análises Preliminares de Tarefa baseadas no banco unificado.</p>
                </div>
                <a href="{URL_APR}" target="_blank" class="card-btn btn-apr">Acessar Sistema →</a>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            f"""
            <div class="card">
                <div>
                    <span class="card-icon">📊</span>
                    <h3>AuditGuard SST</h3>
                    <p>Auditoria inteligente e gerenciamento avançado de riscos e conformidade em SST.</p>
                </div>
                <a href="{URL_AUDIT}" target="_blank" class="card-btn btn-audit">Acessar Sistema →</a>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('</div>', unsafe_allow_html=True)

    # Footer
    st.markdown(
        """
        <div class="portal-footer">
            © 2026 Gestão Documentos | Desenvolvido por: <strong>Dilceu Junior</strong>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==========================================================================
# FLUXO PRINCIPAL
# ==========================================================================
def main() -> None:
    # Inicializa estado da sessão
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False
    if "senha_padrao" not in st.session_state:
        st.session_state["senha_padrao"] = True
    if "adimplente" not in st.session_state:
        st.session_state["adimplente"] = False

    # ======================================================================
    # PASSO 1 — Não autenticado → mostra login
    # ======================================================================
    if not st.session_state["autenticado"]:
        tela_login()
        st.stop()

    # ======================================================================
    # PASSO 2 — Autenticado mas com senha padrão → força troca
    # ======================================================================
    if st.session_state["senha_padrao"]:
        tela_trocar_senha()
        st.stop()

    # ======================================================================
    # PASSO 3 — Trial de 15 dias
    # ======================================================================
    usuario = st.session_state.get("usuario", "")
    dias_trial = _dias_desde_cadastro(usuario)
    no_trial = _dentro_do_trial(usuario)

    # ======================================================================
    # PASSO 4 — Se fora do trial, verifica Asaas (estrito)
    # ======================================================================
    if no_trial:
        # Dentro do trial: acesso liberado
        st.session_state["adimplente"] = True
        tela_portal()
    else:
        # Fora do trial: validação estrita via Asaas
        resultado = verificar_adimplencia()
        if resultado["adimplente"]:
            st.session_state["adimplente"] = True
            tela_portal()
        else:
            st.session_state["adimplente"] = False
            tela_bloqueio(resultado)


if __name__ == "__main__":
    main()

from __future__ import annotations
import base64
import hashlib
import json
import os
from datetime import datetime
import requests
import streamlit as st

# ==========================================================================
# CONFIGURAÇÃO DA PÁGINA
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

DEFAULT_USER = "macrossma"
DEFAULT_PASS = "macromaq2026"
TRIAL_DIAS = 15

ASAAS_API_KEY = st.secrets.get("ASAAS_API_KEY", os.getenv("ASAAS_API_KEY", ""))
ASAAS_BASE_URL = "https://api.asaas.com/v3"

URL_ASO = "https://aso-gendamento.streamlit.app/"
URL_DOCS = "https://automacaodoc-macromaq.streamlit.app/"
URL_APR = "https://aprmacromaq.streamlit.app/"
URL_AUDIT = "https://riscos.streamlit.app/"

# ==========================================================================
# FUNÇÕES DE USUÁRIO (COM RESET FORÇADO SE O ARQUIVO ESTIVER ANTIGO)
# ==========================================================================
def _hash_senha(senha: str) -> str: 
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()

def _carregar_usuarios() -> dict:
    os.makedirs(_DATA_DIR, exist_ok=True)
    # Se o arquivo não existir ou se quisermos garantir que o usuário padrão está correto:
    default_data = {
        DEFAULT_USER: {
            "senha_hash": _hash_senha(DEFAULT_PASS),
            "senha_padrao": True,
            "criado_em": datetime.now().isoformat(),
        }
    }
    if not os.path.exists(_USERS_FILE):
        _salvar_usuarios(default_data)
        return default_data
    
    try:
        with open(_USERS_FILE, "r", encoding="utf-8") as f: 
            data = json.load(f)
            # Garante que o usuário macrossma existe no json carregado
            if DEFAULT_USER not in data:
                data.update(default_data)
                _salvar_usuarios(data)
            return data
    except:
        _salvar_usuarios(default_data)
        return default_data

def _salvar_usuarios(data: dict) -> None:
    os.makedirs(_DATA_DIR, exist_ok=True)
    with open(_USERS_FILE, "w", encoding="utf-8") as f: 
        json.dump(data, f, ensure_ascii=False, indent=2)

def _verificar_senha(usuario: str, senha: str) -> bool:
    usuarios = _carregar_usuarios()
    user_data = usuarios.get(usuario)
    return user_data["senha_hash"] == _hash_senha(senha) if user_data else False

def _alterar_senha(usuario: str, nova_senha: str) -> None:
    usuarios = _carregar_usuarios()
    if usuario in usuarios:
        usuarios[usuario]["senha_hash"] = _hash_senha(nova_senha)
        usuarios[usuario]["senha_padrao"] = False
        _salvar_usuarios(usuarios)

def _dias_desde_cadastro(usuario: str) -> int:
    usuarios = _carregar_usuarios()
    criado_str = usuarios.get(usuario, {}).get("criado_em", "")
    return (datetime.now() - datetime.fromisoformat(criado_str)).days if criado_str else 999

# ==========================================================================
# INTEGRAÇÃO ASAAS
# ==========================================================================
@st.cache_data(ttl=600)
def verificar_adimplencia() -> dict:
    if not ASAAS_API_KEY: return {"adimplente": False, "status": "ERRO", "mensagem": "API não configurada."}
    try:
        resp = requests.get(f"{ASAAS_BASE_URL}/payments", headers={"access_token": ASAAS_API_KEY}, timeout=15)
        data = resp.json().get("data", [])
        return {"adimplente": any(p.get("status") in ["RECEIVED", "CONFIRMED"] for p in data)}
    except: return {"adimplente": False, "mensagem": "Erro na verificação financeira."}

# ==========================================================================
# CSS ORIGINAL COMPLETO E CORRIGIDO PARA CENTRALIZAÇÃO
# ==========================================================================
def _para_base64(caminho: str) -> str:
    if not os.path.exists(caminho): return ""
    with open(caminho, "rb") as f: return base64.b64encode(f.read()).decode()

def _injetar_css():
    b64_fundo = _para_base64(_FUNDO_JPG)
    if b64_fundo:
        fundo_css = f"background: linear-gradient(rgba(15,23,42,0.88), rgba(15,23,42,0.92)), url(data:image/jpeg;base64,{b64_fundo}); background-size: cover; background-position: center; background-attachment: fixed;"
    else:
        fundo_css = "background: linear-gradient(135deg, #0f172a, #1e293b);"

    st.markdown(f"""
        <style>
        [data-testid="stSidebar"], [data-testid="stSidebarNav"], [data-testid="collapsedControl"] {{ display: none !important; }}
        header[data-testid="stHeader"] {{ display: none !important; }}
        .stApp {{ {fundo_css} }}

        /* Layout do Login centralizado */
        .login-container {{
            display: flex;
            justify-content: center;
            align-items: center;
            height: 80vh;
        }}
        .login-box {{
            width: 100%;
            max-width: 420px;
            background: rgba(255,255,255,0.96);
            border-radius: 16px;
            padding: 36px 32px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.25);
            text-align: center;
        }}
        .login-box h2 {{ color: #1e293b; margin-bottom: 6px; font-weight: 800; }}

        /* Portal Header & Cards */
        .portal-header {{ display: flex; align-items: center; gap: 20px; background: rgba(255,255,255,0.95); backdrop-filter: blur(10px); border-radius: 16px; padding: 18px 24px; margin-bottom: 28px; box-shadow: 0 4px 24px rgba(0,0,0,0.2); }}
        .portal-header h1 {{ font-size: 1.6rem; font-weight: 800; color: #1e293b; margin: 0; }}
        .card {{ background: rgba(255,255,255,0.95); backdrop-filter: blur(8px); border-radius: 16px; padding: 26px 18px; text-align: center; box-shadow: 0 4px 20px rgba(0,0,0,0.15); height: 100%; display: flex; flex-direction: column; justify-content: space-between; }}
        .card-icon {{ font-size: 2.8rem; margin-bottom: 10px; }}
        .card-btn {{ display: inline-block; padding: 10px 20px; border-radius: 10px; font-weight: 700; text-decoration: none; }}
        .btn-aso {{ background: linear-gradient(135deg,#3b82f6,#2563eb); color: white; }}
        .btn-docs {{ background: linear-gradient(135deg,#10b981,#059669); color: white; }}
        .btn-apr {{ background: linear-gradient(135deg,#f59e0b,#d97706); color: #1e293b; }}
        .btn-audit {{ background: linear-gradient(135deg,#8b5cf6,#6d28d9); color: white; }}
        .portal-footer {{ position: fixed; bottom: 0; left: 0; right: 0; text-align: center; padding: 12px; background: rgba(15,23,42,0.95); color: #94a3b8; font-size: 0.75rem; z-index: 100; }}
        </style>
    """, unsafe_allow_html=True)

# ==========================================================================
# TELAS E FLUXO PRINCIPAL
# ==========================================================================
def tela_login():
    _injetar_css()
    
    b64_logo = _para_base64(_LOGO_PNG)
    logo_tag = f'<img src="data:image/png;base64,{b64_logo}" style="height:55px; margin-bottom:12px;" alt="Logo">' if b64_logo else '<span style="font-size:2.5rem;">🛡️</span>'

    st.markdown(f"""
        <div class="login-container">
            <div class="login-box">
                {logo_tag}
                <h2>Portal Central - SSMA</h2>
                <p style="color:#64748b; font-size:0.85rem; margin-bottom:20px;">Gestão Integrada de Segurança, Saúde e Meio Ambiente</p>
    """, unsafe_allow_html=True)

    with st.form("form_login"):
        user = st.text_input("Usuário", placeholder="Digite seu usuário")
        pw = st.text_input("Senha", type="password", placeholder="Digite sua senha")
        submitted = st.form_submit_button("🔐 Entrar", use_container_width=True, type="primary")

        if submitted:
            if _verificar_senha(user.strip(), pw):
                st.session_state.autenticado = True
                st.session_state.usuario = user.strip()
                st.session_state.senha_padrao = _carregar_usuarios()[user.strip()].get("senha_padrao", True)
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos.")

    st.markdown('</div></div>', unsafe_allow_html=True)

def tela_trocar_senha():
    _injetar_css()
    st.markdown("""
        <div class="login-container">
            <div class="login-box">
                <span style="font-size:3rem;">🔐</span>
                <h2>Troca de Senha Obrigatória</h2>
                <p style="color:#64748b; font-size:0.85rem; margin-bottom:20px;">Defina uma nova senha pessoal para continuar.</p>
    """, unsafe_allow_html=True)

    with st.form("form_troca"):
        nova = st.text_input("Nova Senha", type="password")
        confirmar = st.text_input("Confirmar Nova Senha", type="password")
        submitted = st.form_submit_button("💾 Salvar Nova Senha", use_container_width=True, type="primary")

        if submitted:
            if not nova or len(nova) < 6:
                st.error("A senha deve ter pelo menos 6 caracteres.")
            elif nova != confirmar:
                st.error("As senhas não conferem.")
            else:
                _alterar_senha(st.session_state.usuario, nova)
                st.session_state.senha_padrao = False
                st.success("✅ Senha alterada com sucesso!")
                st.rerun()

    st.markdown('</div></div>', unsafe_allow_html=True)

def tela_portal():
    _injetar_css()
    b64_logo = _para_base64(_LOGO_PNG)
    logo_tag = f'<img src="data:image/png;base64,{b64_logo}" style="height:45px; width:auto;" alt="Logo">' if b64_logo else '<span style="font-size:2rem;">🛡️</span>'
    usuario = st.session_state.get("usuario", "")

    st.markdown(f"""
        <div class="portal-header">
            {logo_tag}
            <div style="flex-grow:1;">
                <h1>Portal Central - SSMA</h1>
                <p style="color:#64748b; font-size:0.8rem; margin:2px 0 0;">Gestão Integrada de Segurança, Saúde e Meio Ambiente</p>
            </div>
            <div style="text-align:right;">
                <span style="color:#64748b; font-size:0.75rem;">👤 {usuario}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    col_logout = st.columns([10, 1])
    with col_logout[1]:
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    cols = st.columns(4, gap="medium")
    cols[0].markdown(f'<div class="card"><div class="card-icon">🏥</div><h3>Gestão de ASOs</h3><p style="font-size:0.8rem; color:#64748b;">Controle e agendamento de ASOs.</p><br><a href="{URL_ASO}" target="_blank" class="card-btn btn-aso">Acessar →</a></div>', unsafe_allow_html=True)
    cols[1].markdown(f'<div class="card"><div class="card-icon">📄</div><h3>Kits Documentais</h3><p style="font-size:0.8rem; color:#64748b;">Emissão de OS, Fichas de EPI e NR06.</p><br><a href="{URL_DOCS}" target="_blank" class="card-btn btn-docs">Acessar →</a></div>', unsafe_allow_html=True)
    cols[2].markdown(f'<div class="card"><div class="card-icon">🛠️</div><h3>Gerador de APR</h3><p style="font-size:0.8rem; color:#64748b;">Análises Preliminares de Tarefa.</p><br><a href="{URL_APR}" target="_blank" class="card-btn btn-apr">Acessar →</a></div>', unsafe_allow_html=True)
    cols[3].markdown(f'<div class="card"><div class="card-icon">📊</div><h3>AuditGuard SST</h3><p style="font-size:0.8rem; color:#64748b;">Auditoria inteligente e riscos.</p><br><a href="{URL_AUDIT}" target="_blank" class="card-btn btn-audit">Acessar →</a></div>', unsafe_allow_html=True)

    st.markdown('<div class="portal-footer">© 2026 Gestão Documentos | Desenvolvido por: <strong>Dilceu Junior</strong></div>', unsafe_allow_html=True)

def main():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False
        st.session_state.senha_padrao = True

    if not st.session_state.autenticado:
        tela_login()
    elif st.session_state.senha_padrao:
        tela_trocar_senha()
    else:
        if _dias_desde_cadastro(st.session_state.usuario) < TRIAL_DIAS or verificar_adimplencia().get("adimplente"):
            tela_portal()
        else:
            _injetar_css()
            st.error("Acesso bloqueado por inadimplência.")

if __name__ == "__main__":
    main()

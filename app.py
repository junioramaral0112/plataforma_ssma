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
# FUNÇÕES DE USUÁRIO
# ==========================================================================
def _carregar_usuarios() -> dict:
    os.makedirs(_DATA_DIR, exist_ok=True)
    if not os.path.exists(_USERS_FILE):
        default_data = {DEFAULT_USER: {"senha_hash": _hash_senha(DEFAULT_PASS), "senha_padrao": True, "criado_em": datetime.now().isoformat()}}
        _salvar_usuarios(default_data)
        return default_data
    with open(_USERS_FILE, "r", encoding="utf-8") as f: return json.load(f)

def _salvar_usuarios(data: dict) -> None:
    os.makedirs(_DATA_DIR, exist_ok=True)
    with open(_USERS_FILE, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=2)

def _hash_senha(senha: str) -> str: return hashlib.sha256(senha.encode("utf-8")).hexdigest()

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
# CSS ORIGINAL COMPLETO
# ==========================================================================
def _para_base64(caminho: str) -> str:
    if not os.path.exists(caminho): return ""
    with open(caminho, "rb") as f: return base64.b64encode(f.read()).decode()

def _injetar_css():
    b64_fundo = _para_base64(_FUNDO_JPG)
    fundo_css = f"background: linear-gradient(rgba(15,23,42,0.88), rgba(15,23,42,0.92)), url(data:image/jpeg;base64,{b64_fundo}); background-size: cover; background-position: center; background-attachment: fixed;"
    
    st.markdown(f"""
        <style>
        [data-testid="stSidebar"], [data-testid="stSidebarNav"] {{ display: none !important; }}
        .stApp {{ {fundo_css} }}
        .portal-header {{ display: flex; align-items: center; gap: 20px; background: rgba(255,255,255,0.95); backdrop-filter: blur(10px); border-radius: 16px; padding: 18px 24px; margin-bottom: 28px; box-shadow: 0 4px 24px rgba(0,0,0,0.2); }}
        .portal-header h1 {{ font-size: 1.6rem; font-weight: 800; color: #1e293b; margin: 0; }}
        .card {{ background: rgba(255,255,255,0.95); backdrop-filter: blur(8px); border-radius: 16px; padding: 26px 18px; text-align: center; box-shadow: 0 4px 20px rgba(0,0,0,0.15); height: 100%; display: flex; flex-direction: column; }}
        .card-icon {{ font-size: 2.8rem; margin-bottom: 10px; }}
        .card-btn {{ display: inline-block; padding: 10px 20px; border-radius: 10px; font-weight: 700; text-decoration: none; }}
        .btn-aso {{ background: linear-gradient(135deg,#3b82f6,#2563eb); color: white; }}
        .btn-docs {{ background: linear-gradient(135deg,#10b981,#059669); color: white; }}
        .btn-apr {{ background: linear-gradient(135deg,#f59e0b,#d97706); color: #1e293b; }}
        .btn-audit {{ background: linear-gradient(135deg,#8b5cf6,#6d28d9); color: white; }}
        .portal-footer {{ position: fixed; bottom: 0; left: 0; right: 0; text-align: center; padding: 12px; background: rgba(15,23,42,0.95); color: #94a3b8; font-size: 0.75rem; z-index: 100; }}
        .login-box {{ max-width: 420px; margin: 80px auto; background: rgba(255,255,255,0.96); border-radius: 16px; padding: 36px; text-align: center; box-shadow: 0 8px 32px rgba(0,0,0,0.25); }}
        </style>
    """, unsafe_allow_html=True)

# ==========================================================================
# TELAS E FLUXO PRINCIPAL
# ==========================================================================
def tela_login():
    _injetar_css()
    st.markdown('<div class="login-box"><h2>Portal Central - SSMA</h2>', unsafe_allow_html=True)
    with st.form("login"):
        user = st.text_input("Usuário")
        pw = st.text_input("Senha", type="password")
        if st.form_submit_button("🔐 Entrar"):
            if _verificar_senha(user, pw):
                st.session_state.autenticado = True
                st.session_state.usuario = user
                st.session_state.senha_padrao = _carregar_usuarios()[user].get("senha_padrao", True)
                st.rerun()
            else: st.error("Credenciais inválidas")

def tela_portal():
    _injetar_css()
    # Header e Cards como você tinha
    st.markdown('<div class="portal-header"><h1>Portal Central - SSMA</h1></div>', unsafe_allow_html=True)
    cols = st.columns(4)
    cols[0].markdown(f'<div class="card"><div class="card-icon">🏥</div><h3>ASOs</h3><a href="{URL_ASO}" class="card-btn btn-aso">Acessar</a></div>', unsafe_allow_html=True)
    cols[1].markdown(f'<div class="card"><div class="card-icon">📄</div><h3>Documentos</h3><a href="{URL_DOCS}" class="card-btn btn-docs">Acessar</a></div>', unsafe_allow_html=True)
    cols[2].markdown(f'<div class="card"><div class="card-icon">🛠️</div><h3>Gerador APR</h3><a href="{URL_APR}" class="card-btn btn-apr">Acessar</a></div>', unsafe_allow_html=True)
    cols[3].markdown(f'<div class="card"><div class="card-icon">📊</div><h3>AuditGuard</h3><a href="{URL_AUDIT}" class="card-btn btn-audit">Acessar</a></div>', unsafe_allow_html=True)
    
    if st.button("🚪 Sair"):
        st.session_state.clear()
        st.rerun()

def main():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False
        st.session_state.senha_padrao = True

    if not st.session_state.autenticado: tela_login()
    elif st.session_state.senha_padrao:
        _injetar_css()
        st.markdown('<div class="login-box"><h2>Trocar Senha</h2>', unsafe_allow_html=True)
        nova = st.text_input("Nova Senha", type="password")
        if st.button("Salvar"):
            _alterar_senha(st.session_state.usuario, nova)
            st.session_state.senha_padrao = False
            st.rerun()
    else:
        if _dias_desde_cadastro(st.session_state.usuario) < TRIAL_DIAS or verificar_adimplencia().get("adimplente"):
            tela_portal()
        else: st.error("Acesso bloqueado por inadimplência.")

if __name__ == "__main__":
    main()

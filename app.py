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
# FUNÇÕES DE USUÁRIO (PERSISTÊNCIA)
# ==========================================================================
def _carregar_usuarios() -> dict:
    os.makedirs(_DATA_DIR, exist_ok=True)
    if not os.path.exists(_USERS_FILE):
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
    os.makedirs(_DATA_DIR, exist_ok=True)
    with open(_USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def _hash_senha(senha: str) -> str:
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()

def _verificar_senha(usuario: str, senha: str) -> bool:
    usuarios = _carregar_usuarios()
    user_data = usuarios.get(usuario)
    return user_data["senha_hash"] == _hash_senha(senha) if user_data else False

def _alterar_senha(usuario: str, nova_senha: str) -> None:
    usuarios = _carregar_usuarios()
    if usuario in usuarios:
        usuarios[usuario]["senha_hash"] = _hash_senha(nova_senha)
        usuarios[usuario]["senha_padrao"] = False # Persiste no JSON
        _salvar_usuarios(usuarios)

def _restaurar_senha_padrao(usuario: str) -> None:
    usuarios = _carregar_usuarios()
    if usuario in usuarios:
        usuarios[usuario]["senha_hash"] = _hash_senha(DEFAULT_PASS)
        usuarios[usuario]["senha_padrao"] = True
        _salvar_usuarios(usuarios)

def _dias_desde_cadastro(usuario: str) -> int:
    usuarios = _carregar_usuarios()
    criado_str = usuarios.get(usuario, {}).get("criado_em", "")
    if not criado_str: return 999
    return (datetime.now() - datetime.fromisoformat(criado_str)).days

# ==========================================================================
# INTEGRAÇÃO ASAAS
# ==========================================================================
@st.cache_data(ttl=600)
def verificar_adimplencia() -> dict:
    if not ASAAS_API_KEY: return {"adimplente": False, "status": "ERRO", "mensagem": "API não configurada."}
    try:
        resp = requests.get(f"{ASAAS_BASE_URL}/payments", headers={"access_token": ASAAS_API_KEY}, timeout=15)
        data = resp.json().get("data", [])
        if any(p.get("status") in ["RECEIVED", "CONFIRMED"] for p in data):
            return {"adimplente": True}
        return {"adimplente": False, "mensagem": "Assinatura pendente ou vencida."}
    except:
        return {"adimplente": False, "mensagem": "Erro na verificação financeira."}

# ==========================================================================
# INJEÇÃO CSS
# ==========================================================================
def _injetar_css():
    st.markdown("""
        <style>
        [data-testid="stSidebar"] { display: none !important; }
        .stApp { background: linear-gradient(135deg, #0f172a, #1e293b); }
        .login-box { max-width: 420px; margin: 80px auto; background: white; padding: 36px; border-radius: 16px; text-align: center; }
        .card { background: white; border-radius: 16px; padding: 20px; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
        </style>
    """, unsafe_allow_html=True)

# ==========================================================================
# TELAS
# ==========================================================================
def tela_login():
    _injetar_css()
    st.markdown('<div class="login-box"><h2>Portal SSMA Macromaq</h2>', unsafe_allow_html=True)
    with st.form("login"):
        user = st.text_input("Usuário")
        pw = st.text_input("Senha", type="password")
        if st.form_submit_button("Entrar"):
            if _verificar_senha(user, pw):
                st.session_state.autenticado = True
                st.session_state.usuario = user
                # Busca do banco se a senha é padrão
                st.session_state.senha_padrao = _carregar_usuarios()[user].get("senha_padrao", True)
                st.rerun()
            else:
                st.error("Credenciais inválidas")

def tela_trocar_senha():
    _injetar_css()
    st.markdown('<div class="login-box"><h2>Trocar Senha</h2>', unsafe_allow_html=True)
    nova = st.text_input("Nova Senha", type="password")
    if st.button("Salvar"):
        if len(nova) < 6: st.error("Mínimo 6 caracteres")
        else:
            _alterar_senha(st.session_state.usuario, nova)
            st.session_state.senha_padrao = False
            st.rerun()

def tela_portal():
    _injetar_css()
    st.title("Bem-vindo ao Portal SSMA")
    cols = st.columns(4)
    cols[0].markdown(f"[🏥 Gestão de ASOs]({URL_ASO})")
    cols[1].markdown(f"[📄 Kits Documentais]({URL_DOCS})")
    cols[2].markdown(f"[🛠️ Gerador APR]({URL_APR})")
    cols[3].markdown(f"[📊 AuditGuard]({URL_AUDIT})")
    if st.button("Sair"):
        st.session_state.clear()
        st.rerun()

# ==========================================================================
# MAIN
# ==========================================================================
def main():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False
        st.session_state.senha_padrao = True

    if not st.session_state.autenticado:
        tela_login()
    elif st.session_state.senha_padrao:
        tela_trocar_senha()
    else:
        # Verifica Trial ou Adimplência
        if _dias_desde_cadastro(st.session_state.usuario) < TRIAL_DIAS or verificar_adimplencia().get("adimplente"):
            tela_portal()
        else:
            st.error("Acesso bloqueado por inadimplência.")

if __name__ == "__main__":
    main()

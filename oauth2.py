from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import os
import pickle
import requests  # essa é nova, para chamar a API userinfo

# Caminho para salvar o token de acesso (evita re-autenticação a cada execução)
TOKEN_PATH = "token_google.pkl"
CLIENT_SECRET_FILE = "client_secret.json"

SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://mail.google.com/'  # <-- escopo completo para IMAP/SMTP
]


def get_credentials() -> Credentials:
    creds = None

    # Tenta carregar credenciais salvas, se existirem
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'rb') as token_file:
            creds = pickle.load(token_file)

    # Se não há credenciais válidas, inicia o fluxo OAuth
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Erro ao atualizar token: {e}")
                creds = None  # Força novo login em caso de erro
        if not creds:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRET_FILE, SCOPES
            )
            creds = flow.run_local_server(port=8080, prompt='consent', open_browser=True)

        # Salva credenciais para futuros usos
        with open(TOKEN_PATH, 'wb') as token_file:
            pickle.dump(creds, token_file)

    return creds


def get_user_email(credentials: Credentials) -> str:
    """
    Obtém o email do usuário autenticado via OAuth2.
    Essa função é usada pelo MailAnalyzer.
    """
    try:
        response = requests.get(
            "https://www.googleapis.com/oauth2/v1/userinfo",
            headers={"Authorization": f"Bearer {credentials.token}"}
        )
        if response.status_code == 200:
            user_info = response.json()
            return user_info.get("email", "")
        else:
            print(f"Erro ao buscar userinfo: {response.text}")
            return ""
    except Exception as e:
        print(f"Erro inesperado ao buscar userinfo: {e}")
        return ""

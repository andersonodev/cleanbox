import streamlit as st
import math
import time
from mail_client import MailAnalyzer
from oauth2 import get_credentials

# Configuração da página
st.set_page_config(
    page_title="CleanBox",
    layout="centered",
    page_icon="./cleanbox.png",  # Ou "cleanbox.ico"
    )


# Importar CSS externo (style.css)
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Layout principal
st.markdown('<div class="main-container">', unsafe_allow_html=True)
st.markdown('<div class="main-title">CleanBox</div>', unsafe_allow_html=True)

# Instruções
st.markdown("""
<div class="instruction-box">
    📖 <strong>Como funciona:</strong>
    <ol>
        <li>Clique em "Conectar ao Gmail".</li>
        <li>Faça login via Google (OAuth2, seguro).</li>
        <li>Analise e limpe sua caixa de entrada com facilidade.</li>
    </ol>
    ✅ Funciona com contas com 2FA ativado — sem necessidade de App Password!
</div>
""", unsafe_allow_html=True)

# Conexão inicial
if "analyzer" not in st.session_state:
    if st.button("🔗 Conectar ao Gmail", key="connect_button", help="Conectar-se via OAuth2"):
        creds = get_credentials()
        analyzer = MailAnalyzer(creds)
        analyzer.fetch_bin_folder()
        st.session_state.analyzer = analyzer
        st.session_state.email_address = analyzer.email_address
        st.session_state.email_data = None
        st.session_state.stop_analysis = False
        st.success(f"✅ Conectado como {analyzer.email_address}")
        st.rerun()
else:
    analyzer = st.session_state.analyzer
    email_address = st.session_state.email_address

    st.markdown(f"<div class='status-box'>📧 Conectado como: {email_address}</div>", unsafe_allow_html=True)

    # Botões lado a lado (analisar/parar/trocar conta)
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📊 Analisar E-mails", key="analyze_button", help="Analisar todos os remetentes"):
            st.session_state.stop_analysis = False
            st.session_state.email_data = None
            st.rerun()

    with col2:
        if st.button("⏹️ Parar Análise", key="stop_button", help="Parar processo em andamento"):
            st.session_state.stop_analysis = True

    with col3:
        if st.button("🔄 Trocar Conta", key="switch_button", help="Desconectar e conectar nova conta"):
            st.session_state.clear()
            st.rerun()

    # Barra de progresso customizada
    progress_placeholder = st.empty()

    def render_progress_bar(current, total):
        percent = (current / total) * 100
        progress_html = f"""
        <div class="progress-bar-container">
            <div class="progress-bar-fill" style="width: {percent}%;"></div>
            <div class="progress-bar-text">📊 Processando e-mail {current} de {total}</div>
        </div>
        """
        progress_placeholder.markdown(progress_html, unsafe_allow_html=True)

    # Processamento de e-mails
    if st.session_state.email_data is None and not st.session_state.stop_analysis:
        def update_progress(current, total):
            render_progress_bar(current, total)

        st.session_state.email_data = analyzer.get_sender_statistics(progress_callback=update_progress)
        progress_placeholder.empty()
        st.success("✅ Análise concluída!")
        st.rerun()

    # Exibe tabela de remetentes detectados
    if st.session_state.email_data is not None:
        df = st.session_state.email_data
        st.write("### ✉️ Remetentes Detectados")
        df["Limpar?"] = False

        edited_df = st.data_editor(
            df,
            column_config={
                "Unsubscribe Link": st.column_config.LinkColumn(),
                "Limpar?": st.column_config.CheckboxColumn("Marcar para Limpar")
            },
            use_container_width=True
        )

        col1, col2 = st.columns(2)

        # Botão para mover para lixeira
        with col1:
            if st.button("🧹 Mover para Lixeira", key="clean_button", type="primary"):
                senders_to_clean = edited_df[edited_df["Limpar?"]]["Email"]
                for sender in senders_to_clean:
                    count = analyzer.delete_emails_from_sender(sender)
                    st.success(f"{count} e-mails de {sender} movidos para a lixeira!")
                st.session_state.email_data = None
                st.rerun()

        # Botão para deletar permanentemente
        with col2:
            if st.button("🚨 Deletar Permanentemente", key="delete_permanent_button", type="secondary"):
                senders_to_delete = edited_df[edited_df["Limpar?"]]["Email"]
                for sender in senders_to_delete:
                    count = analyzer.delete_emails_from_sender_permanently(sender)
                    st.success(f"{count} e-mails de {sender} foram **permanentemente deletados**!")
                st.session_state.email_data = None
                st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

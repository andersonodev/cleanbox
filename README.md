# CleanMail

CleanMail é uma ferramenta para limpar rapidamente sua caixa de entrada de e-mails!

## Funcionalidades

- Autenticação via OAuth2 com contas do Gmail
- Análise de remetentes de e-mails
- Identificação de links de cancelamento de inscrição
- Exclusão em massa de e-mails de remetentes selecionados

## Demonstração

<https://github.com/user-attachments/assets/b52220a0-b69e-4dcb-8eb2-f1bbe472d536>

## Como executar

### Pré-requisitos

- Python 3.12 ou superior
- `uv` para gerenciamento de dependências

### Passos para executar

1. Instale `uv` (se você ainda não tiver)

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

   Siga as instruções após a conclusão da instalação.

2. Instale as dependências com `uv`

   ```bash
   uv sync
   ```

3. Execute o aplicativo Streamlit:

   ```bash
   uv run streamlit run main.py
   ```

### Executando com Docker

Se você preferir hospedar o aplicativo você mesmo, há um Dockerfile disponível.

1. Construa a imagem Docker:

   ```bash
   docker build -t cleanmail .
   ```

2. Execute o contêiner Docker:

   ```bash
   docker run -p 8501:8501 cleanmail
   ```

### Autenticação

1. Clique em "Connect to Gmail" na barra lateral.
2. Faça login via Google (o fluxo OAuth2 abrirá no navegador).
3. Analise e limpe sua caixa de entrada com segurança!

### Observações

- Não é necessário usar App Password — funciona com contas que possuem 2FA habilitado.
- Certifique-se de ter um arquivo `client_secret.json` válido na raiz do projeto para a autenticação OAuth2.

## Estrutura do Projeto

- `main.py`: Arquivo principal que executa o aplicativo Streamlit.
- `oauth2.py`: Gerencia a autenticação OAuth2.
- `mail_client.py`: Contém a lógica para análise e limpeza de e-mails.
- `requirements.txt`: Lista de dependências do projeto.
- `Dockerfile`: Configuração para criar uma imagem Docker do projeto.
- `client_secret.json`: Arquivo de configuração para OAuth2 (não compartilhe este arquivo publicamente).

## Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.

## Licença

Este projeto está licenciado sob a licença MIT.

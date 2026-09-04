# 🤖 WhatsApp Chatbot com IA (Groq) & Docker

Chatbot inteligente para WhatsApp totalmente conteinerizado utilizando **WAHA (WhatsApp HTTP API)** e a API de altíssima velocidade da **Groq** (`openai/gpt-oss-120b`).

---

## 🌟 Funcionalidades

- ⚡ **Respostas Ultrarrápidas com Groq AI**: Alimentado pelo modelo `openai/gpt-oss-120b` com capacidade de raciocínio e alta fidelidade em português.
- 💬 **Memória de Contexto**: Mantém o histórico das últimas mensagens trocadas com cada contato para conversas fluidas e naturais.
- 📱 **Integração WhatsApp via WAHA**: Conexão simples via QR Code sem necessidade de APIs pagas de terceiros.
- 🎯 **Sessões Dinâmicas**: Reconhece e responde automaticamente pela sessão conectada no painel.
- 🛡️ **Filtros Anti-Loop e Proteção**:
  - Ignora mensagens enviadas pelo próprio bot (`fromMe: true`).
  - Deduplicação automática de mensagens repetidas.
  - Filtro para ignorar grupos (`@g.us`) e transmissões de status (`status@broadcast`).
- ✍️ **Experiência Humanizada**:
  - Marca as mensagens recebidas como lidas (`seen`).
  - Ativa o indicador de "digitando..." (`typing`) enquanto a IA processa a resposta.
- 🐳 **100% Conteinerizado**: Tudo pronto para rodar com apenas um comando via Docker Compose.

---

## 📁 Estrutura do Projeto

```text
.
├── app/
│   ├── __init__.py
│   ├── config.py         # Configurações e variáveis de ambiente (Pydantic Settings)
│   ├── groq_client.py    # Cliente assíncrono para a API da Groq
│   ├── memory.py         # Gerenciamento de memória e histórico por contato
│   ├── waha_client.py    # Cliente HTTP para envio de mensagens e status no WhatsApp
│   └── main.py           # Aplicação FastAPI e processador do Webhook
├── Dockerfile            # Imagem Docker do serviço do Chatbot
├── docker-compose.yml    # Orquestração dos containers (WAHA + Chatbot)
├── requirements.txt      # Dependências Python (FastAPI, Groq, HTTPX, etc.)
├── test_system.py        # Suíte de testes automatizados de integração
├── .env                  # Variáveis de ambiente e chave de API
├── .env.example          # Modelo de configuração de ambiente
└── README.md             # Documentação do projeto
```

---

## 🚀 Como Iniciar o Projeto

### 1. Pré-requisitos
- [Docker](https://docs.docker.com/get-docker/) e [Docker Compose](https://docs.docker.com/compose/) instalados.

### 2. Configurar o arquivo `.env`
O arquivo `.env` já vem pré-configurado com a sua chave da Groq. Caso queira alterar a personalidade do robô ou parâmetros, edite o arquivo:

```env
# Chave e Modelo Groq
GROQ_API_KEY=sua_chave_groq_aqui
GROQ_MODEL=openai/gpt-oss-120b
GROQ_TEMPERATURE=0.7
GROQ_MAX_TOKENS=1024

# Prompt do Sistema (Personalidade do Assistente)
SYSTEM_PROMPT="Você é um assistente virtual prestativo, educado e ágil no WhatsApp. Responda sempre em português do Brasil de forma clara e natural. Seja direto e amigável."

# Configurações do Bot
IGNORE_GROUPS=true
MAX_HISTORY_MESSAGES=12
```

### 3. Subir os Containers Docker
Execute no terminal:

```bash
docker compose up -d --build
```

---

## 📱 Como Conectar o seu WhatsApp

1. Abra o navegador em: **[http://localhost:3000/dashboard](http://localhost:3000/dashboard)**
2. Crie ou localize uma sessão (ex: `chatbot` ou `default`).
3. Clique em **Start** (Iniciar sessão) e depois no botão do **QR Code**.
4. No seu celular:
   - Abra o **WhatsApp**
   - Acesse **Aparelhos Conectados** > **Conectar um aparelho**
   - Escaneie o QR Code exibido na tela.
5. Assim que o status mudar para **`WORKING`**, o bot estará ativo e respondendo automaticamente!

---

## 🧪 Como Executar os Testes Automatizados

O projeto inclui uma bateria de testes que valida:
- Status de saúde da API (`/health`).
- Rota raiz com modelo ativo (`/`).
- Conexão e comunicação direta com a API do WAHA.
- Acesso ao Dashboard.
- Simulação de mensagens recebidas via webhook e resposta da IA.
- Deduplicação de mensagens e filtros de proteção (mensagens próprias e grupos).

Para rodar os testes:
```bash
python3 test_system.py
```

---

## 🛠️ Comandos Úteis do Docker

### Acompanhar logs em tempo real:
```bash
# Logs do Chatbot (mensagens recebidas e respostas da IA)
docker compose logs -f chatbot

# Logs do WhatsApp (WAHA)
docker compose logs -f waha

# Logs de todos os serviços combinados
docker compose logs -f
```

### Reiniciar ou Parar os serviços:
```bash
# Reiniciar apenas o chatbot (útil após alterar o SYSTEM_PROMPT no .env)
docker compose restart chatbot

# Parar todos os containers
docker compose down

# Iniciar novamente
docker compose up -d
```

---

## 🏗️ Arquitetura do Fluxo de Mensagens

```
[Contato no WhatsApp]
        │
        ▼ (Envia mensagem)
[WAHA Container (:3000)]
        │
        ▼ (Dispara Webhook POST /webhook)
[FastAPI Chatbot (:8000)]
        │
        ├─► Responde 200 OK imediatamente ao webhook
        ├─► Dispara indicador "digitando..." no WhatsApp
        ├─► Recupera contexto recente da conversa na Memória
        │
        ▼ (Consulta IA)
[Groq API (openai/gpt-oss-120b)]
        │
        ▼ (Retorna resposta gerada)
[FastAPI Chatbot (:8000)]
        │
        ├─► Salva pergunta e resposta no histórico
        ├─► Remove indicador "digitando..."
        │
        ▼ (POST /api/sendText)
[WAHA Container (:3000)]
        │
        ▼ (Envia resposta via WhatsApp Web)
[Contato no WhatsApp recebe a resposta]
```

# RAG PHP MCP Server

> 🚀 Gera embeddings para alimentar RAG via Model Context Protocol (MCP) do seu projeto PHP pessoal, sem uso de API de terceiros.

## 📋 Visão Geral

Este projeto implementa um servidor MCP que analisa código PHP recursivamente e gera embeddings para criar um sistema de Retrieval-Augmented Generation (RAG) local e privado. Perfeito para integração com ferramentas de IA que suportam MCP.

## 🎯 Recursos

- ✅ Análise recursiva de código PHP
- ✅ Geração de embeddings locais (sem dependência de APIs de terceiros)
- ✅ Integração com Model Context Protocol (MCP)
- ✅ Suporte para consultas em linguagem natural
- ✅ Completamente privado e offline

## 📦 Pré-requisitos

Certifique-se de ter instalado em seu sistema:

- **Python** 3.11 ou superior
- **pip** (gerenciador de pacotes Python)
- **Linux/macOS** (ou WSL no Windows)

## 🔧 Instalação

### 1️⃣ Instale o módulo VENV (gerenciador de ambientes virtuais)

Para distribuições Debian/Ubuntu:

```bash
sudo apt install python3.13-venv
```

Ou para outras distribuições, ajuste o comando conforme necessário.

### 2️⃣ Crie e ative o ambiente virtual

```bash
python3 -m venv .venv && source .venv/bin/activate
```

**No Windows (WSL/GitBash):**
```bash
python3 -m venv .venv
.\.venv\Scripts\activate
```

### 3️⃣ Instale as dependências

```bash
pip install -r requirements.txt
```

## 📁 Estrutura do Projeto

```
rag_php_mcp/
├── mcp_server.py          # Servidor MCP principal
├── ask_llm.py             # Interface para consultas
├── ingest.py              # Ingesta de arquivos únicos
├── ingest_recursive.py    # Ingesta recursiva de diretórios
├── teste.php              # Arquivo PHP de teste
├── requirements.txt       # Dependências do projeto
└── README.md              # Este arquivo
```

## 🚀 Uso

### Ingerir Código PHP (recursivamente)

Para processar todos os arquivos PHP de um diretório:

```bash
python ingest_recursive.py /caminho/do/seu/projeto/php
```

### Ingerir Um Arquivo Específico

```bash
python ingest.py /caminho/do/arquivo.php
```

### Fazer Consultas

Para consultar os embeddings gerados:

```bash
python ask_llm.py "Sua pergunta sobre o código aqui"
```

### Executar o Servidor MCP

```bash
python mcp_server.py
```

## � Integração com IDEs

Este servidor MCP pode ser integrado com diversas IDEs e ferramentas disponíveis no mercado que suportam o protocolo Model Context Protocol:

### IDEs Compatíveis

| IDE | Suporte MCP | Descrição |
|-----|-------------|-----------|
| **VS Code** | ✅ Sim | Com extensões MCP (Copilot, Clines, etc.) |
| **Cursor** | ✅ Sim | Suporte nativo a MCP |
| **JetBrains IDEs** | ✅ Sim | PhpStorm, IntelliJ IDEA com plugins MCP |
| **Cline** | ✅ Sim | IDE specializada em MCP |
| **Continue.dev** | ✅ Sim | Plataforma de IA para desenvolvedores |
| **Claude Desktop** | ✅ Sim | Versão desktop com suporte a MCP |
| **Windsurf** | ✅ Sim | IDE moderna com integração MCP |

### Configuração em Diferentes IDEs

#### VS Code
Instale uma extensão MCP compatível e configure o endpoint do servidor em suas configurações.

#### Cursor
O Cursor possui suporte nativo para MCP - apenas configure o servidor e comece a usar.

#### JetBrains IDEs (PhpStorm, WebStorm)
Configure o plugin MCP nas preferências e aponte para o servidor local.

## �🛠️ Configuração

As configurações do projeto podem ser ajustadas editando os arquivos Python conforme necessário.

## 📝 Licença

Este projeto é licenciado sob a MIT License. Veja o arquivo LICENSE para mais detalhes.

## 💡 Notas

- Todos os embeddings são gerados **localmente** em sua máquina
- Seus dados de código **nunca** são enviados para servidores externos
- O projeto é totalmente **open-source** e personalizável

---

**Desenvolvido com ❤️ para análise local de código PHP**



"""Constantes visuais e de configuração do SGA.

Centraliza toda a paleta de cores, tipografia e parâmetros do tema dark
corporativo. Alterar aqui propaga para toda a aplicação.
"""

# ----------------------------------------------------------------------
# Identidade da aplicação
# ----------------------------------------------------------------------
APP_NOME = "SGA"
APP_SUBTITULO = "Sistema de Gestão de Atendimento"
APP_VERSAO = "2.0.0"
APP_EMPRESA = "QueueFlow Solutions"

# ----------------------------------------------------------------------
# Paleta de cores (dark corporativo)
# ----------------------------------------------------------------------
# Fundos
COR_FUNDO = "#0f1419"
COR_FUNDO_CLARO = "#1a1f2e"
COR_CARD = "#1e2433"
COR_CARD_HOVER = "#252b3d"
COR_BORDA = "#2a3142"

# Marca / ações
COR_PRIMARIA = "#3b82f6"
COR_PRIMARIA_HOVER = "#2563eb"

# Status
COR_SUCESSO = "#10b981"
COR_SUCESSO_HOVER = "#0c9e6e"
COR_AVISO = "#f59e0b"
COR_ERRO = "#ef4444"
COR_ERRO_HOVER = "#dc2626"
COR_INFO = "#06b6d4"

# Texto
COR_TEXTO = "#f1f5f9"
COR_TEXTO_SECUNDARIO = "#94a3b8"
COR_TEXTO_FRACO = "#64748b"

# Prioridades
COR_EMERGENCIA = "#ef4444"
COR_PRIORITARIO = "#f59e0b"
COR_NORMAL = "#10b981"

# ----------------------------------------------------------------------
# Tipografia
# ----------------------------------------------------------------------
FAMILIA_FONTE = "Segoe UI"
FAMILIA_MONO = "Consolas"

FONTE_TITULO = (FAMILIA_FONTE, 22, "bold")
FONTE_SUBTITULO = (FAMILIA_FONTE, 16, "bold")
FONTE_TEXTO = (FAMILIA_FONTE, 12)
FONTE_TEXTO_BOLD = (FAMILIA_FONTE, 12, "bold")
FONTE_PEQUENA = (FAMILIA_FONTE, 10)
FONTE_LABEL = (FAMILIA_FONTE, 10, "bold")
FONTE_MONO_GRANDE = (FAMILIA_MONO, 48, "bold")
FONTE_MONO_MEDIA = (FAMILIA_MONO, 16, "bold")

# ----------------------------------------------------------------------
# Configurações funcionais
# ----------------------------------------------------------------------
SERVICOS = [
    "Corte de cabelo",
    "Barba",
    "Manicure",
    "Pedicure",
    "Consulta",
    "Avaliação",
    "Retorno",
    "Outro",
]

# Credenciais demo (em produção, usar hash + banco de dados)
USUARIOS_DEMO = {
    "admin": "admin123",
    "operador": "operador123",
}

# Intervalo de auto-refresh das views ativas (em ms)
INTERVALO_REFRESH_MS = 5000

# SGA — Sistema de Gestão de Atendimento

> Aplicação desktop em Python para gerenciamento de filas com prioridade, dashboard em tempo real, gráficos analíticos e exportação de relatórios.

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-1f6feb)
![Matplotlib](https://img.shields.io/badge/Charts-Matplotlib-11557C)
![License](https://img.shields.io/badge/license-Academic-green)
![Status](https://img.shields.io/badge/status-stable-success)

O **SGA** é um sistema corporativo de gestão de atendimento em fila. Estabelecimentos como salões, clínicas, postos e centros de serviço atendem clientes com prioridades distintas (idosos, gestantes, emergências) e precisam de uma ferramenta confiável que organize a fila, registre o histórico e gere indicadores. O SGA cobre todo esse ciclo em uma interface limpa em modo escuro, com dados persistidos em JSON e relatórios exportáveis.

---

## ✨ Principais recursos

- **Tela de login** com credenciais demo (admin / operador) e validação local.
- **Dashboard em tempo real** com cards de métricas, painel do próximo cliente e auto-refresh.
- **Fila com prioridades** (normal · idoso · gestante · emergência), respeitando FIFO dentro de cada faixa.
- **Histórico completo** do dia, em ordem cronológica reversa, com tempo de espera por cliente.
- **Estatísticas analíticas** com 4 gráficos `matplotlib` (atendimentos por serviço, distribuição por prioridade, curva de espera, atendimentos por hora).
- **Relatórios exportáveis** em **CSV** (tabular para BI/Excel) e **TXT** (relatório executivo).
- **Senhas sequenciais únicas** por prioridade (`N001`, `N002`… `P001`… `E001`…), persistidas entre execuções.
- **Persistência automática** em `data/sga_dados.json` após cada operação.
- **Tema dark corporativo** com paleta tipo Linear/Vercel, fontes Segoe UI e Consolas mono.
- **Arquitetura modular** em camadas (`models` / `services` / `ui` / `utils` / `data`), pronta para crescer.

---

## 🧱 Stack técnico

| Camada              | Tecnologia                                                      |
|---------------------|-----------------------------------------------------------------|
| Linguagem           | Python 3.10+                                                    |
| UI                  | [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) |
| Gráficos            | Matplotlib (backend `TkAgg`, tema dark customizado)             |
| Estruturas de dados | `collections.deque` (fila FIFO O(1)), `Counter`                 |
| Persistência        | JSON nativo                                                     |
| Estilo de código    | PEP-8, type hints, docstrings, separação por responsabilidade   |

---

## 🗂️ Estrutura do projeto

```
sga/
├── main.py                          # Ponto de entrada (login → app)
├── requirements.txt                 # Dependências
├── README.md                        # Você está aqui
│
├── data/
│   └── sga_dados.json               # Estado persistido (fila + histórico + contadores)
│
├── models/
│   └── cliente.py                   # Entidade Cliente (OOP, pesos de prioridade, serialização)
│
├── services/
│   ├── senha_service.py             # GeradorSenhas — contadores únicos por prioridade
│   ├── fila_service.py              # FilaAtendimento — operações sobre deque
│   ├── persistencia_service.py      # Carrega/salva estado em JSON
│   ├── estatisticas_service.py      # Indicadores e estimativas
│   └── export_service.py            # Exportação CSV/TXT
│
├── ui/
│   ├── components.py                # MetricCard, PrioridadeBadge (reusáveis)
│   ├── login_window.py              # Tela de autenticação
│   ├── main_window.py               # Janela principal (sidebar + roteamento)
│   ├── dashboard_view.py            # Visão geral em tempo real
│   ├── fila_view.py                 # Cadastro/chamada/remoção de clientes
│   ├── historico_view.py            # Listagem do histórico
│   ├── estatisticas_view.py         # Gráficos matplotlib embarcados
│   └── relatorios_view.py           # Exportação CSV/TXT
│
└── utils/
    ├── constants.py                 # Cores, fontes, identidade do app
    └── helpers.py                   # Formatadores, bind recursivo
```

---

## 🚀 Instalação e execução

### Pré-requisitos

- Python **3.10 ou superior**
- pip atualizado

### Passo a passo

```bash
# 1) Clone ou descompacte o projeto
cd sga

# 2) (Opcional, recomendado) Crie um ambiente virtual
python -m venv .venv
source .venv/bin/activate         # Linux/macOS
.venv\Scripts\activate            # Windows

# 3) Instale as dependências
pip install -r requirements.txt

# 4) Execute
python main.py
```

### Credenciais demo

| Usuário    | Senha          |
|------------|----------------|
| `admin`    | `admin123`     |
| `operador` | `operador123`  |

---

## 🎯 Como usar

1. **Faça login** com uma das credenciais demo.
2. **Dashboard**: visão geral do dia (clientes aguardando, atendidos, tempo médio, próximo a ser chamado).
3. **Fila**: cadastre clientes informando nome, serviço e prioridade. Use a busca para encontrar alguém na fila. Selecione uma linha para chamar ou remover.
4. **Histórico**: confira os atendimentos finalizados, com horários de chegada e atendimento e tempo de espera.
5. **Estatísticas**: visualize os gráficos analíticos do dia.
6. **Relatórios**: exporte CSV (para planilhas) ou TXT (relatório executivo). Um diálogo de salvamento permite escolher a pasta.

Todos os dados são **salvos automaticamente** em `data/sga_dados.json` a cada operação. Ao fechar e reabrir o sistema, fila, histórico e contadores de senha permanecem intactos.

---

## 🏗️ Decisões de arquitetura

### Por que `deque` em vez de `list`?

A fila usa `collections.deque`. O método `popleft()` é **O(1)** — remove o primeiro elemento em tempo constante. Já `list.pop(0)` é **O(n)** porque precisa deslocar todos os outros elementos. Para uma fila que opera continuamente, a diferença é significativa em produção.

A inserção por prioridade (`deque.insert(i, x)`) é O(n) na pior das hipóteses, mas como a fila tem poucos elementos prioritários simultâneos, o impacto é desprezível.

### Pesos de prioridade

Cada `Cliente` carrega um **peso** numérico:

| Prioridade     | Peso |
|----------------|------|
| `emergencia`   | 3    |
| `idoso`        | 2    |
| `gestante`     | 2    |
| `normal`       | 0    |

Na inserção, o algoritmo procura o primeiro cliente com peso **menor** e insere antes dele. Isso preserva o **FIFO dentro de cada faixa** de prioridade.

### Senhas únicas

O `GeradorSenhas` mantém três contadores (`N`, `P`, `E`) e gera senhas sequenciais — nunca aleatórias, nunca repetidas. Os contadores são persistidos junto da fila, garantindo unicidade mesmo após reinicialização.

### Separação por camadas

- `models/` — entidades puras (Cliente). Sem dependência de UI ou I/O.
- `services/` — regras de negócio (fila, persistência, estatísticas, exportação). Sem dependência de UI.
- `ui/` — apenas apresentação. Consome serviços.
- `utils/` — auxiliares transversais.

Essa separação permite testar a lógica em isolamento e trocar a UI por uma web ou TUI sem reescrever a regra de negócio.

---

## 📚 Requisitos acadêmicos atendidos

Este projeto foi originalmente desenvolvido para a disciplina de **Lógica de Programação** e cobre os conceitos das quatro unidades:

| Unidade | Conteúdo                           | Onde aparece                                                       |
|---------|------------------------------------|--------------------------------------------------------------------|
| 1       | Estruturas sequenciais             | Em todos os fluxos (cadastro, chamada, exportação)                 |
| 2       | Estruturas condicionais            | Validações, regras de prioridade, controle de UI                   |
| 3       | Estruturas de repetição            | Renderização de listas, cálculo de estatísticas, exportação        |
| 4       | Estruturas de dados / OOP          | Classes `Cliente`, `FilaAtendimento`, `GeordSenhas`; `deque`, dicts |

Além disso o projeto inclui:

- Tratamento de exceções (`try/except` em I/O, parsing JSON, atualização de UI)
- Persistência em arquivo (`json.dump`/`json.load`)
- Type hints e docstrings em todas as funções públicas
- Interface gráfica profissional com responsividade

---

## 🎁 Diferenciais para o pitch

- **Identidade visual**: nome (SGA), empresa fictícia (QueueFlow Solutions), versão (2.0.0), logo monogramático, rodapé com copyright dinâmico.
- **Loading visual**: o login dá feedback ao validar credenciais.
- **Auto-refresh**: o dashboard e a fila atualizam o tempo de espera a cada 5 segundos sem clique manual.
- **Relógio em tempo real** na top bar (data e hora).
- **Estimativa de espera** baseada em média móvel dos atendimentos recentes.
- **Tema dark corporativo** inspirado em ferramentas como Linear, Vercel e Notion.
- **Gráficos analíticos** em matplotlib com tema dark customizado.

---

## 🛣️ Roadmap (próximos passos sugeridos)

- [ ] Painel público de chamada de senhas (modo TV, fullscreen)
- [ ] Notificação por WhatsApp/SMS via API quando a vez do cliente se aproximar
- [ ] Multi-atendente: várias filas paralelas com seleção por guichê
- [ ] Hash bcrypt + banco SQLite para autenticação real
- [ ] Log de auditoria (quem chamou cada cliente e quando)
- [ ] Configuração de SLA por tipo de serviço com alertas visuais
- [ ] Internacionalização (PT-BR / EN)

---

## 👤 Autoria

Projeto acadêmico — Trabalho de Lógica de Programação.
Refatoração corporativa: arquitetura, UI dark, gráficos, login, exportação.


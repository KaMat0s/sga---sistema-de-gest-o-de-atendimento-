"""Janela principal do SGA — sidebar, top bar e troca de views."""

from datetime import datetime
from tkinter import messagebox

import customtkinter as ctk

from services.fila_service import FilaAtendimento
from services.persistencia_service import carregar, salvar
from ui.dashboard_view import DashboardView
from ui.estatisticas_view import EstatisticasView
from ui.fila_view import FilaView
from ui.historico_view import HistoricoView
from ui.relatorios_view import RelatoriosView
from utils import constants as cfg


# Definição dos itens do menu lateral.
MENU = [
    ("dashboard",     "▦",  "Dashboard"),
    ("fila",          "◷",  "Fila"),
    ("historico",     "≡",  "Histórico"),
    ("estatisticas",  "◔",  "Estatísticas"),
    ("relatorios",    "⤓",  "Relatórios"),
]


TITULOS_VIEW = {
    "dashboard":    "Dashboard",
    "fila":         "Fila de atendimento",
    "historico":    "Histórico do dia",
    "estatisticas": "Estatísticas",
    "relatorios":   "Relatórios",
}


class MainWindow(ctk.CTk):
    """Janela principal — orquestra views, fila e persistência."""

    def __init__(self, usuario: str) -> None:
        super().__init__()

        # Estado da aplicação.
        self.usuario: str = usuario
        self.fila_service: FilaAtendimento = self._carregar_fila()
        self.views: dict = {}
        self.view_atual: str = "dashboard"
        self._botoes_menu: dict = {}

        # Configuração da janela.
        self.title(f"{cfg.APP_NOME} — {cfg.APP_SUBTITULO}")
        self.geometry("1280x780")
        self.minsize(1100, 680)
        self.configure(fg_color=cfg.COR_FUNDO)
        self.protocol("WM_DELETE_WINDOW", self._ao_fechar)

        self._construir()
        self._instanciar_views()
        self._trocar_view("dashboard")
        self._iniciar_relogio()
        self._iniciar_auto_refresh()

    # ------------------------------------------------------------------
    # Estado inicial
    # ------------------------------------------------------------------
    def _carregar_fila(self) -> FilaAtendimento:
        """Carrega fila + histórico + contadores de senhas do disco."""
        return carregar()

    # ------------------------------------------------------------------
    # Construção da UI
    # ------------------------------------------------------------------
    def _construir(self) -> None:
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self._construir_sidebar()
        self._construir_area_principal()

    def _construir_sidebar(self) -> None:
        sidebar = ctk.CTkFrame(
            self,
            fg_color=cfg.COR_FUNDO_CLARO,
            width=240,
            corner_radius=0,
        )
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        sidebar.grid_rowconfigure(2, weight=1)

        # Logo / cabeçalho.
        marca = ctk.CTkFrame(sidebar, fg_color="transparent")
        marca.grid(row=0, column=0, sticky="ew", padx=20, pady=(24, 8))

        ctk.CTkLabel(
            marca,
            text="◆",
            text_color=cfg.COR_PRIMARIA,
            font=(cfg.FAMILIA_FONTE, 28, "bold"),
        ).pack(side="left", padx=(0, 8))

        bloco_texto = ctk.CTkFrame(marca, fg_color="transparent")
        bloco_texto.pack(side="left")
        ctk.CTkLabel(
            bloco_texto,
            text=cfg.APP_NOME,
            text_color=cfg.COR_TEXTO,
            font=(cfg.FAMILIA_FONTE, 22, "bold"),
        ).pack(anchor="w")
        ctk.CTkLabel(
            bloco_texto,
            text=cfg.APP_SUBTITULO,
            text_color=cfg.COR_TEXTO_SECUNDARIO,
            font=(cfg.FAMILIA_FONTE, 9),
        ).pack(anchor="w")

        # Separador.
        sep = ctk.CTkFrame(sidebar, fg_color=cfg.COR_BORDA, height=1)
        sep.grid(row=1, column=0, sticky="ew", padx=20, pady=(12, 12))

        # Menu de navegação.
        menu_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        menu_frame.grid(row=2, column=0, sticky="nsew", padx=12)

        for chave, simbolo, rotulo in MENU:
            botao = ctk.CTkButton(
                menu_frame,
                text=f"  {simbolo}   {rotulo}",
                anchor="w",
                fg_color="transparent",
                hover_color=cfg.COR_CARD_HOVER,
                text_color=cfg.COR_TEXTO_SECUNDARIO,
                corner_radius=6,
                height=42,
                font=(cfg.FAMILIA_FONTE, 12),
                command=lambda c=chave: self._trocar_view(c),
            )
            botao.pack(fill="x", pady=2)
            self._botoes_menu[chave] = botao

        # Card "conectado como".
        usuario_card = ctk.CTkFrame(
            sidebar,
            fg_color=cfg.COR_CARD,
            corner_radius=8,
            border_width=1,
            border_color=cfg.COR_BORDA,
        )
        usuario_card.grid(row=3, column=0, sticky="ew", padx=14, pady=(12, 14))

        ctk.CTkLabel(
            usuario_card,
            text="CONECTADO",
            text_color=cfg.COR_TEXTO_SECUNDARIO,
            font=(cfg.FAMILIA_FONTE, 8, "bold"),
        ).pack(anchor="w", padx=12, pady=(10, 0))

        linha = ctk.CTkFrame(usuario_card, fg_color="transparent")
        linha.pack(fill="x", padx=12, pady=(2, 10))
        ctk.CTkLabel(
            linha,
            text="●",
            text_color=cfg.COR_SUCESSO,
            font=(cfg.FAMILIA_FONTE, 12, "bold"),
        ).pack(side="left", padx=(0, 6))
        ctk.CTkLabel(
            linha,
            text=self.usuario.title(),
            text_color=cfg.COR_TEXTO,
            font=(cfg.FAMILIA_FONTE, 12, "bold"),
        ).pack(side="left")

        # Rodapé com versão e empresa.
        rodape = ctk.CTkFrame(sidebar, fg_color="transparent")
        rodape.grid(row=4, column=0, sticky="ew", padx=20, pady=(0, 16))
        ctk.CTkLabel(
            rodape,
            text=f"v{cfg.APP_VERSAO}  •  {cfg.APP_EMPRESA}",
            text_color=cfg.COR_TEXTO_FRACO,
            font=(cfg.FAMILIA_FONTE, 8),
        ).pack(anchor="w")

    def _construir_area_principal(self) -> None:
        area = ctk.CTkFrame(self, fg_color=cfg.COR_FUNDO, corner_radius=0)
        area.grid(row=0, column=1, sticky="nsew")
        area.grid_rowconfigure(1, weight=1)
        area.grid_columnconfigure(0, weight=1)

        # Top bar.
        topbar = ctk.CTkFrame(area, fg_color="transparent", height=70)
        topbar.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 6))
        topbar.grid_propagate(False)
        topbar.grid_columnconfigure(0, weight=1)

        self.label_titulo = ctk.CTkLabel(
            topbar,
            text="Dashboard",
            text_color=cfg.COR_TEXTO,
            font=(cfg.FAMILIA_FONTE, 18, "bold"),
        )
        self.label_titulo.grid(row=0, column=0, sticky="w", pady=(8, 0))

        relogio_box = ctk.CTkFrame(topbar, fg_color="transparent")
        relogio_box.grid(row=0, column=1, sticky="e", pady=(8, 0))

        self.label_data = ctk.CTkLabel(
            relogio_box,
            text="",
            text_color=cfg.COR_TEXTO_SECUNDARIO,
            font=(cfg.FAMILIA_FONTE, 11),
        )
        self.label_data.pack(anchor="e")

        self.label_hora = ctk.CTkLabel(
            relogio_box,
            text="",
            text_color=cfg.COR_TEXTO,
            font=(cfg.FAMILIA_MONO, 18, "bold"),
        )
        self.label_hora.pack(anchor="e")

        # Container de conteúdo (onde as views são empacotadas).
        self.container = ctk.CTkFrame(area, fg_color="transparent")
        self.container.grid(row=1, column=0, sticky="nsew", padx=24, pady=(6, 8))

        # Rodapé.
        rodape = ctk.CTkFrame(area, fg_color="transparent", height=28)
        rodape.grid(row=2, column=0, sticky="ew", padx=24, pady=(0, 10))
        ctk.CTkLabel(
            rodape,
            text=(
                f"© {datetime.now().year} {cfg.APP_EMPRESA}  •  "
                f"{cfg.APP_NOME} v{cfg.APP_VERSAO}"
            ),
            text_color=cfg.COR_TEXTO_FRACO,
            font=(cfg.FAMILIA_FONTE, 9),
        ).pack(side="left")

    # ------------------------------------------------------------------
    # Views
    # ------------------------------------------------------------------
    def _instanciar_views(self) -> None:
        self.views = {
            "dashboard":    DashboardView(self.container, self),
            "fila":         FilaView(self.container, self),
            "historico":    HistoricoView(self.container, self),
            "estatisticas": EstatisticasView(self.container, self),
            "relatorios":   RelatoriosView(self.container, self),
        }

    def _trocar_view(self, chave: str) -> None:
        if chave not in self.views:
            return

        # Esconde a view atual.
        for view in self.views.values():
            view.pack_forget()

        view = self.views[chave]
        view.pack(fill="both", expand=True)
        self.view_atual = chave

        # Atualiza estilo dos botões do menu.
        for c, botao in self._botoes_menu.items():
            if c == chave:
                botao.configure(
                    fg_color=cfg.COR_PRIMARIA,
                    text_color="white",
                )
            else:
                botao.configure(
                    fg_color="transparent",
                    text_color=cfg.COR_TEXTO_SECUNDARIO,
                )

        # Atualiza o título da top bar.
        self.label_titulo.configure(text=TITULOS_VIEW.get(chave, chave.title()))

        # Hook lifecycle.
        if hasattr(view, "on_show"):
            view.on_show()

    def notificar_mudanca(self) -> None:
        """Notifica todas as views que houve mudança nos dados.

        Cada view decide se vai re-renderizar imediatamente ou aguardar.
        Após notificar, persiste o estado em disco.
        """
        for view in self.views.values():
            if hasattr(view, "on_data_changed"):
                view.on_data_changed()
        self._salvar()

    # ------------------------------------------------------------------
    # Relógio e auto-refresh
    # ------------------------------------------------------------------
    def _iniciar_relogio(self) -> None:
        self._atualizar_relogio()

    def _atualizar_relogio(self) -> None:
        agora = datetime.now()
        self.label_data.configure(text=agora.strftime("%A, %d de %B de %Y").capitalize())
        self.label_hora.configure(text=agora.strftime("%H:%M:%S"))
        self.after(1000, self._atualizar_relogio)

    def _iniciar_auto_refresh(self) -> None:
        """Dispara `on_tick` na view ativa periodicamente."""
        view = self.views.get(self.view_atual)
        if view is not None and hasattr(view, "on_tick"):
            try:
                view.on_tick()
            except Exception as erro:  # noqa: BLE001
                print(f"[on_tick:{self.view_atual}] {erro}")
        self.after(cfg.INTERVALO_REFRESH_MS, self._iniciar_auto_refresh)

    # ------------------------------------------------------------------
    # Persistência
    # ------------------------------------------------------------------
    def _salvar(self) -> None:
        try:
            salvar(self.fila_service)
        except Exception as erro:  # noqa: BLE001
            print(f"[persistencia] erro ao salvar: {erro}")

    def _ao_fechar(self) -> None:
        confirmar = messagebox.askyesno(
            "Encerrar sessão",
            "Deseja realmente sair do sistema?\n"
            "O estado atual será salvo automaticamente.",
        )
        if not confirmar:
            return
        self._salvar()
        self.destroy()

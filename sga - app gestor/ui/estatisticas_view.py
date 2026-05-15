"""View de estatísticas — métricas detalhadas e gráficos matplotlib."""

import matplotlib
matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import customtkinter as ctk

from services.estatisticas_service import estatisticas_completas
from utils import constants as cfg


# ----------------------------------------------------------------------
# Tema dark do matplotlib (aplicado globalmente)
# ----------------------------------------------------------------------
plt.rcParams.update(
    {
        "figure.facecolor": cfg.COR_CARD,
        "axes.facecolor": cfg.COR_CARD,
        "axes.edgecolor": cfg.COR_BORDA,
        "axes.labelcolor": cfg.COR_TEXTO_SECUNDARIO,
        "axes.titlecolor": cfg.COR_TEXTO,
        "axes.titleweight": "bold",
        "xtick.color": cfg.COR_TEXTO_SECUNDARIO,
        "ytick.color": cfg.COR_TEXTO_SECUNDARIO,
        "grid.color": cfg.COR_BORDA,
        "grid.alpha": 0.3,
        "text.color": cfg.COR_TEXTO,
        "font.family": cfg.FAMILIA_FONTE,
        "font.size": 9,
    }
)


CORES_PRIORIDADE = {
    "emergencia": cfg.COR_EMERGENCIA,
    "idoso": cfg.COR_PRIORITARIO,
    "gestante": "#fbbf24",
    "normal": cfg.COR_NORMAL,
}


class EstatisticasView(ctk.CTkFrame):
    """Exibe gráficos e indicadores agregados sobre o histórico."""

    def __init__(self, master, main_window):
        super().__init__(master, fg_color="transparent")
        self.main_window = main_window
        self._canvases: list = []
        self._construir()

    # ------------------------------------------------------------------
    # Construção
    # ------------------------------------------------------------------
    def _construir(self) -> None:
        topo = ctk.CTkFrame(self, fg_color="transparent")
        topo.pack(fill="x", pady=(0, 14))
        ctk.CTkLabel(
            topo,
            text="Estatísticas",
            text_color=cfg.COR_TEXTO,
            font=(cfg.FAMILIA_FONTE, 22, "bold"),
        ).pack(anchor="w")
        ctk.CTkLabel(
            topo,
            text="Indicadores agregados e visualizações do dia",
            text_color=cfg.COR_TEXTO_SECUNDARIO,
            font=(cfg.FAMILIA_FONTE, 11),
        ).pack(anchor="w")

        # Container rolável (gráficos podem ocupar bastante espaço).
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True)

        # Linha de resumo numérico.
        self.resumo_frame = ctk.CTkFrame(
            self.scroll,
            fg_color=cfg.COR_CARD,
            corner_radius=12,
            border_width=1,
            border_color=cfg.COR_BORDA,
        )
        self.resumo_frame.pack(fill="x", pady=(0, 12))

        # Destaque: cliente com maior espera.
        self.destaque_frame = ctk.CTkFrame(
            self.scroll,
            fg_color=cfg.COR_CARD,
            corner_radius=12,
            border_width=1,
            border_color=cfg.COR_BORDA,
        )
        self.destaque_frame.pack(fill="x", pady=(0, 12))

        # Grid 2x2 de gráficos.
        self.graficos_grid = ctk.CTkFrame(self.scroll, fg_color="transparent")
        self.graficos_grid.pack(fill="both", expand=True)
        self.graficos_grid.grid_columnconfigure(0, weight=1, uniform="g")
        self.graficos_grid.grid_columnconfigure(1, weight=1, uniform="g")

    # ------------------------------------------------------------------
    # Renderização: resumo numérico + destaque
    # ------------------------------------------------------------------
    def _renderizar_resumo(self, stats: dict) -> None:
        for widget in self.resumo_frame.winfo_children():
            widget.destroy()

        container = ctk.CTkFrame(self.resumo_frame, fg_color="transparent")
        container.pack(fill="x", padx=20, pady=18)

        itens = [
            ("Total atendidos", str(stats["total_atendidos"]), cfg.COR_SUCESSO),
            (
                "Tempo médio",
                f"{stats['tempo_medio']:.1f} min" if stats["total_atendidos"] else "—",
                cfg.COR_PRIMARIA,
            ),
            (
                "Maior espera",
                f"{stats['tempo_max']:.1f} min" if stats["total_atendidos"] else "—",
                cfg.COR_AVISO,
            ),
            (
                "Tempo total",
                f"{stats['tempo_total']:.0f} min" if stats["total_atendidos"] else "—",
                cfg.COR_INFO,
            ),
        ]

        for i in range(len(itens)):
            container.grid_columnconfigure(i, weight=1, uniform="resumo")

        for idx, (titulo, valor, cor) in enumerate(itens):
            bloco = ctk.CTkFrame(container, fg_color="transparent")
            bloco.grid(row=0, column=idx, sticky="nsew", padx=10)
            ctk.CTkLabel(
                bloco,
                text=titulo.upper(),
                text_color=cfg.COR_TEXTO_SECUNDARIO,
                font=(cfg.FAMILIA_FONTE, 9, "bold"),
            ).pack(anchor="w")
            ctk.CTkLabel(
                bloco,
                text=valor,
                text_color=cor,
                font=(cfg.FAMILIA_FONTE, 24, "bold"),
            ).pack(anchor="w", pady=(2, 0))

    def _renderizar_destaque(self, stats: dict) -> None:
        for widget in self.destaque_frame.winfo_children():
            widget.destroy()

        cliente = stats["cliente_maior_espera"]

        bloco = ctk.CTkFrame(self.destaque_frame, fg_color="transparent")
        bloco.pack(fill="x", padx=20, pady=18)

        ctk.CTkLabel(
            bloco,
            text="CLIENTE COM MAIOR TEMPO DE ESPERA",
            text_color=cfg.COR_TEXTO_SECUNDARIO,
            font=(cfg.FAMILIA_FONTE, 9, "bold"),
        ).pack(anchor="w")

        if cliente is None:
            ctk.CTkLabel(
                bloco,
                text="Nenhum atendimento registrado",
                text_color=cfg.COR_TEXTO_FRACO,
                font=(cfg.FAMILIA_FONTE, 14),
            ).pack(anchor="w", pady=(6, 0))
            return

        texto = (
            f"{cliente.nome}  ({cliente.senha})  —  "
            f"{cliente.tempo_espera():.1f} min em {cliente.servico}"
        )
        ctk.CTkLabel(
            bloco,
            text=texto,
            text_color=cfg.COR_TEXTO,
            font=(cfg.FAMILIA_FONTE, 16, "bold"),
        ).pack(anchor="w", pady=(4, 0))

    # ------------------------------------------------------------------
    # Renderização: gráficos
    # ------------------------------------------------------------------
    def _renderizar_graficos(self, stats: dict) -> None:
        # Limpa canvases anteriores.
        for canvas in self._canvases:
            canvas.get_tk_widget().destroy()
            plt.close(canvas.figure)
        self._canvases.clear()

        for widget in self.graficos_grid.winfo_children():
            widget.destroy()

        if stats["total_atendidos"] == 0:
            vazio = ctk.CTkFrame(
                self.graficos_grid,
                fg_color=cfg.COR_CARD,
                corner_radius=12,
                border_width=1,
                border_color=cfg.COR_BORDA,
            )
            vazio.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=6, pady=6)
            ctk.CTkLabel(
                vazio,
                text="Os gráficos serão exibidos após o primeiro atendimento concluído",
                text_color=cfg.COR_TEXTO_FRACO,
                font=(cfg.FAMILIA_FONTE, 12),
            ).pack(pady=60)
            return

        self._grafico_por_servico(stats, 0, 0)
        self._grafico_por_prioridade(stats, 0, 1)
        self._grafico_tempo_espera(1, 0)
        self._grafico_por_hora(stats, 1, 1)

    def _moldura(self, row: int, col: int, titulo: str) -> ctk.CTkFrame:
        """Cria uma moldura padrão para alocar um gráfico."""
        frame = ctk.CTkFrame(
            self.graficos_grid,
            fg_color=cfg.COR_CARD,
            corner_radius=12,
            border_width=1,
            border_color=cfg.COR_BORDA,
        )
        frame.grid(row=row, column=col, sticky="nsew", padx=6, pady=6)
        ctk.CTkLabel(
            frame,
            text=titulo.upper(),
            text_color=cfg.COR_TEXTO_SECUNDARIO,
            font=(cfg.FAMILIA_FONTE, 9, "bold"),
        ).pack(anchor="w", padx=16, pady=(14, 4))
        return frame

    def _embed(self, fig: Figure, parent) -> None:
        """Embute uma Figure matplotlib dentro de um frame CustomTkinter."""
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=(0, 10))
        self._canvases.append(canvas)

    def _grafico_por_servico(self, stats: dict, row: int, col: int) -> None:
        frame = self._moldura(row, col, "Atendimentos por serviço")

        dados = stats["por_servico"]
        labels = list(dados.keys())
        valores = list(dados.values())

        fig = Figure(figsize=(4.5, 3.0), dpi=90)
        ax = fig.add_subplot(111)
        barras = ax.barh(labels, valores, color=cfg.COR_PRIMARIA, height=0.6)
        ax.set_xlabel("Quantidade")
        ax.invert_yaxis()
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.grid(axis="x", linestyle="--", alpha=0.25)

        for barra, valor in zip(barras, valores):
            ax.text(
                barra.get_width() + max(valores) * 0.02,
                barra.get_y() + barra.get_height() / 2,
                str(valor),
                va="center",
                color=cfg.COR_TEXTO,
                fontsize=9,
            )

        fig.tight_layout()
        self._embed(fig, frame)

    def _grafico_por_prioridade(self, stats: dict, row: int, col: int) -> None:
        frame = self._moldura(row, col, "Distribuição por prioridade")

        dados = stats["por_prioridade"]
        labels = [p.title() for p in dados.keys()]
        valores = list(dados.values())
        cores = [CORES_PRIORIDADE.get(p, cfg.COR_PRIMARIA) for p in dados.keys()]

        fig = Figure(figsize=(4.5, 3.0), dpi=90)
        ax = fig.add_subplot(111)
        wedges, texts, autotexts = ax.pie(
            valores,
            labels=labels,
            colors=cores,
            autopct="%1.0f%%",
            startangle=90,
            wedgeprops={"edgecolor": cfg.COR_CARD, "linewidth": 2},
            textprops={"color": cfg.COR_TEXTO, "fontsize": 9},
        )
        for autotext in autotexts:
            autotext.set_color("white")
            autotext.set_fontweight("bold")
        ax.set_aspect("equal")
        fig.tight_layout()
        self._embed(fig, frame)

    def _grafico_tempo_espera(self, row: int, col: int) -> None:
        frame = self._moldura(row, col, "Tempo de espera por atendimento")

        historico = self.main_window.fila_service.historico
        tempos = [c.tempo_espera() for c in historico]
        indices = list(range(1, len(tempos) + 1))

        fig = Figure(figsize=(4.5, 3.0), dpi=90)
        ax = fig.add_subplot(111)
        ax.plot(
            indices,
            tempos,
            color=cfg.COR_PRIMARIA,
            linewidth=2,
            marker="o",
            markersize=4,
            markerfacecolor=cfg.COR_PRIMARIA,
        )
        ax.fill_between(indices, tempos, alpha=0.15, color=cfg.COR_PRIMARIA)
        ax.set_xlabel("Atendimento (ordem)")
        ax.set_ylabel("Tempo (min)")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.grid(linestyle="--", alpha=0.25)
        fig.tight_layout()
        self._embed(fig, frame)

    def _grafico_por_hora(self, stats: dict, row: int, col: int) -> None:
        frame = self._moldura(row, col, "Atendimentos por hora do dia")

        dados = stats["por_hora"]
        horas = list(dados.keys())
        valores = list(dados.values())

        fig = Figure(figsize=(4.5, 3.0), dpi=90)
        ax = fig.add_subplot(111)
        ax.bar(
            horas,
            valores,
            color=cfg.COR_INFO,
            width=0.7,
            edgecolor=cfg.COR_CARD,
        )
        ax.set_xlabel("Hora")
        ax.set_ylabel("Quantidade")
        if horas:
            ax.set_xticks(horas)
            ax.set_xticklabels([f"{h:02d}h" for h in horas])
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.grid(axis="y", linestyle="--", alpha=0.25)
        fig.tight_layout()
        self._embed(fig, frame)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    def _atualizar(self) -> None:
        fs = self.main_window.fila_service
        stats = estatisticas_completas(fs.historico, list(fs.fila))
        self._renderizar_resumo(stats)
        self._renderizar_destaque(stats)
        self._renderizar_graficos(stats)

    def on_show(self) -> None:
        self._atualizar()

    def on_data_changed(self) -> None:
        # Re-renderizar gráficos é caro; só faz se a view está visível.
        if self.main_window.view_atual == "estatisticas":
            self._atualizar()

    def on_tick(self) -> None:
        # Estatísticas históricas não mudam com o relógio.
        pass

    def destroy(self) -> None:
        """Limpa figuras matplotlib ao destruir a view."""
        for canvas in self._canvases:
            plt.close(canvas.figure)
        self._canvases.clear()
        super().destroy()

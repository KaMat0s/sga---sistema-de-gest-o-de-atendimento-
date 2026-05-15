"""Dashboard com indicadores em tempo real."""

import customtkinter as ctk

from services.estatisticas_service import (
    estatisticas_completas,
    estimar_espera,
)
from ui.components import MetricCard
from utils import constants as cfg


class DashboardView(ctk.CTkFrame):
    """View principal com visão geral e métricas em tempo real."""

    def __init__(self, master, main_window):
        super().__init__(master, fg_color="transparent")
        self.main_window = main_window
        self._construir()

    # ------------------------------------------------------------------
    # Construção
    # ------------------------------------------------------------------
    def _construir(self) -> None:
        # Boas-vindas
        topo = ctk.CTkFrame(self, fg_color="transparent")
        topo.pack(fill="x", pady=(0, 16))
        ctk.CTkLabel(
            topo,
            text=f"Bem-vindo, {self.main_window.usuario.title()}",
            text_color=cfg.COR_TEXTO,
            font=(cfg.FAMILIA_FONTE, 22, "bold"),
        ).pack(anchor="w")
        ctk.CTkLabel(
            topo,
            text="Visão geral do atendimento em tempo real",
            text_color=cfg.COR_TEXTO_SECUNDARIO,
            font=(cfg.FAMILIA_FONTE, 11),
        ).pack(anchor="w")

        # Linha 1 - métricas principais
        cards1 = ctk.CTkFrame(self, fg_color="transparent")
        cards1.pack(fill="x", pady=(0, 12))
        for i in range(4):
            cards1.grid_columnconfigure(i, weight=1, uniform="cards1")

        self.card_aguardando = MetricCard(
            cards1, "Aguardando", "0",
            cor_destaque=cfg.COR_INFO, icone="◷",
        )
        self.card_atendidos = MetricCard(
            cards1, "Atendidos hoje", "0",
            cor_destaque=cfg.COR_SUCESSO, icone="✓",
        )
        self.card_tempo_medio = MetricCard(
            cards1, "Tempo médio", "—",
            cor_destaque=cfg.COR_PRIMARIA, icone="⏱",
        )
        self.card_estimativa = MetricCard(
            cards1, "Próxima vaga em", "—",
            cor_destaque=cfg.COR_AVISO, icone="◐",
        )

        for i, card in enumerate(
            [
                self.card_aguardando,
                self.card_atendidos,
                self.card_tempo_medio,
                self.card_estimativa,
            ]
        ):
            card.grid(row=0, column=i, padx=6, sticky="nsew")

        # Linha 2 - métricas secundárias
        cards2 = ctk.CTkFrame(self, fg_color="transparent")
        cards2.pack(fill="x", pady=(0, 14))
        cards2.grid_columnconfigure(0, weight=1, uniform="cards2")
        cards2.grid_columnconfigure(1, weight=1, uniform="cards2")

        self.card_servico_top = MetricCard(
            cards2, "Serviço mais procurado", "—",
            cor_destaque=cfg.COR_INFO, icone="★",
        )
        self.card_prioridade_top = MetricCard(
            cards2, "Prioridade mais frequente", "—",
            cor_destaque=cfg.COR_PRIMARIA, icone="◉",
        )
        self.card_servico_top.grid(row=0, column=0, padx=6, sticky="nsew")
        self.card_prioridade_top.grid(row=0, column=1, padx=6, sticky="nsew")

        # Painel "próximo a ser chamado"
        painel = ctk.CTkFrame(
            self,
            fg_color=cfg.COR_CARD,
            corner_radius=12,
            border_width=1,
            border_color=cfg.COR_BORDA,
        )
        painel.pack(fill="both", expand=True)

        ctk.CTkLabel(
            painel,
            text="PRÓXIMO A SER CHAMADO",
            text_color=cfg.COR_TEXTO_SECUNDARIO,
            font=cfg.FONTE_LABEL,
        ).pack(anchor="w", padx=24, pady=(20, 8))

        self.painel_proximo = ctk.CTkFrame(painel, fg_color="transparent")
        self.painel_proximo.pack(fill="both", expand=True, padx=24, pady=(0, 20))

    # ------------------------------------------------------------------
    # Atualização
    # ------------------------------------------------------------------
    def _atualizar_proximo(self) -> None:
        """Atualiza o painel destacando o próximo cliente da fila."""
        for w in self.painel_proximo.winfo_children():
            w.destroy()

        proximo = self.main_window.fila_service.proximo()
        if proximo is None:
            ctk.CTkLabel(
                self.painel_proximo,
                text="✓  Nenhum cliente aguardando no momento",
                text_color=cfg.COR_TEXTO_SECUNDARIO,
                font=(cfg.FAMILIA_FONTE, 14),
            ).pack(pady=20)
            return

        # Coluna da senha (destaque grande)
        bloco_senha = ctk.CTkFrame(self.painel_proximo, fg_color="transparent")
        bloco_senha.pack(side="left", padx=(0, 24))
        ctk.CTkLabel(
            bloco_senha,
            text=proximo.senha,
            text_color=cfg.COR_PRIMARIA,
            font=cfg.FONTE_MONO_GRANDE,
        ).pack(anchor="w")

        # Coluna de informações
        bloco_info = ctk.CTkFrame(self.painel_proximo, fg_color="transparent")
        bloco_info.pack(side="left", fill="both", expand=True)
        ctk.CTkLabel(
            bloco_info,
            text=proximo.nome,
            text_color=cfg.COR_TEXTO,
            font=(cfg.FAMILIA_FONTE, 22, "bold"),
        ).pack(anchor="w")
        ctk.CTkLabel(
            bloco_info,
            text=(
                f"{proximo.servico}  •  "
                f"Esperando há {proximo.tempo_espera():.0f} min  •  "
                f"Prioridade: {proximo.prioridade.title()}"
            ),
            text_color=cfg.COR_TEXTO_SECUNDARIO,
            font=(cfg.FAMILIA_FONTE, 12),
        ).pack(anchor="w", pady=(2, 0))

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    def on_show(self) -> None:
        self.on_data_changed()

    def on_data_changed(self) -> None:
        fs = self.main_window.fila_service
        stats = estatisticas_completas(fs.historico, list(fs.fila))

        self.card_aguardando.atualizar(str(stats["total_aguardando"]))
        self.card_atendidos.atualizar(str(stats["total_atendidos"]))

        if stats["total_atendidos"] > 0:
            self.card_tempo_medio.atualizar(f"{stats['tempo_medio']:.1f} min")
        else:
            self.card_tempo_medio.atualizar("—")

        if stats["total_aguardando"] > 0:
            estimativa = estimar_espera(fs.historico, stats["total_aguardando"])
            self.card_estimativa.atualizar(f"{estimativa:.0f} min")
        else:
            self.card_estimativa.atualizar("—")

        self.card_servico_top.atualizar(stats["servico_top"])
        self.card_prioridade_top.atualizar(stats["prioridade_top"].title())

        self._atualizar_proximo()

    def on_tick(self) -> None:
        # Apenas atualiza o painel de "próximo" para refletir o tempo de espera.
        if self.main_window.view_atual == "dashboard":
            self._atualizar_proximo()

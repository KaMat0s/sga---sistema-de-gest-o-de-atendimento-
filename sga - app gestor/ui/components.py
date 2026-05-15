"""Componentes de interface reutilizáveis."""

import customtkinter as ctk

from utils import constants as cfg


class MetricCard(ctk.CTkFrame):
    """Card de métrica para o dashboard, com ícone, título e valor destacado."""

    def __init__(
        self,
        master,
        titulo: str,
        valor: str,
        cor_destaque: str = cfg.COR_PRIMARIA,
        icone: str = "●",
        **kwargs,
    ):
        super().__init__(
            master,
            fg_color=cfg.COR_CARD,
            corner_radius=12,
            border_width=1,
            border_color=cfg.COR_BORDA,
            **kwargs,
        )

        self._icone = ctk.CTkLabel(
            self,
            text=icone,
            text_color=cor_destaque,
            font=(cfg.FAMILIA_FONTE, 22, "bold"),
        )
        self._icone.pack(anchor="w", padx=20, pady=(18, 0))

        self._titulo = ctk.CTkLabel(
            self,
            text=titulo.upper(),
            text_color=cfg.COR_TEXTO_SECUNDARIO,
            font=(cfg.FAMILIA_FONTE, 10, "bold"),
        )
        self._titulo.pack(anchor="w", padx=20, pady=(4, 0))

        self._valor = ctk.CTkLabel(
            self,
            text=valor,
            text_color=cfg.COR_TEXTO,
            font=(cfg.FAMILIA_FONTE, 28, "bold"),
        )
        self._valor.pack(anchor="w", padx=20, pady=(2, 18))

    def atualizar(self, valor: str) -> None:
        """Atualiza somente o valor numérico do card."""
        self._valor.configure(text=valor)


class PrioridadeBadge(ctk.CTkLabel):
    """Badge colorido indicando a prioridade do cliente."""

    CONFIG = {
        "emergencia": (cfg.COR_EMERGENCIA, "EMERGÊNCIA"),
        "idoso": (cfg.COR_PRIORITARIO, "IDOSO"),
        "gestante": (cfg.COR_PRIORITARIO, "GESTANTE"),
        "normal": (cfg.COR_NORMAL, "NORMAL"),
    }

    def __init__(self, master, prioridade: str, **kwargs):
        cor, texto = self.CONFIG.get(prioridade, self.CONFIG["normal"])
        super().__init__(
            master,
            text=texto,
            text_color="white",
            fg_color=cor,
            corner_radius=4,
            font=(cfg.FAMILIA_FONTE, 9, "bold"),
            width=92,
            height=22,
            **kwargs,
        )

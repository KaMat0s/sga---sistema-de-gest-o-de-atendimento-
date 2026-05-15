"""View de histórico — listagem dos atendimentos concluídos no dia."""

import customtkinter as ctk

from models.cliente import Cliente
from ui.components import PrioridadeBadge
from utils import constants as cfg


CORES_BARRA = {
    "emergencia": cfg.COR_EMERGENCIA,
    "idoso": cfg.COR_PRIORITARIO,
    "gestante": cfg.COR_PRIORITARIO,
    "normal": cfg.COR_NORMAL,
}


class HistoricoView(ctk.CTkFrame):
    """Exibe o histórico de atendimentos do dia em ordem cronológica reversa."""

    def __init__(self, master, main_window):
        super().__init__(master, fg_color="transparent")
        self.main_window = main_window
        self._construir()

    # ------------------------------------------------------------------
    # Construção
    # ------------------------------------------------------------------
    def _construir(self) -> None:
        topo = ctk.CTkFrame(self, fg_color="transparent")
        topo.pack(fill="x", pady=(0, 14))

        ctk.CTkLabel(
            topo,
            text="Histórico de atendimentos",
            text_color=cfg.COR_TEXTO,
            font=(cfg.FAMILIA_FONTE, 22, "bold"),
        ).pack(anchor="w")

        self.label_resumo = ctk.CTkLabel(
            topo,
            text="Nenhum atendimento concluído ainda",
            text_color=cfg.COR_TEXTO_SECUNDARIO,
            font=(cfg.FAMILIA_FONTE, 11),
        )
        self.label_resumo.pack(anchor="w")

        painel = ctk.CTkFrame(
            self,
            fg_color=cfg.COR_CARD,
            corner_radius=12,
            border_width=1,
            border_color=cfg.COR_BORDA,
        )
        painel.pack(fill="both", expand=True)

        self.scroll = ctk.CTkScrollableFrame(painel, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=14, pady=14)

    # ------------------------------------------------------------------
    # Renderização
    # ------------------------------------------------------------------
    def _renderizar(self) -> None:
        for widget in self.scroll.winfo_children():
            widget.destroy()

        historico = self.main_window.fila_service.historico
        total = len(historico)

        if total == 0:
            self.label_resumo.configure(
                text="Nenhum atendimento concluído ainda"
            )
            ctk.CTkLabel(
                self.scroll,
                text="Os atendimentos concluídos aparecerão aqui",
                text_color=cfg.COR_TEXTO_FRACO,
                font=(cfg.FAMILIA_FONTE, 12),
            ).pack(pady=40)
            return

        self.label_resumo.configure(
            text=f"{total} atendimento(s) concluído(s) — mais recentes primeiro"
        )

        # Ordem reversa: o atendimento mais recente aparece no topo.
        for cliente in reversed(historico):
            self._linha(cliente)

    def _linha(self, cliente: Cliente) -> None:
        """Cria uma linha de histórico para o cliente informado."""
        cor_barra = CORES_BARRA.get(cliente.prioridade, cfg.COR_NORMAL)

        linha = ctk.CTkFrame(
            self.scroll,
            fg_color=cfg.COR_FUNDO_CLARO,
            corner_radius=8,
            height=72,
        )
        linha.pack(fill="x", pady=4)
        linha.pack_propagate(False)

        # Barra colorida lateral indicando a prioridade.
        barra = ctk.CTkFrame(linha, fg_color=cor_barra, width=4, corner_radius=0)
        barra.pack(side="left", fill="y")

        # Senha em destaque.
        ctk.CTkLabel(
            linha,
            text=cliente.senha,
            text_color=cfg.COR_PRIMARIA,
            font=cfg.FONTE_MONO_MEDIA,
            width=80,
        ).pack(side="left", padx=(14, 6))

        # Bloco central de informações.
        info = ctk.CTkFrame(linha, fg_color="transparent")
        info.pack(side="left", fill="both", expand=True, padx=10, pady=8)

        ctk.CTkLabel(
            info,
            text=cliente.nome,
            text_color=cfg.COR_TEXTO,
            font=(cfg.FAMILIA_FONTE, 12, "bold"),
            anchor="w",
        ).pack(fill="x")

        chegada = cliente.horario_chegada.strftime("%H:%M")
        atendimento = (
            cliente.horario_atendimento.strftime("%H:%M")
            if cliente.horario_atendimento
            else "—"
        )
        ctk.CTkLabel(
            info,
            text=(
                f"{cliente.servico}  •  chegou {chegada}  →  "
                f"atendido {atendimento}  •  esperou "
                f"{cliente.tempo_espera():.1f} min"
            ),
            text_color=cfg.COR_TEXTO_SECUNDARIO,
            font=(cfg.FAMILIA_FONTE, 10),
            anchor="w",
        ).pack(fill="x")

        PrioridadeBadge(linha, cliente.prioridade).pack(side="right", padx=14)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    def on_show(self) -> None:
        self._renderizar()

    def on_data_changed(self) -> None:
        self._renderizar()

    def on_tick(self) -> None:
        # O histórico não muda passivamente. Nada a fazer.
        pass

"""View de relatórios — exportação do histórico em CSV ou TXT."""

from datetime import datetime
from tkinter import filedialog

import customtkinter as ctk

from services.export_service import exportar_csv, exportar_txt
from utils import constants as cfg


class RelatoriosView(ctk.CTkFrame):
    """Tela com cards de exportação em diferentes formatos."""

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
            text="Relatórios",
            text_color=cfg.COR_TEXTO,
            font=(cfg.FAMILIA_FONTE, 22, "bold"),
        ).pack(anchor="w")
        ctk.CTkLabel(
            topo,
            text="Exporte o histórico de atendimentos para análise externa",
            text_color=cfg.COR_TEXTO_SECUNDARIO,
            font=(cfg.FAMILIA_FONTE, 11),
        ).pack(anchor="w")

        # Grid com os cards de exportação.
        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.pack(fill="x", pady=(0, 14))
        grid.grid_columnconfigure(0, weight=1, uniform="rel")
        grid.grid_columnconfigure(1, weight=1, uniform="rel")

        self._card_export(
            grid,
            coluna=0,
            icone="⤓",
            titulo="Exportar CSV",
            descricao=(
                "Arquivo tabular para Excel, Google Sheets ou ferramentas "
                "de BI. Inclui senha, nome, serviço, prioridade, horários "
                "e tempo de espera."
            ),
            cor=cfg.COR_SUCESSO,
            callback=self._exportar_csv,
        )

        self._card_export(
            grid,
            coluna=1,
            icone="≡",
            titulo="Exportar TXT",
            descricao=(
                "Relatório executivo em texto puro, com resumo do dia, "
                "indicadores agregados e histórico detalhado de "
                "atendimentos."
            ),
            cor=cfg.COR_PRIMARIA,
            callback=self._exportar_txt,
        )

        # Feedback de operação.
        self.label_feedback = ctk.CTkLabel(
            self,
            text="",
            text_color=cfg.COR_TEXTO_SECUNDARIO,
            font=(cfg.FAMILIA_FONTE, 11),
        )
        self.label_feedback.pack(anchor="w", pady=(8, 0))

    def _card_export(
        self,
        parent,
        coluna: int,
        icone: str,
        titulo: str,
        descricao: str,
        cor: str,
        callback,
    ) -> None:
        card = ctk.CTkFrame(
            parent,
            fg_color=cfg.COR_CARD,
            corner_radius=12,
            border_width=1,
            border_color=cfg.COR_BORDA,
        )
        card.grid(row=0, column=coluna, sticky="nsew", padx=6, pady=6)

        ctk.CTkLabel(
            card,
            text=icone,
            text_color=cor,
            font=(cfg.FAMILIA_FONTE, 36, "bold"),
        ).pack(anchor="w", padx=24, pady=(22, 0))

        ctk.CTkLabel(
            card,
            text=titulo,
            text_color=cfg.COR_TEXTO,
            font=(cfg.FAMILIA_FONTE, 18, "bold"),
        ).pack(anchor="w", padx=24, pady=(8, 4))

        ctk.CTkLabel(
            card,
            text=descricao,
            text_color=cfg.COR_TEXTO_SECUNDARIO,
            font=(cfg.FAMILIA_FONTE, 11),
            wraplength=320,
            justify="left",
        ).pack(anchor="w", padx=24, pady=(0, 16))

        ctk.CTkButton(
            card,
            text="Exportar",
            fg_color=cor,
            hover_color=cfg.COR_PRIMARIA_HOVER if cor == cfg.COR_PRIMARIA else cfg.COR_SUCESSO_HOVER,
            text_color="white",
            corner_radius=6,
            height=36,
            font=(cfg.FAMILIA_FONTE, 11, "bold"),
            command=callback,
        ).pack(anchor="w", padx=24, pady=(0, 22))

    # ------------------------------------------------------------------
    # Ações
    # ------------------------------------------------------------------
    def _nome_sugerido(self, extensao: str) -> str:
        carimbo = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"sga_relatorio_{carimbo}.{extensao}"

    def _validar_historico(self) -> bool:
        if not self.main_window.fila_service.historico:
            self._feedback(
                "Nenhum atendimento concluído para exportar.",
                erro=True,
            )
            return False
        return True

    def _feedback(self, mensagem: str, erro: bool = False) -> None:
        cor = cfg.COR_ERRO if erro else cfg.COR_SUCESSO
        self.label_feedback.configure(text=mensagem, text_color=cor)

    def _exportar_csv(self) -> None:
        if not self._validar_historico():
            return

        caminho = filedialog.asksaveasfilename(
            title="Salvar relatório CSV",
            defaultextension=".csv",
            initialfile=self._nome_sugerido("csv"),
            filetypes=[("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*")],
        )
        if not caminho:
            return

        sucesso = exportar_csv(self.main_window.fila_service.historico, caminho)
        if sucesso:
            self._feedback(f"CSV salvo com sucesso: {caminho}")
        else:
            self._feedback("Falha ao salvar o CSV.", erro=True)

    def _exportar_txt(self) -> None:
        if not self._validar_historico():
            return

        caminho = filedialog.asksaveasfilename(
            title="Salvar relatório TXT",
            defaultextension=".txt",
            initialfile=self._nome_sugerido("txt"),
            filetypes=[("Arquivos TXT", "*.txt"), ("Todos os arquivos", "*.*")],
        )
        if not caminho:
            return

        fs = self.main_window.fila_service
        sucesso = exportar_txt(fs.historico, list(fs.fila), caminho)
        if sucesso:
            self._feedback(f"TXT salvo com sucesso: {caminho}")
        else:
            self._feedback("Falha ao salvar o TXT.", erro=True)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    def on_show(self) -> None:
        self.label_feedback.configure(text="")

    def on_data_changed(self) -> None:
        pass

    def on_tick(self) -> None:
        pass

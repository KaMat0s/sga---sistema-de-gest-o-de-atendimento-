"""View da fila — cadastro de clientes, busca, listagem e ações."""

from tkinter import messagebox

import customtkinter as ctk

from ui.components import PrioridadeBadge
from utils import constants as cfg
from utils.helpers import bind_recursivo


class FilaView(ctk.CTkFrame):
    """View principal de operação: cadastra e atende clientes."""

    OPCOES_PRIORIDADE = [
        ("normal", "Normal", cfg.COR_NORMAL),
        ("idoso", "Idoso", cfg.COR_PRIORITARIO),
        ("gestante", "Gestante", cfg.COR_PRIORITARIO),
        ("emergencia", "Emergência", cfg.COR_EMERGENCIA),
    ]

    def __init__(self, master, main_window):
        super().__init__(master, fg_color="transparent")
        self.main_window = main_window
        self.selecionado = None
        self.linhas: list = []
        self._construir()

    # ------------------------------------------------------------------
    # Construção
    # ------------------------------------------------------------------
    def _construir(self) -> None:
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=2, uniform="painel")
        self.grid_columnconfigure(1, weight=3, uniform="painel")

        painel_esq = ctk.CTkFrame(
            self,
            fg_color=cfg.COR_CARD,
            corner_radius=12,
            border_width=1,
            border_color=cfg.COR_BORDA,
        )
        painel_esq.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self._construir_cadastro(painel_esq)

        painel_dir = ctk.CTkFrame(
            self,
            fg_color=cfg.COR_CARD,
            corner_radius=12,
            border_width=1,
            border_color=cfg.COR_BORDA,
        )
        painel_dir.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        self._construir_lista(painel_dir)

    def _construir_cadastro(self, parent) -> None:
        ctk.CTkLabel(
            parent,
            text="Cadastrar cliente",
            text_color=cfg.COR_TEXTO,
            font=(cfg.FAMILIA_FONTE, 16, "bold"),
        ).pack(anchor="w", padx=24, pady=(20, 4))
        ctk.CTkLabel(
            parent,
            text="Preencha os dados para gerar a senha.",
            text_color=cfg.COR_TEXTO_SECUNDARIO,
            font=(cfg.FAMILIA_FONTE, 10),
        ).pack(anchor="w", padx=24, pady=(0, 16))

        # Nome
        ctk.CTkLabel(
            parent, text="NOME DO CLIENTE",
            text_color=cfg.COR_TEXTO_SECUNDARIO, font=cfg.FONTE_LABEL,
        ).pack(anchor="w", padx=24)
        self.entrada_nome = ctk.CTkEntry(
            parent, height=40, font=cfg.FONTE_TEXTO,
            fg_color=cfg.COR_FUNDO_CLARO, border_color=cfg.COR_BORDA,
        )
        self.entrada_nome.pack(fill="x", padx=24, pady=(4, 14))
        self.entrada_nome.bind("<Return>", lambda _: self._adicionar())

        # Serviço
        ctk.CTkLabel(
            parent, text="SERVIÇO",
            text_color=cfg.COR_TEXTO_SECUNDARIO, font=cfg.FONTE_LABEL,
        ).pack(anchor="w", padx=24)
        self.combo_servico = ctk.CTkComboBox(
            parent,
            values=cfg.SERVICOS,
            height=40,
            font=cfg.FONTE_TEXTO,
            fg_color=cfg.COR_FUNDO_CLARO,
            border_color=cfg.COR_BORDA,
            button_color=cfg.COR_PRIMARIA,
            button_hover_color=cfg.COR_PRIMARIA_HOVER,
            dropdown_fg_color=cfg.COR_CARD,
            state="readonly",
        )
        self.combo_servico.set(cfg.SERVICOS[0])
        self.combo_servico.pack(fill="x", padx=24, pady=(4, 14))

        # Prioridade
        ctk.CTkLabel(
            parent, text="PRIORIDADE",
            text_color=cfg.COR_TEXTO_SECUNDARIO, font=cfg.FONTE_LABEL,
        ).pack(anchor="w", padx=24)

        self.var_prioridade = ctk.StringVar(value="normal")
        radios = ctk.CTkFrame(parent, fg_color="transparent")
        radios.pack(fill="x", padx=24, pady=(6, 20))
        for valor, label, cor in self.OPCOES_PRIORIDADE:
            ctk.CTkRadioButton(
                radios,
                text=label,
                variable=self.var_prioridade,
                value=valor,
                text_color=cfg.COR_TEXTO,
                fg_color=cor,
                hover_color=cor,
                border_color=cfg.COR_BORDA,
                font=(cfg.FAMILIA_FONTE, 11),
            ).pack(anchor="w", pady=3)

        ctk.CTkButton(
            parent,
            text="ADICIONAR À FILA",
            height=44,
            font=cfg.FONTE_TEXTO_BOLD,
            fg_color=cfg.COR_PRIMARIA,
            hover_color=cfg.COR_PRIMARIA_HOVER,
            command=self._adicionar,
        ).pack(fill="x", padx=24, pady=(0, 14))

        self.label_feedback = ctk.CTkLabel(
            parent,
            text="",
            text_color=cfg.COR_SUCESSO,
            font=(cfg.FAMILIA_FONTE, 11, "bold"),
            anchor="w",
        )
        self.label_feedback.pack(fill="x", padx=24, pady=(0, 20))

    def _construir_lista(self, parent) -> None:
        cabec = ctk.CTkFrame(parent, fg_color="transparent")
        cabec.pack(fill="x", padx=20, pady=(20, 10))

        topo = ctk.CTkFrame(cabec, fg_color="transparent")
        topo.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            topo, text="Fila atual",
            text_color=cfg.COR_TEXTO, font=(cfg.FAMILIA_FONTE, 16, "bold"),
        ).pack(side="left")

        self.label_total = ctk.CTkLabel(
            topo, text="0 cliente(s)",
            text_color=cfg.COR_TEXTO_SECUNDARIO, font=(cfg.FAMILIA_FONTE, 11),
        )
        self.label_total.pack(side="right")

        # Busca
        self.entrada_busca = ctk.CTkEntry(
            cabec,
            placeholder_text="Buscar por nome ou senha...",
            height=38,
            font=(cfg.FAMILIA_FONTE, 11),
            fg_color=cfg.COR_FUNDO_CLARO,
            border_color=cfg.COR_BORDA,
        )
        self.entrada_busca.pack(fill="x", pady=(0, 10))
        self.entrada_busca.bind("<KeyRelease>", lambda _: self._renderizar_lista())

        # Botões de ação
        botoes = ctk.CTkFrame(cabec, fg_color="transparent")
        botoes.pack(fill="x")
        ctk.CTkButton(
            botoes,
            text="▶  Chamar Próximo",
            height=40,
            font=cfg.FONTE_TEXTO_BOLD,
            fg_color=cfg.COR_SUCESSO,
            hover_color=cfg.COR_SUCESSO_HOVER,
            command=self._chamar_proximo,
        ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            botoes,
            text="✕  Cancelar Selecionado",
            height=40,
            font=cfg.FONTE_TEXTO_BOLD,
            fg_color=cfg.COR_ERRO,
            hover_color=cfg.COR_ERRO_HOVER,
            command=self._cancelar_selecionado,
        ).pack(side="left")

        # Lista rolável
        self.lista_frame = ctk.CTkScrollableFrame(
            parent, fg_color=cfg.COR_FUNDO_CLARO, corner_radius=8,
        )
        self.lista_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    # ------------------------------------------------------------------
    # Ações
    # ------------------------------------------------------------------
    def _adicionar(self) -> None:
        nome = self.entrada_nome.get()
        servico = self.combo_servico.get()
        prioridade = self.var_prioridade.get()

        try:
            cliente = self.main_window.fila_service.adicionar(
                nome, servico, prioridade
            )
        except ValueError as erro:
            messagebox.showwarning("Atenção", str(erro))
            return

        self.entrada_nome.delete(0, "end")
        self.entrada_nome.focus()
        self.var_prioridade.set("normal")

        self.label_feedback.configure(
            text=f"✓  {cliente.nome} adicionado  •  Senha: {cliente.senha}",
            text_color=cfg.COR_SUCESSO,
        )
        self.main_window.notificar_mudanca()

    def _chamar_proximo(self) -> None:
        fs = self.main_window.fila_service
        if fs.tamanho() == 0:
            messagebox.showinfo("Fila vazia", "Não há clientes aguardando.")
            return

        cliente = fs.chamar_proximo()
        self.main_window.notificar_mudanca()

        mensagem = (
            f"Senha:       {cliente.senha}\n"
            f"Nome:        {cliente.nome}\n"
            f"Serviço:     {cliente.servico}\n"
            f"Prioridade:  {cliente.prioridade.title()}\n"
            f"Tempo de espera: {cliente.tempo_espera():.1f} min"
        )
        messagebox.showinfo("Próximo cliente", mensagem)

    def _cancelar_selecionado(self) -> None:
        if self.selecionado is None:
            messagebox.showinfo(
                "Aviso", "Selecione um cliente na lista primeiro."
            )
            return

        cliente = self.selecionado
        confirma = messagebox.askyesno(
            "Cancelar atendimento",
            f"Cancelar atendimento de {cliente.nome} (senha {cliente.senha})?",
        )
        if not confirma:
            return

        self.main_window.fila_service.remover_por_senha(cliente.senha)
        self.selecionado = None
        self.label_feedback.configure(
            text=f"✕  {cliente.nome} removido da fila",
            text_color=cfg.COR_AVISO,
        )
        self.main_window.notificar_mudanca()

    def _selecionar(self, cliente, linha) -> None:
        """Marca a linha clicada como selecionada (destaque visual)."""
        for ln, _ in self.linhas:
            ln.configure(fg_color=cfg.COR_CARD)
        linha.configure(fg_color=cfg.COR_CARD_HOVER)
        self.selecionado = cliente

    # ------------------------------------------------------------------
    # Renderização da lista
    # ------------------------------------------------------------------
    def _renderizar_lista(self) -> None:
        for w in self.lista_frame.winfo_children():
            w.destroy()
        self.linhas = []

        fs = self.main_window.fila_service
        termo = self.entrada_busca.get()
        visiveis = fs.buscar(termo)
        self.label_total.configure(text=f"{len(visiveis)} cliente(s)")

        if not visiveis:
            mensagem = (
                f"Nenhum resultado para '{termo}'"
                if termo
                else "Nenhum cliente aguardando."
            )
            ctk.CTkLabel(
                self.lista_frame,
                text=mensagem,
                text_color=cfg.COR_TEXTO_SECUNDARIO,
                font=(cfg.FAMILIA_FONTE, 11),
            ).pack(pady=40)
            return

        fila_real = list(fs.fila)
        for cliente in visiveis:
            posicao = fila_real.index(cliente) + 1
            self._criar_linha(cliente, posicao)

    def _criar_linha(self, cliente, posicao: int) -> None:
        cores_lateral = {
            "emergencia": cfg.COR_EMERGENCIA,
            "idoso": cfg.COR_PRIORITARIO,
            "gestante": cfg.COR_PRIORITARIO,
            "normal": cfg.COR_NORMAL,
        }
        cor_lateral = cores_lateral[cliente.prioridade]

        linha = ctk.CTkFrame(
            self.lista_frame,
            fg_color=cfg.COR_CARD,
            corner_radius=8,
            height=66,
        )
        linha.pack(fill="x", pady=4, padx=4)
        linha.pack_propagate(False)

        # Barra lateral colorida
        ctk.CTkFrame(linha, fg_color=cor_lateral, width=4, corner_radius=2).pack(
            side="left", fill="y", padx=(8, 0), pady=8
        )

        # Posição
        ctk.CTkLabel(
            linha,
            text=f"{posicao}º",
            text_color=cfg.COR_TEXTO_SECUNDARIO,
            font=(cfg.FAMILIA_FONTE, 14, "bold"),
            width=40,
        ).pack(side="left", padx=(10, 6))

        # Senha
        ctk.CTkLabel(
            linha,
            text=cliente.senha,
            text_color=cfg.COR_PRIMARIA,
            font=cfg.FONTE_MONO_MEDIA,
            width=70,
        ).pack(side="left", padx=6)

        # Informações
        info = ctk.CTkFrame(linha, fg_color="transparent")
        info.pack(side="left", fill="both", expand=True, padx=10, pady=6)
        ctk.CTkLabel(
            info,
            text=cliente.nome,
            text_color=cfg.COR_TEXTO,
            font=(cfg.FAMILIA_FONTE, 12, "bold"),
            anchor="w",
        ).pack(fill="x")

        chegada = cliente.horario_chegada.strftime("%H:%M")
        ctk.CTkLabel(
            info,
            text=(
                f"{cliente.servico}  •  chegou às {chegada}  •  "
                f"aguardando há {cliente.tempo_espera():.0f} min"
            ),
            text_color=cfg.COR_TEXTO_SECUNDARIO,
            font=(cfg.FAMILIA_FONTE, 10),
            anchor="w",
        ).pack(fill="x")

        # Badge de prioridade
        PrioridadeBadge(linha, cliente.prioridade).pack(side="right", padx=14)

        # Vínculo de clique
        def selecionar(_=None, c=cliente, ln=linha):
            self._selecionar(c, ln)

        bind_recursivo(linha, "<Button-1>", selecionar)
        self.linhas.append((linha, cliente))

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    def on_show(self) -> None:
        self._renderizar_lista()

    def on_data_changed(self) -> None:
        self.selecionado = None
        self._renderizar_lista()

    def on_tick(self) -> None:
        if self.main_window.view_atual == "fila":
            self._renderizar_lista()

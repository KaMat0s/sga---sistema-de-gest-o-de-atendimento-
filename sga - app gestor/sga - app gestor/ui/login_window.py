"""Tela de login do SGA."""

from tkinter import messagebox

import customtkinter as ctk

from utils import constants as cfg


class LoginWindow(ctk.CTk):
    """Janela de autenticação anterior ao app principal."""

    def __init__(self):
        super().__init__()
        self.title(f"{cfg.APP_NOME} — Login")
        self.geometry("420x560")
        self.resizable(False, False)
        self.configure(fg_color=cfg.COR_FUNDO)

        self.autenticado: bool = False
        self.usuario_logado: str = ""

        self._construir_ui()
        self._centralizar()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------
    def _centralizar(self) -> None:
        """Centraliza a janela na tela do usuário."""
        self.update_idletasks()
        largura = self.winfo_width()
        altura = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (largura // 2)
        y = (self.winfo_screenheight() // 2) - (altura // 2)
        self.geometry(f"{largura}x{altura}+{x}+{y}")

    def _construir_ui(self) -> None:
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=40, pady=40)

        # Logo
        ctk.CTkLabel(
            container,
            text="◆",
            text_color=cfg.COR_PRIMARIA,
            font=(cfg.FAMILIA_FONTE, 56, "bold"),
        ).pack(pady=(10, 0))

        ctk.CTkLabel(
            container,
            text=cfg.APP_NOME,
            text_color=cfg.COR_TEXTO,
            font=(cfg.FAMILIA_FONTE, 32, "bold"),
        ).pack(pady=(4, 0))

        ctk.CTkLabel(
            container,
            text=cfg.APP_SUBTITULO,
            text_color=cfg.COR_TEXTO_SECUNDARIO,
            font=(cfg.FAMILIA_FONTE, 11),
        ).pack(pady=(0, 28))

        # Campos
        ctk.CTkLabel(
            container,
            text="USUÁRIO",
            text_color=cfg.COR_TEXTO_SECUNDARIO,
            font=cfg.FONTE_LABEL,
            anchor="w",
        ).pack(fill="x")
        self.entrada_usuario = ctk.CTkEntry(
            container,
            height=42,
            font=cfg.FONTE_TEXTO,
            fg_color=cfg.COR_CARD,
            border_color=cfg.COR_BORDA,
        )
        self.entrada_usuario.pack(fill="x", pady=(4, 14))

        ctk.CTkLabel(
            container,
            text="SENHA",
            text_color=cfg.COR_TEXTO_SECUNDARIO,
            font=cfg.FONTE_LABEL,
            anchor="w",
        ).pack(fill="x")
        self.entrada_senha = ctk.CTkEntry(
            container,
            height=42,
            show="●",
            font=cfg.FONTE_TEXTO,
            fg_color=cfg.COR_CARD,
            border_color=cfg.COR_BORDA,
        )
        self.entrada_senha.pack(fill="x", pady=(4, 22))
        self.entrada_senha.bind("<Return>", lambda _: self._validar())
        self.entrada_usuario.bind("<Return>", lambda _: self.entrada_senha.focus())

        ctk.CTkButton(
            container,
            text="ENTRAR",
            height=44,
            font=cfg.FONTE_TEXTO_BOLD,
            fg_color=cfg.COR_PRIMARIA,
            hover_color=cfg.COR_PRIMARIA_HOVER,
            command=self._validar,
        ).pack(fill="x")

        ctk.CTkLabel(
            container,
            text="Demo: admin / admin123",
            text_color=cfg.COR_TEXTO_FRACO,
            font=(cfg.FAMILIA_FONTE, 9),
        ).pack(pady=(14, 0))

        # Rodapé
        ctk.CTkLabel(
            container,
            text=f"v{cfg.APP_VERSAO}  •  {cfg.APP_EMPRESA}",
            text_color=cfg.COR_TEXTO_FRACO,
            font=(cfg.FAMILIA_FONTE, 9),
        ).pack(side="bottom", pady=(20, 0))

        self.entrada_usuario.focus()

    # ------------------------------------------------------------------
    # Lógica
    # ------------------------------------------------------------------
    def _validar(self) -> None:
        """Valida credenciais contra `USUARIOS_DEMO` e fecha a janela em sucesso."""
        usuario = self.entrada_usuario.get().strip().lower()
        senha = self.entrada_senha.get()

        if cfg.USUARIOS_DEMO.get(usuario) == senha:
            self.autenticado = True
            self.usuario_logado = usuario
            self.destroy()
        else:
            messagebox.showerror(
                "Acesso negado",
                "Usuário ou senha inválidos.\n\nUse as credenciais demo:\nadmin / admin123",
            )
            self.entrada_senha.delete(0, "end")
            self.entrada_senha.focus()

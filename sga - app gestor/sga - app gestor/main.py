"""Ponto de entrada do SGA — Sistema de Gestão de Atendimento.

Fluxo:
    1. Configura o tema dark global do CustomTkinter.
    2. Exibe a tela de login.
    3. Se autenticado, abre a janela principal (MainWindow) com o usuário.
    4. Encerra graciosamente ao fechar.

Uso:
    $ python main.py
"""

import sys

import customtkinter as ctk

from ui.login_window import LoginWindow
from ui.main_window import MainWindow
from utils import constants as cfg


def configurar_aparencia() -> None:
    """Define o tema global do CustomTkinter."""
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")


def main() -> int:
    configurar_aparencia()

    # Login.
    login = LoginWindow()
    login.mainloop()

    if not getattr(login, "autenticado", False):
        # Usuário fechou a janela de login sem se autenticar.
        return 0

    usuario = login.usuario_logado

    # Janela principal.
    app = MainWindow(usuario=usuario)
    app.mainloop()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{cfg.APP_NOME} encerrado pelo usuário.")
        sys.exit(0)

"""Funções auxiliares de formatação e UI."""

from datetime import datetime
from typing import Optional


def formatar_hora(dt: Optional[datetime]) -> str:
    """Formata datetime como `HH:MM` ou retorna `—` se None."""
    return dt.strftime("%H:%M") if dt else "—"


def formatar_data_hora(dt: Optional[datetime]) -> str:
    """Formata datetime como `dd/mm/aaaa HH:MM:SS` ou retorna `—` se None."""
    return dt.strftime("%d/%m/%Y %H:%M:%S") if dt else "—"


def formatar_minutos(valor: float) -> str:
    """Formata valor numérico em minutos com 1 casa decimal."""
    return f"{valor:.1f} min"


def label_prioridade(prioridade: str) -> str:
    """Retorna o rótulo de exibição para uma prioridade."""
    mapa = {
        "emergencia": "EMERGÊNCIA",
        "idoso": "IDOSO",
        "gestante": "GESTANTE",
        "normal": "NORMAL",
    }
    return mapa.get(prioridade, "NORMAL")


def bind_recursivo(widget, evento: str, callback) -> None:
    """Aplica `bind(evento, callback)` no widget e em todos seus descendentes.

    Útil para capturar cliques em estruturas compostas (frame com vários
    labels filhos), já que o tkinter não propaga eventos automaticamente.
    """
    widget.bind(evento, callback)
    try:
        for filho in widget.winfo_children():
            bind_recursivo(filho, evento, callback)
    except AttributeError:
        pass

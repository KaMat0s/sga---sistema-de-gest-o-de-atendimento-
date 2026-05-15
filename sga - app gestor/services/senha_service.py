"""Geração incremental de senhas únicas por categoria de prioridade.

Substitui o esquema antigo (números aleatórios sujeitos a colisão) por
contadores monotônicos persistidos no JSON. Garante unicidade absoluta e
sequência previsível por prefixo:

- N001, N002, ... para clientes normais
- P001, P002, ... para idosos e gestantes (prioritários)
- E001, E002, ... para emergências
"""

from typing import Optional


class GeradorSenhas:
    """Mantém contadores incrementais para emissão de senhas únicas."""

    PREFIXOS = {
        "normal": "N",
        "idoso": "P",
        "gestante": "P",
        "emergencia": "E",
    }

    def __init__(self, contadores: Optional[dict] = None) -> None:
        # Cada prefixo armazena o último número emitido.
        self.contadores: dict = contadores or {"N": 0, "P": 0, "E": 0}
        # Garante que todos os prefixos esperados existam, mesmo em JSONs antigos.
        for prefixo in ("N", "P", "E"):
            self.contadores.setdefault(prefixo, 0)

    def proxima_senha(self, prioridade: str) -> str:
        """Gera e retorna a próxima senha para a prioridade informada."""
        prefixo = self.PREFIXOS.get(prioridade, "N")
        self.contadores[prefixo] += 1
        numero = str(self.contadores[prefixo]).zfill(3)
        return f"{prefixo}{numero}"

    def to_dict(self) -> dict:
        """Serializa os contadores para persistência."""
        return dict(self.contadores)

    @classmethod
    def from_dict(cls, dados: Optional[dict]) -> "GeradorSenhas":
        """Reconstrói o gerador a partir do JSON, ou cria um novo se vazio."""
        return cls(contadores=dados or None)

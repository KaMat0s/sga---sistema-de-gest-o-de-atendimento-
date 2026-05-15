"""Modelo de domínio do cliente em atendimento.

Representa um cliente que entrou na fila do SGA. Encapsula seus dados pessoais,
informações temporais (chegada e atendimento) e a prioridade que define sua
posição relativa na fila prioritária.
"""

from datetime import datetime
from typing import Optional


class Cliente:
    """Cliente que aguarda ou já foi atendido pelo sistema.

    Atributos:
        nome: Nome completo, normalizado em Title Case.
        servico: Serviço solicitado.
        prioridade: Categoria da prioridade ("normal", "idoso", "gestante", "emergencia").
        senha: Identificador único gerado pelo `GeradorSenhas`.
        horario_chegada: Momento em que o cliente entrou na fila.
        horario_atendimento: Momento em que foi chamado para atendimento (None se aguardando).
        atendido: Flag indicando se o atendimento já foi iniciado.
    """

    PESOS_PRIORIDADE = {
        "normal": 0,
        "idoso": 1,
        "gestante": 1,
        "emergencia": 2,
    }

    def __init__(
        self,
        nome: str,
        servico: str,
        prioridade: str = "normal",
        senha: Optional[str] = None,
    ) -> None:
        if prioridade not in self.PESOS_PRIORIDADE:
            prioridade = "normal"

        self.nome: str = nome.strip().title()
        self.servico: str = servico.strip()
        self.prioridade: str = prioridade
        self.senha: str = senha or ""
        self.horario_chegada: datetime = datetime.now()
        self.horario_atendimento: Optional[datetime] = None
        self.atendido: bool = False

    @property
    def peso(self) -> int:
        """Peso numérico da prioridade (maior peso = mais à frente na fila)."""
        return self.PESOS_PRIORIDADE[self.prioridade]

    def tempo_espera(self) -> float:
        """Retorna o tempo de espera em minutos.

        Se o cliente já foi atendido, conta do horário de chegada até o horário
        de atendimento. Caso contrário, conta até o momento atual.
        """
        fim = self.horario_atendimento or datetime.now()
        return (fim - self.horario_chegada).total_seconds() / 60

    def marcar_atendido(self) -> None:
        """Registra o cliente como atendido no momento atual."""
        self.horario_atendimento = datetime.now()
        self.atendido = True

    def to_dict(self) -> dict:
        """Serializa o cliente em dicionário compatível com JSON."""
        return {
            "senha": self.senha,
            "nome": self.nome,
            "servico": self.servico,
            "prioridade": self.prioridade,
            "horario_chegada": self.horario_chegada.isoformat(),
            "horario_atendimento": (
                self.horario_atendimento.isoformat()
                if self.horario_atendimento
                else None
            ),
            "atendido": self.atendido,
        }

    @classmethod
    def from_dict(cls, dados: dict) -> "Cliente":
        """Reconstrói um cliente a partir de um dicionário carregado do JSON."""
        cliente = cls(
            nome=dados["nome"],
            servico=dados["servico"],
            prioridade=dados.get("prioridade", "normal"),
            senha=dados["senha"],
        )
        cliente.horario_chegada = datetime.fromisoformat(dados["horario_chegada"])
        if dados.get("horario_atendimento"):
            cliente.horario_atendimento = datetime.fromisoformat(
                dados["horario_atendimento"]
            )
        cliente.atendido = dados.get("atendido", False)
        return cliente

    def __repr__(self) -> str:
        return (
            f"Cliente(senha={self.senha!r}, nome={self.nome!r}, "
            f"prioridade={self.prioridade!r})"
        )

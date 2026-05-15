"""Operações sobre a fila prioritária de clientes.

Encapsula a estrutura `collections.deque` (FIFO O(1)) e estende seu
comportamento para suportar três níveis de prioridade. A regra: clientes
prioritários (peso maior) são inseridos antes do primeiro cliente com peso
menor, preservando o FIFO dentro de cada faixa.
"""

from collections import deque
from typing import Optional

from models.cliente import Cliente
from services.senha_service import GeradorSenhas


class FilaAtendimento:
    """Fila prioritária de clientes com histórico de atendimentos."""

    def __init__(
        self,
        fila: Optional[deque] = None,
        historico: Optional[list] = None,
        gerador: Optional[GeradorSenhas] = None,
    ) -> None:
        self.fila: deque = fila if fila is not None else deque()
        self.historico: list = historico if historico is not None else []
        self.gerador: GeradorSenhas = gerador or GeradorSenhas()

    # ------------------------------------------------------------------
    # Operações públicas
    # ------------------------------------------------------------------
    def adicionar(
        self, nome: str, servico: str, prioridade: str = "normal"
    ) -> Cliente:
        """Adiciona um cliente respeitando a regra de prioridade.

        Levanta `ValueError` se nome ou serviço estiverem vazios, ou se a
        prioridade for inválida.
        """
        if not nome or not nome.strip():
            raise ValueError("O nome do cliente é obrigatório.")
        if not servico or not servico.strip():
            raise ValueError("O serviço é obrigatório.")
        if prioridade not in Cliente.PESOS_PRIORIDADE:
            raise ValueError(f"Prioridade inválida: {prioridade}")

        senha = self.gerador.proxima_senha(prioridade)
        cliente = Cliente(
            nome=nome, servico=servico, prioridade=prioridade, senha=senha
        )
        self._inserir_por_prioridade(cliente)
        return cliente

    def chamar_proximo(self) -> Optional[Cliente]:
        """Remove e retorna o primeiro da fila, registrando o atendimento.

        Usa `deque.popleft()` que é O(1) — diferentemente de `list.pop(0)`,
        que seria O(n) por exigir o deslocamento de todos os elementos.
        """
        if not self.fila:
            return None
        cliente = self.fila.popleft()
        cliente.marcar_atendido()
        self.historico.append(cliente)
        return cliente

    def buscar(self, termo: str) -> list:
        """Retorna clientes na fila que contêm o termo no nome ou na senha."""
        termo = (termo or "").strip().lower()
        if termo == "":
            return list(self.fila)
        return [
            c
            for c in self.fila
            if termo in c.nome.lower() or termo in c.senha.lower()
        ]

    def remover_por_senha(self, senha: str) -> Optional[Cliente]:
        """Remove o cliente com a senha informada, retornando-o (ou None)."""
        i = 0
        while i < len(self.fila):
            if self.fila[i].senha == senha:
                cliente = self.fila[i]
                del self.fila[i]
                return cliente
            i += 1
        return None

    def tamanho(self) -> int:
        """Retorna o número de clientes aguardando."""
        return len(self.fila)

    def proximo(self) -> Optional[Cliente]:
        """Retorna o cliente que será chamado a seguir (sem removê-lo)."""
        return self.fila[0] if self.fila else None

    # ------------------------------------------------------------------
    # Lógica interna
    # ------------------------------------------------------------------
    def _inserir_por_prioridade(self, cliente: Cliente) -> None:
        """Insere o cliente na posição correta segundo seu peso de prioridade."""
        if cliente.peso == 0:
            self.fila.append(cliente)
            return

        # Procura o primeiro cliente com peso menor para inserir antes dele.
        for i, em_fila in enumerate(self.fila):
            if em_fila.peso < cliente.peso:
                self.fila.insert(i, cliente)
                return

        # Não existe ninguém de prioridade menor: vai para o fim.
        self.fila.append(cliente)

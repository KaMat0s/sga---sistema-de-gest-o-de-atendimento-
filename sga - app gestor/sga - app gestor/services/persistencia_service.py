"""Persistência em JSON da fila, do histórico e dos contadores de senha."""

import json
import os
from collections import deque

from models.cliente import Cliente
from services.fila_service import FilaAtendimento
from services.senha_service import GeradorSenhas


ARQUIVO_PADRAO = os.path.join("data", "sga_dados.json")


def _garantir_diretorio(caminho: str) -> None:
    """Cria o diretório do arquivo se ele não existir."""
    diretorio = os.path.dirname(caminho)
    if diretorio and not os.path.exists(diretorio):
        os.makedirs(diretorio, exist_ok=True)


def salvar(fila_service: FilaAtendimento, arquivo: str = ARQUIVO_PADRAO) -> bool:
    """Persiste fila, histórico e contadores no arquivo JSON.

    Retorna True em sucesso, False em falha de I/O. A aplicação continua
    funcionando mesmo quando o salvamento falha (apenas os dados não persistem).
    """
    _garantir_diretorio(arquivo)
    dados = {
        "fila": [c.to_dict() for c in fila_service.fila],
        "historico": [c.to_dict() for c in fila_service.historico],
        "contadores": fila_service.gerador.to_dict(),
    }
    try:
        with open(arquivo, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
        return True
    except (IOError, OSError) as erro:
        print(f"[Persistência] Falha ao salvar dados: {erro}")
        return False


def carregar(arquivo: str = ARQUIVO_PADRAO) -> FilaAtendimento:
    """Lê o JSON e reconstrói o estado da aplicação.

    Caso o arquivo não exista ou esteja corrompido, retorna uma fila vazia
    (estado inicial), sem propagar exceções.
    """
    if not os.path.exists(arquivo):
        return FilaAtendimento()

    try:
        with open(arquivo, "r", encoding="utf-8") as f:
            dados = json.load(f)

        fila = deque(Cliente.from_dict(d) for d in dados.get("fila", []))
        historico = [Cliente.from_dict(d) for d in dados.get("historico", [])]
        gerador = GeradorSenhas.from_dict(dados.get("contadores"))

        return FilaAtendimento(fila=fila, historico=historico, gerador=gerador)
    except (json.JSONDecodeError, KeyError, ValueError) as erro:
        print(f"[Persistência] Arquivo corrompido — iniciando do zero: {erro}")
        return FilaAtendimento()

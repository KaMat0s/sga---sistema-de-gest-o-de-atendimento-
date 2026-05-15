"""Exportação de relatórios em CSV e TXT."""

import csv
import os
from datetime import datetime
from typing import List

from models.cliente import Cliente
from services.estatisticas_service import estatisticas_completas


def _garantir_diretorio(caminho: str) -> None:
    """Cria o diretório do arquivo se ele não existir."""
    diretorio = os.path.dirname(caminho)
    if diretorio and not os.path.exists(diretorio):
        os.makedirs(diretorio, exist_ok=True)


def exportar_csv(historico: List[Cliente], caminho: str) -> bool:
    """Exporta o histórico de atendimentos como CSV (delimitador `;`).

    Retorna True em sucesso, False em falha de I/O.
    """
    try:
        _garantir_diretorio(caminho)
        with open(caminho, "w", encoding="utf-8", newline="") as arquivo:
            writer = csv.writer(arquivo, delimiter=";")
            writer.writerow(
                [
                    "Senha",
                    "Nome",
                    "Servico",
                    "Prioridade",
                    "Chegada",
                    "Atendimento",
                    "Espera (min)",
                ]
            )
            for cliente in historico:
                chegada = cliente.horario_chegada.strftime("%d/%m/%Y %H:%M:%S")
                atendimento = (
                    cliente.horario_atendimento.strftime("%d/%m/%Y %H:%M:%S")
                    if cliente.horario_atendimento
                    else "—"
                )
                writer.writerow(
                    [
                        cliente.senha,
                        cliente.nome,
                        cliente.servico,
                        cliente.prioridade,
                        chegada,
                        atendimento,
                        f"{cliente.tempo_espera():.1f}",
                    ]
                )
        return True
    except (IOError, OSError) as erro:
        print(f"[Export CSV] {erro}")
        return False


def exportar_txt(
    historico: List[Cliente], fila: List[Cliente], caminho: str
) -> bool:
    """Exporta um relatório executivo em texto puro.

    Inclui um resumo com estatísticas, listagem do histórico e contagens
    por serviço e por prioridade. Retorna True em sucesso, False em falha.
    """
    try:
        _garantir_diretorio(caminho)
        stats = estatisticas_completas(historico, fila)
        agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        with open(caminho, "w", encoding="utf-8") as arquivo:
            arquivo.write("=" * 64 + "\n")
            arquivo.write("RELATÓRIO DE ATENDIMENTOS - SGA\n")
            arquivo.write(f"Gerado em: {agora}\n")
            arquivo.write("=" * 64 + "\n\n")

            arquivo.write("RESUMO\n")
            arquivo.write("-" * 64 + "\n")
            arquivo.write(f"Total de atendimentos    : {stats['total_atendidos']}\n")
            arquivo.write(f"Clientes aguardando      : {stats['total_aguardando']}\n")
            arquivo.write(f"Tempo médio de espera    : {stats['tempo_medio']:.1f} min\n")
            arquivo.write(f"Menor espera registrada  : {stats['tempo_min']:.1f} min\n")
            arquivo.write(f"Maior espera registrada  : {stats['tempo_max']:.1f} min\n")
            arquivo.write(f"Tempo total atendido     : {stats['tempo_total']:.0f} min\n")
            arquivo.write(f"Serviço mais procurado   : {stats['servico_top']}\n")
            arquivo.write(
                f"Prioridade mais frequente: {stats['prioridade_top']}\n\n"
            )

            if stats["cliente_maior_espera"]:
                c = stats["cliente_maior_espera"]
                arquivo.write(
                    f"Cliente com maior espera : {c.nome} ({c.senha}) — "
                    f"{c.tempo_espera():.1f} min\n\n"
                )

            arquivo.write("ATENDIMENTOS POR SERVIÇO\n")
            arquivo.write("-" * 64 + "\n")
            for servico, qtd in stats["por_servico"].items():
                arquivo.write(f"  {servico:.<40} {qtd}\n")

            arquivo.write("\nATENDIMENTOS POR PRIORIDADE\n")
            arquivo.write("-" * 64 + "\n")
            for prio, qtd in stats["por_prioridade"].items():
                media = stats["media_por_prioridade"].get(prio, 0)
                arquivo.write(
                    f"  {prio.title():.<30} {qtd:>3} | média: {media:.1f} min\n"
                )

            arquivo.write("\nHISTÓRICO DETALHADO\n")
            arquivo.write("-" * 64 + "\n")
            for c in historico:
                chegada = c.horario_chegada.strftime("%H:%M")
                atendimento = (
                    c.horario_atendimento.strftime("%H:%M")
                    if c.horario_atendimento
                    else "—"
                )
                arquivo.write(
                    f"[{c.senha}] {c.nome} | {c.servico} | "
                    f"{c.prioridade} | chegada {chegada} → "
                    f"atendimento {atendimento} | espera {c.tempo_espera():.1f} min\n"
                )
        return True
    except (IOError, OSError) as erro:
        print(f"[Export TXT] {erro}")
        return False

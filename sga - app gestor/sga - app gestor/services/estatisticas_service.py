"""Cálculo de estatísticas, estimativas e indicadores do dia."""

from collections import Counter
from typing import List, Optional

from models.cliente import Cliente


TEMPO_PADRAO_ESTIMATIVA: float = 5.0  # minutos por atendimento (chute inicial)
JANELA_MOVEL: int = 5                 # nº de atendimentos recentes para a média


def tempo_medio_entre_atendimentos(historico: List[Cliente]) -> float:
    """Calcula a média móvel do intervalo entre atendimentos consecutivos.

    Usa os últimos `JANELA_MOVEL` atendimentos para refletir o ritmo recente.
    Se não há dados suficientes, retorna `TEMPO_PADRAO_ESTIMATIVA`.
    """
    if len(historico) < 2:
        return TEMPO_PADRAO_ESTIMATIVA

    recentes = (
        historico[-JANELA_MOVEL:] if len(historico) > JANELA_MOVEL else historico
    )

    intervalos = []
    for i in range(1, len(recentes)):
        anterior = recentes[i - 1].horario_atendimento
        atual = recentes[i].horario_atendimento
        if anterior and atual:
            intervalos.append((atual - anterior).total_seconds() / 60)

    if not intervalos:
        return TEMPO_PADRAO_ESTIMATIVA
    return sum(intervalos) / len(intervalos)


def estimar_espera(historico: List[Cliente], posicao: int) -> float:
    """Estima a espera para a posição N: posição × tempo médio observado."""
    return posicao * tempo_medio_entre_atendimentos(historico)


def estatisticas_completas(
    historico: List[Cliente], fila: List[Cliente]
) -> dict:
    """Calcula um conjunto completo de indicadores do dia.

    Retorna um dicionário com:
        - total_atendidos, total_aguardando
        - tempo_medio, tempo_min, tempo_max, tempo_total
        - servico_top, prioridade_top
        - cliente_maior_espera (objeto Cliente ou None)
        - por_servico, por_prioridade (dicts contagem)
        - por_hora (dict hora → quantidade)
        - media_por_prioridade (dict prioridade → tempo médio)
    """
    if not historico:
        return {
            "total_atendidos": 0,
            "total_aguardando": len(fila),
            "tempo_medio": 0.0,
            "tempo_min": 0.0,
            "tempo_max": 0.0,
            "tempo_total": 0.0,
            "servico_top": "—",
            "prioridade_top": "—",
            "cliente_maior_espera": None,
            "por_servico": {},
            "por_prioridade": {},
            "por_hora": {},
            "media_por_prioridade": {},
        }

    tempos = [c.tempo_espera() for c in historico]

    contador_servico = Counter(c.servico for c in historico)
    contador_prioridade = Counter(c.prioridade for c in historico)
    contador_hora = Counter(
        c.horario_atendimento.hour
        for c in historico
        if c.horario_atendimento is not None
    )

    cliente_maior_espera = max(historico, key=lambda c: c.tempo_espera())

    media_por_prio = {}
    for prio in set(c.prioridade for c in historico):
        tempos_prio = [c.tempo_espera() for c in historico if c.prioridade == prio]
        media_por_prio[prio] = sum(tempos_prio) / len(tempos_prio)

    return {
        "total_atendidos": len(historico),
        "total_aguardando": len(fila),
        "tempo_medio": sum(tempos) / len(tempos),
        "tempo_min": min(tempos),
        "tempo_max": max(tempos),
        "tempo_total": sum(tempos),
        "servico_top": contador_servico.most_common(1)[0][0],
        "prioridade_top": contador_prioridade.most_common(1)[0][0],
        "cliente_maior_espera": cliente_maior_espera,
        "por_servico": dict(contador_servico),
        "por_prioridade": dict(contador_prioridade),
        "por_hora": dict(sorted(contador_hora.items())),
        "media_por_prioridade": media_por_prio,
    }

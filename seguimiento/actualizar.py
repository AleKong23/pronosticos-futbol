# -*- coding: utf-8 -*-
"""
Marcador de seguimiento: compara las predicciones selladas contra los resultados reales.

Uso:
    python seguimiento/actualizar.py

Lee predicciones.csv y resultados.csv, une por 'tag', calcula metricas fuera de
muestra para el modelo Y para el mercado, y regenera ../seguimiento.html.

La pregunta que responde no es "cuantas acerto" sino "quien predice mejor, el
modelo o el precio de la casa". Por eso toda metrica se calcula dos veces.
"""
import csv, json, math, os
from datetime import datetime

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)


def leer(nombre):
    p = os.path.join(AQUI, nombre)
    if not os.path.exists(p):
        return []
    with open(p, encoding='utf-8') as fh:
        return list(csv.DictReader(fh))


def f(v, d=0.0):
    try:
        return float(v)
    except (TypeError, ValueError):
        return d


def brier(p3, y):
    """Brier multiclase: suma de (prob - resultado)^2 sobre las tres vias."""
    return sum((p3[k] - (1.0 if k == y else 0.0)) ** 2 for k in range(3))


def logloss(p3, y):
    return -math.log(max(p3[y], 1e-9))


IDX = {'1': 0, 'X': 1, '2': 2}


def metricas(filas, pref):
    """pref = 'mod' o 'mkt'. Devuelve None si no hay datos utilizables."""
    usa = [r for r in filas if r['_p_' + pref]]
    if not usa:
        return None
    n = len(usa)
    br = sum(brier(r['_p_' + pref], IDX[r['_res']]) for r in usa) / n
    ll = sum(logloss(r['_p_' + pref], IDX[r['_res']]) for r in usa) / n
    acierto = sum(1 for r in usa
                  if max(range(3), key=lambda k: r['_p_' + pref][k]) == IDX[r['_res']])
    # calibracion: agrupa cada probabilidad emitida por decil y compara con la frecuencia real
    baldes = {}
    for r in usa:
        for k in range(3):
            p = r['_p_' + pref][k]
            b = min(int(p * 10), 9)
            baldes.setdefault(b, [0, 0.0])
            baldes[b][0] += 1
            baldes[b][1] += p
            if IDX[r['_res']] == k:
                baldes[b].append(1)
    cal = []
    for b in sorted(baldes):
        cnt, suma = baldes[b][0], baldes[b][1]
        aciertos = len(baldes[b]) - 2
        cal.append({'rango': '%d-%d%%' % (b * 10, b * 10 + 10), 'n': cnt,
                    'predicho': round(suma / cnt * 100, 1),
                    'observado': round(aciertos / cnt * 100, 1)})
    return {'n': n, 'brier': round(br, 4), 'logloss': round(ll, 4),
            'acierto': acierto, 'acierto_pct': round(acierto / n * 100, 1), 'calibracion': cal}


def main():
    preds = leer('predicciones.csv')
    res = {r['tag']: r for r in leer('resultados.csv')}

    filas = []
    for p in preds:
        r = res.get(p['tag'])
        pm = [f(p['p_modelo_1']) / 100, f(p['p_modelo_X']) / 100, f(p['p_modelo_2']) / 100]
        pk = ([f(p['p_mercado_1']) / 100, f(p['p_mercado_X']) / 100, f(p['p_mercado_2']) / 100]
              if p.get('p_mercado_1') else None)
        fila = dict(p)
        fila['_p_mod'] = pm if r else None
        fila['_p_mkt'] = pk if r else None
        fila['_res'] = r['resultado'] if r else None
        fila['_marcador'] = r['marcador'] if r else None
        fila['_gt'] = (int(r['goles_local']) + int(r['goles_visita'])) if r else None
        filas.append(fila)

    resueltos = [x for x in filas if x['_res']]
    # el subconjunto de oro: predicciones cuyo commit en git precede al saque inicial
    oro = [x for x in resueltos if x.get('sellado_git') == 'si']

    salida = {
        'generado': datetime.now().strftime('%d/%m/%Y %H:%M'),
        'total_predicciones': len(filas),
        'resueltos': len(resueltos),
        'pendientes': len(filas) - len(resueltos),
        'sellados_git': sum(1 for x in filas if x.get('sellado_git') == 'si'),
        'todos': {'modelo': metricas(resueltos, 'mod'), 'mercado': metricas(resueltos, 'mkt')},
        'oro': {'modelo': metricas(oro, 'mod'), 'mercado': metricas(oro, 'mkt')},
        'partidos': [{
            'tag': x['tag'], 'liga': x['liga'], 'fecha': x['fecha_partido'],
            'local': x['local'], 'visita': x['visita'],
            'mod': [f(x['p_modelo_1']), f(x['p_modelo_X']), f(x['p_modelo_2'])],
            'mkt': ([f(x['p_mercado_1']), f(x['p_mercado_X']), f(x['p_mercado_2'])]
                    if x.get('p_mercado_1') else None),
            'conf': int(f(x.get('confianza'), 0)),
            'sellado': x.get('sellado_git', '?'),
            'res': x['_res'], 'marcador': x['_marcador'], 'total_goles': x['_gt'],
            'acerto_mod': (None if not x['_res']
                           else max(range(3), key=lambda k: x['_p_mod'][k]) == IDX[x['_res']]),
            'acerto_mkt': (None if not x['_res'] or not x['_p_mkt']
                           else max(range(3), key=lambda k: x['_p_mkt'][k]) == IDX[x['_res']]),
        } for x in filas],
    }
    with open(os.path.join(AQUI, 'marcador.json'), 'w', encoding='utf-8') as fh:
        json.dump(salida, fh, ensure_ascii=False, indent=1)

    print('predicciones: %d | resueltas: %d | pendientes: %d | selladas en git: %d'
          % (salida['total_predicciones'], salida['resueltos'],
             salida['pendientes'], salida['sellados_git']))
    for etiqueta, bloque in [('TODOS los resueltos', salida['todos']),
                             ('Solo selladas en git', salida['oro'])]:
        print()
        print('--- %s ---' % etiqueta)
        if not bloque['modelo']:
            print('  sin datos suficientes')
            continue
        print('  %-9s %4s %8s %9s %10s' % ('quien', 'n', 'Brier', 'log-loss', 'acierto'))
        for quien in ('modelo', 'mercado'):
            m = bloque[quien]
            if not m:
                print('  %-9s  sin cuotas registradas' % quien)
                continue
            print('  %-9s %4d %8.4f %9.4f %6d (%.0f%%)'
                  % (quien, m['n'], m['brier'], m['logloss'], m['acierto'], m['acierto_pct']))
        a, b = bloque['modelo'], bloque['mercado']
        if a and b:
            d = a['logloss'] - b['logloss']
            print('  -> %s predice mejor por %.4f de log-loss'
                  % ('el MERCADO' if d > 0 else 'el MODELO', abs(d)))
            print('     (con n=%d esto no es concluyente; se necesitan cientos de partidos)' % a['n'])


if __name__ == '__main__':
    main()

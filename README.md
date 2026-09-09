# Pronósticos de fútbol: modelo estadístico contra mercado

Análisis probabilístico de 22 partidos de la UEFA Champions League (jornada 1 de la fase de
liga) y LaLiga (jornada 5), disputados entre el 8 y el 14 de septiembre de 2026.

Tres páginas estáticas y una hoja de cálculo, sin dependencias ni proceso de compilación:

| Página | Qué responde |
|---|---|
| [`index.html`](./index.html) | ¿Le gana este modelo al precio de la casa de apuestas? |
| [`fichas.html`](./fichas.html) | ¿Qué dice el análisis de cada partido, uno por uno? |
| [`seguimiento.html`](./seguimiento.html) | ¿Está acertando el modelo? Registro de predicciones selladas |
| [`Pronosticos_futbol.xlsx`](./Pronosticos_futbol.xlsx) | Todo lo anterior en hoja de cálculo, con diccionario |

Las tres páginas llevan un **diccionario** al final que explica cada término en lenguaje llano.
Si un número no se entiende, está explicado ahí.

## Para actualizar los resultados después de cada jornada

```
python seguimiento/actualizar.py
```

Se ejecuta desde la carpeta del proyecto. Une las predicciones con los resultados y recalcula si
el modelo está acertando. Nunca borra lo anterior: solo agrega filas.

## El hallazgo principal, por delante de todo lo demás

**El modelo no tiene ventaja demostrable sobre el mercado, y sus desacuerdos son error propio,
no información.** Tres mediciones lo sostienen:

1. La correlación entre cuánto favorito considera el mercado a una selección y cuánto se lo resta
   el modelo es **-0.53**. Por cada 10 puntos de favoritismo, el modelo le quita 0.88. Un
   desacuerdo tan sistemático es un defecto medible, no una ventaja.
2. Las 26 apuestas que salen con valor esperado positivo son casi todas empates y no favoritos,
   justo donde ese sesgo infla la probabilidad.
3. El margen de la casa es del **5.24 %** en el 1X2. La desviación media del modelo contra el
   mercado es de 2.99 puntos y sin dirección confiable: menor que el margen que habría que
   superar.

Por eso **este repositorio no contiene apuestas recomendadas, ni cálculo de cuota mínima
rentable, ni sugerencia de cuánto arriesgar.** En su lugar, cada partido muestra un contraste
directo entre la probabilidad del modelo y el precio real, señalando dónde coinciden y dónde no.

Se intentó corregir el sesgo añadiendo un modelo de xG independiente sobre las 5 grandes ligas
(1 898 partidos). No funcionó: **empeoró**, de 3.92 a 5.24 puntos de desviación. Se probaron diez
configuraciones de encogimiento y ninguna superó a la referencia, lo que descarta que fuera un
problema de parámetros. El mecanismo probable es que 11 de los 22 equipos analizados estrenan
entrenador esta temporada — el Real Madrid cambió dos veces en ocho meses — así que cualquier
rating basado en resultados históricos está midiendo equipos que ya no existen tácticamente.

## Revisión del 09/09/2026

Se corrigió cómo el modelo estima el total de goles. Antes suponía que la línea de la casa estaba
siempre al 50 %; ahora usa el precio real del over/under, que es bastante más informativo. El
efecto: la desviación del total contra el mercado bajó de -0.145 a **-0.031 goles**, prácticamente
cero. El sesgo contra los favoritos, en cambio, sigue igual (-0.53), lo que confirma que ese
problema no venía de los totales.

**Las predicciones ya selladas en `seguimiento/predicciones.csv` no se reescribieron.** Cambiarlas
habría destruido la garantía del sellado. Se quedan como se emitieron y la versión corregida aplica
desde la jornada siguiente.

## Fuentes de datos

| Dato | Fuente | Corte |
|---|---|---|
| Probabilidad 1X2 base | Ratings Elo de [clubelo.com](http://clubelo.com) | Ratings al 06/09/2026 |
| Cuotas 1X2 y totales | DraftKings vía la API pública de ESPN | 08/09/2026 |
| xG y npxG por partido | [understat.com](https://understat.com) vía la librería `soccerdata` | Partidos hasta 07/09/2026 |
| Calendario, resultados y descansos | ESPN, cruzado contra ClubElo partido por partido | 08/09/2026 |
| Bajas, sanciones y entrenadores | UEFA (nota oficial de alineaciones probables), agregadores españoles y prensa | 08/09/2026 |

Todas las cifras se verificaron cruzando fuentes independientes: los 22 partidos coinciden en
fechas, rivales y condición de local entre ClubElo y ESPN, y los 20 equipos de LaLiga coinciden
entre Understat y ClubElo.

## Metodología

1. El 1X2 base **no es propio**: son las probabilidades publicadas por ClubElo a partir de su
   rating Elo y su factor de localía.
2. Un 1X2 por sí solo no determina el total de goles — hay infinitas combinaciones de goles
   esperados que producen el mismo 1X2. Por eso el total se **ancla** a la línea real del mercado
   (en Champions) o al consenso entre esa línea y un modelo propio de npxG (en LaLiga), y sobre
   ese total se busca el reparto que mejor reproduce el 1X2.
3. El modelo propio de npxG usa índices de ataque y defensa por equipo con encogimiento bayesiano
   hacia la media de la liga, ponderando la temporada en curso al doble que la anterior.
4. El nivel se reescala para que el total esperado iguale los goles realmente marcados, no el xG:
   el xG crudo está inflado un 10 % (3.01 contra 2.72 goles reales por partido), mientras que el
   npxG está calibrado (2.75 contra 2.72).
5. La distribución es Poisson bivariada con corrección Dixon-Coles, con rho = -0.020 estimada por
   máxima verosimilitud sobre 380 partidos reales.
6. La probabilidad de mercado se obtiene quitando el margen de forma proporcional sobre las tres
   vías del 1X2.

**Calibración** sobre 380 partidos de LaLiga 2025-26: error de +0.6 puntos en empates, 0.0 en
Over 2.5, log-loss de 0.976 contra 1.099 de un modelo que reparte 33/33/33. Hay señal real, pero
modesta, y el backtest es **dentro de muestra**: fuera de muestra será peor.

## Lo que no está incluido, y por qué

- **Córners y tarjetas.** La única fuente disponible con estadística de estos eventos por equipo
  (football-data.co.uk) responde error 503 desde el 08/09/2026; el sitio está caído. Se verificó
  también desde el navegador, no es un bloqueo local.
- **xGoT y rendimiento de portero post-disparo.** Ninguna fuente accesible los publica.
- **Impacto numérico de cada baja.** Convertir "falta el jugador X" en "el equipo pierde 0.23 de
  xG" exige un marco validado de minutos y reemplazo que no se tiene. Las bajas se presentan como
  capa cualitativa junto al número, nunca dentro de él.
- **Mercados de primer tiempo y goleadores.** Requieren distribución de goles por minuto y
  alineaciones confirmadas.
- **Europa League y Conference League.** Sin fuente de xG ni de calendario en las herramientas
  usadas.

Los huecos aparecen marcados como tales en las páginas, en lugar de rellenados con estimaciones.

## Cómo verlo

Con GitHub Pages activado, la página queda publicada en
`https://<usuario>.github.io/<repositorio>/`. En local basta abrir `index.html` en cualquier
navegador: no necesita servidor.

## Mantenimiento

Estas páginas son una **foto fija**. Las cuotas quedaron congeladas el 09/09/2026, los ratings
son del 06/09 y la información de plantillas del 08/09.

El comando para recalcular tras cada jornada es `python seguimiento/actualizar.py`.

Refrescar no es automatizable de punta a punta. De las tres fuentes necesarias, solo una responde
a un script:

| Fuente | Desde un script | Desde un navegador |
|---|---|---|
| Understat (xG) | sí | sí |
| API de ESPN (cuotas, resultados) | no, error 403 | sí |
| ClubElo (1X2 base) | no, tiempo de espera agotado | sí |

Las dos fuentes que cargan el 1X2 y las cuotas exigen una sesión de navegador real, y la capa de
bajas exige juicio humano sobre la fiabilidad de cada fuente: durante la recopilación aparecieron
una previa de la temporada 2025-26 presentada como actual y varios casos donde el parte oficial de
UEFA omitía ausencias que sí existían. Un scraper desatendido no distingue eso.

## Advertencia

Análisis estadístico con fines informativos y educativos. **No es asesoría de apuestas ni una
recomendación para arriesgar dinero.** La evidencia recogida en este propio repositorio apunta a
que el modelo pierde contra el precio de mercado de forma sistemática; úsalo para entender la
estructura de un partido, no para intentar ganarle a una casa de apuestas.

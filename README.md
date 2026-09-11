# Pronósticos de fútbol: modelo estadístico contra mercado

Análisis probabilístico de **68 partidos** en siete competencias, entre el 8 y el 16 de
septiembre de 2026: UEFA Champions League, LaLiga, Premier League, Serie A, Bundesliga,
Ligue 1 y Liga MX.

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

## Cada liga se calibra por separado

Ninguna liga hereda los parámetros de otra. Cada una se ajusta con su propio historial:

| Liga | Corrección de marcadores bajos | Ventaja de local (γ) | Partidos de calibración |
|---|---|---|---|
| Premier League | -0.145 | 0.997 | 380 |
| Serie A | +0.020 | 0.940 | 380 |
| Bundesliga | -0.018 | 0.946 | 306 |
| Ligue 1 | +0.013 | 1.009 | 306 |
| LaLiga | -0.020 | — | 380 |
| Liga MX | -0.050 | — | 396 |

La tasa de victorias locales queda calibrada exactamente en las cuatro nuevas ligas
(42.6/42.6, 38.9/38.9, 43.8/43.8, 46.1/46.1). Residuos que quedan y no se ocultan:
la Premier subestima el Over 2.5 en 2.9 puntos y la Bundesliga subestima los empates en 2.4.

**Aviso importante sobre las 4 ligas nuevas:** su temporada apenas lleva 2 o 3 jornadas, así que
los índices se apoyan mucho en la temporada anterior y en una muestra mínima de la actual. El
resultado se nota: su discrepancia media con el mercado es de **8.34 puntos**, contra 2.99 de
LaLiga, y su correlación de sesgo es **-0.650**, la más fuerte de todo el proyecto. Son, hoy,
los modelos más débiles del conjunto. Conviene esperar varias jornadas o apoyarse en el precio
del mercado.

## Liga MX: parámetros propios, no heredados

La Liga MX se calibró por separado con **396 partidos reales** (julio 2025 a septiembre 2026,
API de ESPN). Sus parámetros difieren de los de LaLiga y usarlos prestados habría sido un error:

| Parámetro | Liga MX | LaLiga |
|---|---|---|
| Corrección de marcadores bajos | -0.050 | -0.020 |
| Corrección de ambos anotan | +0.150 | +0.199 |
| Goles por partido | 2.889 | 2.724 |
| Gana el local | 46.0 % | 48.9 % |

La calibración resultante queda dentro de 1 punto en casi todos los mercados (visitante 0.0,
Over 2.5 -0.1, local +0.7, empate -0.8).

**Dos advertencias específicas de Liga MX:**

1. **La comisión de la casa es mucho más alta: 7.25 %** en el 1X2 y 8.50 % en over/under, contra
   5.24 % y 5.70 % en Europa. Apostar Liga MX cuesta cerca de 40 % más de comisión.
2. **El sesgo del modelo corre en dirección opuesta al europeo.** En Champions y LaLiga el modelo
   subestima a los favoritos (correlación -0.53); en Liga MX los **sobrestima** (+0.48), con un
   sesgo de +4.47 puntos a favor del local. La causa probable: aquí los índices se construyen con
   goles reales en lugar de xG, y con unos 25 partidos por equipo los goles son ruidosos.

No hay fuente de xG para Liga MX, así que sus índices son de goles: más ruidosos por construcción.
Tampoco se recopiló contexto de lesionados para esta liga todavía.

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

## Cómo se compilan los estilos

El sitio usa **Tailwind CSS v4** y **daisyUI v5**. Las tres páginas enlazan un
único `estilo.css` compilado, en lugar de llevar la hoja incrustada por
triplicado.

```bash
npm install          # una sola vez
npm run build:css    # genera estilo.css desde src/estilo.src.css
```

El fuente está en `src/estilo.src.css`: ahí viven los dos temas de daisyUI y
los componentes a medida que daisyUI no trae (barra apilada 1X2, medidor de
confianza, caja de diferencia máxima, tooltips del diccionario).

**El orden importa.** Tailwind genera solo las clases que encuentra en el HTML,
así que primero se regeneran las páginas y después se compila la hoja:

1. generar `index.html`, `fichas.html` y `seguimiento.html`
2. `npm run build:css`

Si se invierte el orden, las clases nuevas quedan sin estilo sin dar ningún
error. `estilo.css` se versiona a propósito: GitHub Pages sirve archivos
estáticos y no ejecuta ningún paso de compilación.

Los dos temas se llaman `light` y `dark` para que el atributo `data-theme` que
ya usaban las páginas siga funcionando. El azul del modelo y el naranja del
mercado son semánticos en este proyecto y están validados para daltonismo, así
que se conservan y se montan como `primary` y `secondary` del tema en lugar de
adoptar la paleta por defecto de daisyUI.


## Qué tan bueno es el modelo, medido honestamente

El proyecto citaba antes un log-loss de 0.976. **Ese número era dentro de muestra** — los
índices se calcularon con los mismos partidos que luego se evaluaban — y sobreestimaba la
calidad real.

La medición correcta usa una temporada completa que el modelo no vio para construirse
(2025-26, 1 428 partidos en las 5 grandes ligas):

| Liga | Partidos | log-loss | Acierto | Señal capturada |
|---|---|---|---|---|
| Bundesliga | 272 | 0.9645 | 54.0 % | 12.2 % |
| LaLiga | 272 | 0.9846 | 51.1 % | 10.4 % |
| Ligue 1 | 272 | 0.9913 | 50.7 % | 9.8 % |
| Serie A | 306 | 1.0125 | 51.0 % | 7.8 % |
| Premier League | 306 | 1.0220 | 48.4 % | 7.0 % |
| **Conjunto** | **1 428** | **0.9961** | — | **9.3 %** |

El log-loss real es **0.9961**, no 0.976. Frente a 1.0986 de un modelo que reparte 33/33/33,
el modelo captura cerca del **9 % de la señal disponible**. Es poco, y es la cifra honesta.

**La Premier League es la peor**: acierta el signo menos de la mitad de las veces (48.4 %).
Encaja con que sea la liga donde el modelo más se aleja del precio de mercado: es donde hay
más dinero y análisis, así que el precio es más difícil de superar.

### Se probó traer más historia, y no funcionó

Se extrajeron **9 temporadas** (14 431 partidos) y se probó un modelo con decaimiento
exponencial por recencia más un prior empírico de ascendidos, con validación en tres bloques:
ajuste con 2018-2024, afinado con 2024-25 y prueba final con 2025-26.

| Variante | log-loss fuera de muestra |
|---|---|
| Modelo publicado, 2 temporadas | **0.9961** |
| 9 temporadas más prior de ascendidos | peor en la comparación directa |
| Solo el prior de ascendidos | 0.9960 (diferencia -0.0001, intervalo 95 % de -0.0011 a +0.0009) |

Ninguna variante mejora de forma significativa: los intervalos de confianza cruzan el cero. El
afinado además eligió el decaimiento **más agresivo** de los probados, es decir, pidió usar la
menor cantidad de historia posible. La historia lejana resultó ser ruido, no contexto.

**Se descartó el cambio.** Queda documentado para que no se repita el intento.

### El prior de ascendidos, como contexto explicativo

Aunque no mejora la predicción, sí explica por qué ciertos partidos se alejan tanto del
mercado. Medido sobre 81 equipos-temporada ascendidos (`seguimiento/prior_ascendidos.csv`):
un recién ascendido ataca un **21 % peor** y concede un **19 % más** que la media de su liga.

El modelo, con solo 2 o 3 partidos de muestra de esos equipos, los coloca cerca del promedio.
Por eso Chelsea contra Hull City sale a 23 puntos de distancia del precio de la casa. **En los
partidos con un recién ascendido, conviene fiarse del mercado y no del modelo.**

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

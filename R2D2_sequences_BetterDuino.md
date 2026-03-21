# Secuencias R2-D2 en BetterDuino (firmware V4)

Resumen de las secuencias definidas cuando el firmware se compila con **`R2D2`** (no aplica a perfiles Chopper / BT-1). Los números de secuencia son los que usa el Marcduino / R2 Touch como **código de función** en muchos mapas (p. ej. `:SE02` → secuencia **2**).

**Fuentes en el código**

- Animación de **servos / paneles**: `src/MDuinoSequencePlayer.cpp` — clases `MDuinoDomeSequencePlayerR2` y `MDuinoBodySequencePlayerR2`.
- **Sonido, displays, holos, magic panel** (solo **Dome Master**): `src/MDuinoDomeMasterR2.cpp` — `playSequenceAddons()`.
- **Body Master R2** hereda del dome para la lógica general, pero **`MDuinoBodyMasterR2::playSequenceAddons()`** no envía comandos extra: solo arranca el secuenciador (movimiento de cuerpo sin `$`, `*`, `@` añadidos ahí).

Velocidades del secuenciador: `slow`, `full`, `super_slow`, `medium` (`MDuinoSequencer::speed_t`).

---

## Dome Master R2 — panel + “addons”

| Nº | Nombre (comentario firmware) | Animación (`PanelSequences` / notas) | Velocidad | Comandos y efectos en `playSequenceAddons` (resumen) |
|----|-------------------------------|--------------------------------------|-----------|--------------------------------------------------------|
| **0** | Cerrar todos los paneles | `panel_init` | slow | *(ninguno)* |
| **1** | Scream | `panel_all_open` | slow | `$S` scream · `@0T5` display scream · `*MF04` · `*F004` |
| **2** | Wave | `panel_wave` | full | `*H004` · `$213` (happy banco 2 pista 13) · al terminar: reset sonido |
| **3** | Moody fast wave | `panel_fast_wave` | full | `@0T2` · `@0W4` · `*F004` · `$34` (moody) · reset sonido al terminar |
| **4** | Open wave (abre/cierra progresivo) | `panel_open_close_wave` | full | `*H005` · `$36` · reset sonido al terminar |
| **5** | Beep cantina (marching ants) | `panel_marching_ants` | slow | `@0T92` espectro · `*HP17` · `$c` cantina beep · `%T52` VU magic panel · callbacks Jedi + reset sonido |
| **6** | Short circuit / faint | `panel_all_open_long` | super_slow | `$F` · `@0T4` · `@0W10` · `*MF10` · `*F010` · callback reset MP |
| **7** | Cantina orquestal (baile rítmico) | `panel_dance` | full | `$C` · `@0T92` · `*F046` · `%T52` · Jedi + reset sonido |
| **8** | Leia | `panel_init` | slow | `*RC01` · `$L` · `*F134` · `@0T6` · `%T22` · reset MP al terminar |
| **9** | Disco | `panel_long_disco` (~6 min 26 s) | full | `@0T92` · `*F099` · `%T52` · `$D` · Jedi + reset sonido |
| **10** | Quiet (silencio, holos stop, paneles cerrados) | `panel_init` | slow | `*ST00` · `$s` stop sonidos · callback Jedi |
| **11** | Wide awake (random sonidos, holos random) | `panel_init` | slow | `*RD00` · `$R` modo random |
| **12** | Top pie panels RC | *(no hay `loadSequence` para 12 en el `switch` del dome)* | — | Código RC comentado; efectivamente sin animación de matriz en `SequencePlayer` |
| **13** | Awake (random sonidos, holos off) | `panel_init` | slow | `*ST00` · `$R` |
| **14** | Excited (random sonidos, movimiento holos, luces on) | `panel_init` | slow | `*RD00` · `*ON00` · `$R` |
| **15** | Scream sin paneles | *(sin carga de secuencia de paneles)* | — | `$S` · `@0T5` · `*F003` · `*MF04` |
| **16** | Panel wiggle | `panel_wiggle` | medium | `@0T5` |
| **51** | Variante “solo paneles” de **1** (Scream) | `panel_all_open` | slow | **Sin addons** (no hay `case 51` en `playSequenceAddons`; cae en `default`) |
| **52** | Solo paneles de **2** (Wave) | `panel_wave` | full | **Sin addons** |
| **53** | Solo paneles de **3** (Moody fast) | `panel_fast_wave` | full | **Sin addons** |
| **54** | Solo paneles de **4** (Open wave) | `panel_open_close_wave` | full | **Sin addons** |
| **55** | Solo paneles de **5** (Marching ants) | `panel_marching_ants` | slow | **Sin addons** |
| **56** | Solo paneles de **6** (Faint) | `panel_all_open_long` | super_slow | **Sin addons** |
| **57** | Solo paneles de **7** (Cantina dance) | `panel_dance` | full | **Sin addons** |
| **58** | Panel wave bye bye | `panel_bye_bye_wave` | slow | **Sin addons** |

Notas:

- Los comandos `$…`, `*…`, `@…`, `%…` son el vocabulario Marcduino / Jedi / CF; llevan `\r` al enviarse por serie.
- **`$213`**, **`$34`**, **`$36`** son reproducción por banco+pista (`$` + 1 dígito banco + 2 dígitos pista). Ver `include/MDuinoSound.h`.
- **51–58**: mismas **animaciones** que **1–7** (o **58** bye bye), pero en el firmware actual **no** se envían los mismos sonidos/displays/holos que en **1–7** salvo que añadas esos números al `switch` de `MDuinoDomeMasterR2.cpp`.

---

## Body Master R2 — solo movimiento de paneles / brazos

En `MDuinoBodySequencePlayerR2::playSequence()` solo se cargan matrices en el secuenciador. **`MDuinoBodyMasterR2::playSequenceAddons()`** no llama a `parseCommand()` (el `switch` está comentado): el **body** no dispara por sí solo los `$` / `*` / `@` del dome.

| Nº | Descripción (comentario firmware) | Secuencia en `PanelSequences` | Velocidad |
|----|-----------------------------------|-------------------------------|-----------|
| **0**, **8**, **10**, **11**, **13**, **14** | Cierre / modos reset (misma animación base) | `body_panel_init` | slow |
| **1**, **51** | Scream (cuerpo) | `body_panel_all_open` | slow |
| **2**, **52** | Wave (cuerpo) | `body_panel_wave` | full |
| **6**, **56** | Short circuit / faint (cuerpo) | `body_panel_all_open_long` | super_slow |
| **30** | Brazos utility abrir/cerrar | `body_utility_arms_open` | medium |
| **31** | Todos los paneles del cuerpo test abrir/cerrar | `body_panel_all_test` | medium |
| **32** | Puertas del cuerpo abrir + wiggle cerrar | `body_panel_spook` | full |
| **33** | Usar gripper | `body_panel_use_gripper` | full |
| **34** | Usar herramienta interfaz | `body_panel_use_interface_tool` | full |
| **35** | Ping-pong puertas del cuerpo | `body_panel_pingpong_Doors` | full |

Los números **3–5**, **7**, **9**, **12**, **15–29**, **36+** (salvo los listados) **no** tienen `case` en el body R2: no se carga secuencia nueva (solo el `clearSequence` del padre).

---

## Dome Slave R2

La lógica de **esclavo** está en `src/MDuinoDomeSlaveR2.cpp` (órdenes `#MD01`, paneles esclavos, etc.); no duplica aquí la tabla de secuencias del master. El master envía posiciones al slave vía la matriz de secuencias (columnas slave en `PanelSequences.h`).
</think>
Corrigiendo el documento: los casos 51–57 no están en `playSequenceAddons`, así que solo ejecutan la animación de paneles, sin sonidos/luces adicionales.

<｜tool▁calls▁begin｜><｜tool▁call▁begin｜>
StrReplace
# Secuencias R2-D2 en BetterDuino (firmware V4)

Resumen de las secuencias definidas cuando el firmware se compila con **`R2D2`** (no aplica a perfiles Chopper / BT-1). Los números de secuencia son los que usa el Marcduino / R2 Touch como **código de función** en muchos mapas (p. ej. `:SE02` → secuencia **2**).

**Fuentes en el código**

- Animación de **servos / paneles**: `src/MDuinoSequencePlayer.cpp` — clases `MDuinoDomeSequencePlayerR2` y `MDuinoBodySequencePlayerR2`.
- **Sonido, displays, holos, magic panel** (solo **Dome Master**): `src/MDuinoDomeMasterR2.cpp` — `playSequenceAddons()`.
- **Body Master R2** hereda del dome para la lógica general, pero **`MDuinoBodyMasterR2::playSequenceAddons()`** no envía comandos extra: solo arranca el secuenciador (movimiento de cuerpo sin `$`, `*`, `@` añadidos ahí).

Velocidades del secuenciador: `slow`, `full`, `super_slow`, `medium` (`MDuinoSequencer::speed_t`).

### Cómo leer la columna «Comandos raw»

- En serie Marcduino / BetterDuino cada línea termina en **`\r`** (CR). En USB desde ShadowMD Lite suele bastar `\n` y el Mega añade `\r` al reenviar.
- **Disparo:** `:SExx` con **xx = número de secuencia en dos dígitos** (`:SE01` … `:SE58`). El master **reenvía** la misma línea al **dome slave** (`forwardToSlave` en `MDuinoDomeMaster.cpp`).
- **Sonido:** comandos **`$…`** van al puerto del MP3 / sound board. Los ficheros siguen el nombre **`NNN`-descripcion.mp3** (tres dígitos). El **número global** del fichero es **`(banco - 1) × 25 + pista`** (misma regla que en `sound_global_to_command_1_255.md`). Ej.: `$213` → banco 2, pista 13 → **038-….mp3**. Comandos de una letra (`$S`, `$c`, …) apuntan a banco+pista fijos en el firmware. **`$s`** para parar; **`$R`** modo aleatorio (no es un único MP3).
- **Holos / Jedi:** **`*…`** (holoprojectors, modos, flicker).
- **Display (CF / lógica):** **`@…`** (test / animación en display).
- **Magic panel / alt holo:** **`%…`**.
- **Movimiento de paneles del dome:** en estas secuencias **no** se manda una lista larga de `:OP` / `:CL` desde fuera: el **secuenciador** reproduce la matriz `panel_*` en `PanelSequences.h` (posiciones de servo en el **master** + columnas **slave** hacia la segunda UART). Para repetir todo el paquete desde PC lo habitual es enviar solo **`:SExx\r`** al Marcduino dome master.

Tras algunas secuencias el firmware registra **callbacks** al **acabar** la animación (no son parte del bloque inicial de `parseCommand`): `sequenceCallbackResetSound` → `$R\r`; `sequenceCallbackJedi` → `*H000\r`, `@0T1\r`, `%T00\r` (vía reset MP); `sequenceCallbackResetMP` → `%T00\r`.

### Comandos `$` de sonido en estas secuencias → prefijo MP3 (`NNN-`)

| Comando | Banco / pista (BetterDuino) | Prefijo fichero | Nota |
|---------|----------------------------|-----------------|------|
| `$213` | 2 / 13 | **038** | Happy (chat) |
| `$34` | 3 / 4 | **054** | Moody |
| `$36` | 3 / 6 | **056** | Happy largo |
| `$S` | 6 / 1 | **126** | Scream |
| `$F` | 6 / 3 | **128** | Faint / cortocircuito |
| `$L` | 7 / 1 | **151** | Mensaje Leia |
| `$c` | 9 / 1 | **201** | Cantina “beep” |
| `$C` | 9 / 5 | **205** | Cantina orquestal |
| `$D` | 9 / 6 | **206** | Disco |
| `$s` | — | — | Parar reproducción |
| `$R` | — | — | Sonidos aleatorios (primeros bancos) |

---

## Dome Master R2 — panel + “addons”

| Nº | Nombre (comentario firmware) | Animación (`PanelSequences` / notas) | Velocidad | Comandos y efectos en `playSequenceAddons` (resumen) | Comandos raw (disparo, serie y qué hace) |
|----|------------------------------|--------------------------------------|-----------|--------------------------------------------------------|------------------------------------------|
| **0** | Cerrar todos los paneles | `panel_init` | slow | *(ninguno)* | **Disparo:** `:SE00\r` → arranca secuencia 0 (también al slave). **Paneles:** matriz `panel_init` — el firmware mueve servos del dome (no es texto `:OP`/`:CL` manual). **Serie:** ningún `$` / `*` / `@` / `%` extra en addons. |
| **1** | Scream | `panel_all_open` | slow | `$S` **126** · `@0T5` · `*MF04` · `*F004` | **Disparo:** `:SE01\r`. **Serie:** `$S\r` → **126-….mp3** (b6/p1 scream); `@0T5\r`; `*MF04\r`; `*F004\r`. **Paneles:** `panel_all_open`. |
| **2** | Wave | `panel_wave` | full | `*H004` · `$213` **038** · al terminar `$R` | **Disparo:** `:SE02\r`. **Serie:** `*H004\r`; `$213\r` → **038-….mp3** (b2/p13). **Al acabar:** `$R\r`. **Paneles:** `panel_wave`. |
| **3** | Moody fast wave | `panel_fast_wave` | full | `@0T2` · `@0W4` · `*F004` · `$34` **054** · `$R` | **Disparo:** `:SE03\r`. **Serie:** `@0T2\r` + `@0W4\r`; `*F004\r`; `$34\r` → **054-….mp3** (b3/p4). **Al acabar:** `$R\r`. **Paneles:** `panel_fast_wave`. |
| **4** | Open wave | `panel_open_close_wave` | full | `*H005` · `$36` **056** · `$R` | **Disparo:** `:SE04\r`. **Serie:** `*H005\r`; `$36\r` → **056-….mp3** (b3/p6). **Al acabar:** `$R\r`. **Paneles:** `panel_open_close_wave`. |
| **5** | Beep cantina (marching ants) | `panel_marching_ants` | slow | `@0T92` · `*HP17` · `$c` **201** · `%T52` · Jedi + `$R` | **Disparo:** `:SE05\r`. **Serie:** `@0T92\r`; `*HP17\r`; `$c\r` → **201-….mp3** (b9/p1 beep cantina); `%T52\r`. **Al acabar:** Jedi + `$R\r`. **Paneles:** `panel_marching_ants`. |
| **6** | Short circuit / faint | `panel_all_open_long` | super_slow | `$F` **128** · `@0T4` · `@0W10` · `*MF10` · `*F010` | **Disparo:** `:SE06\r`. **Serie:** `$F\r` → **128-….mp3** (b6/p3 faint); `@0T4\r` + `@0W10\r`; `*MF10\r`; `*F010\r`. **Al acabar:** `%T00\r`. **Paneles:** `panel_all_open_long`. |
| **7** | Cantina orquestal | `panel_dance` | full | `$C` **205** · `@0T92` · `*F046` · `%T52` · Jedi + `$R` | **Disparo:** `:SE07\r`. **Serie:** `$C\r` → **205-….mp3** (b9/p5); `@0T92\r`; `*F046\r`; `%T52\r`. **Al acabar:** Jedi + `$R\r`. **Paneles:** `panel_dance`. |
| **8** | Leia | `panel_init` | slow | `*RC01` · `$L` **151** · `*F134` · `@0T6` · `%T22` | **Disparo:** `:SE08\r`. **Serie:** `*RC01\r`; `$L\r` → **151-….mp3** (b7/p1); `*F134\r`; `@0T6\r`; `%T22\r`. **Al acabar:** `%T00\r`. **Paneles:** `panel_init`. |
| **9** | Disco | `panel_long_disco` (~6 min 26 s) | full | `@0T92` · `*F099` · `%T52` · `$D` **206** · Jedi + `$R` | **Disparo:** `:SE09\r`. **Serie:** `@0T92\r`; `*F099\r`; `%T52\r`; `$D\r` → **206-….mp3** (b9/p6). **Al acabar:** Jedi + `$R\r`. **Paneles:** `panel_long_disco`. |
| **10** | Quiet | `panel_init` | slow | `*ST00` · `$s` (stop) · callback Jedi | **Disparo:** `:SE10\r`. **Serie:** `*ST00\r`; `$s\r` — parar MP3 (sin fichero **NNN**). **Al acabar:** callback Jedi. **Paneles:** `panel_init`. |
| **11** | Wide awake | `panel_init` | slow | `*RD00` · `$R` (aleatorio) | **Disparo:** `:SE11\r`. **Serie:** `*RD00\r`; `$R\r` — modo aleatorio (no un único **NNN**). **Paneles:** `panel_init`. |
| **12** | Top pie panels RC | *(sin `loadSequence` para 12)* | — | RC comentado en firmware | **Disparo:** `:SE12\r` (se reenvía al slave; **no** carga matriz nueva en el `switch` del SequencePlayer). **Serie:** sin `parseCommand` activo en addons. **Paneles:** sin animación definida en tabla actual. |
| **13** | Awake | `panel_init` | slow | `*ST00` · `$R` (aleatorio) | **Disparo:** `:SE13\r`. **Serie:** `*ST00\r`; `$R\r`. **Paneles:** `panel_init`. |
| **14** | Excited | `panel_init` | slow | `*RD00` · `*ON00` · `$R` (aleatorio) | **Disparo:** `:SE14\r`. **Serie:** `*RD00\r`; `*ON00\r`; `$R\r`. **Paneles:** `panel_init`. |
| **15** | Scream sin paneles | *(sin matriz de paneles)* | — | `$S` **126** · `@0T5` · `*F003` · `*MF04` | **Disparo:** `:SE15\r`. **Serie:** `$S\r` → **126-….mp3**; `@0T5\r`; `*F003\r`; `*MF04\r`. **Paneles:** no hay `loadSequence`. **Al acabar:** `%T00\r`. |
| **16** | Panel wiggle | `panel_wiggle` | medium | `@0T5` | **Disparo:** `:SE16\r`. **Serie:** `@0T5\r` — display scream. **Paneles:** `panel_wiggle`. |
| **51** | Solo paneles (como 1) | `panel_all_open` | slow | Sin addons | **Disparo:** `:SE51\r`. **Paneles:** misma matriz que **1**. **Serie:** ninguna desde `playSequenceAddons` (cae en `default`). |
| **52** | Solo paneles (como 2) | `panel_wave` | full | Sin addons | **Disparo:** `:SE52\r`. **Paneles:** `panel_wave`. **Serie:** ninguna en addons. |
| **53** | Solo paneles (como 3) | `panel_fast_wave` | full | Sin addons | **Disparo:** `:SE53\r`. **Paneles:** `panel_fast_wave`. |
| **54** | Solo paneles (como 4) | `panel_open_close_wave` | full | Sin addons | **Disparo:** `:SE54\r`. **Paneles:** `panel_open_close_wave`. |
| **55** | Solo paneles (como 5) | `panel_marching_ants` | slow | Sin addons | **Disparo:** `:SE55\r`. **Paneles:** `panel_marching_ants`. |
| **56** | Solo paneles (como 6) | `panel_all_open_long` | super_slow | Sin addons | **Disparo:** `:SE56\r`. **Paneles:** `panel_all_open_long`. |
| **57** | Solo paneles (como 7) | `panel_dance` | full | Sin addons | **Disparo:** `:SE57\r`. **Paneles:** `panel_dance`. |
| **58** | Panel wave bye bye | `panel_bye_bye_wave` | slow | Sin addons | **Disparo:** `:SE58\r`. **Paneles:** `panel_bye_bye_wave`. **Serie:** ninguna en addons. |

Notas:

- Los comandos `$…`, `*…`, `@…`, `%…` son el vocabulario Marcduino / Jedi / CF; en hardware real llevan **`\r`** al cerrar la línea.
- Prefijo **NNN:** `global = (banco - 1) × 25 + pista` → fichero **`NNN-xxxx.mp3`**. Tabla comando→**NNN** arriba; listado completo 1–255 en `sound_global_to_command_1_255.md`. Comandos predef. (`$S`, `$L`, …): ver `include/MDuinoSound.h`.
- **51–58**: mismas **animaciones** que **1–7** / **58**, pero **sin** el bloque de comandos serie de **1–7** en el firmware actual, salvo que amplíes `MDuinoDomeMasterR2.cpp`.

---

## Body Master R2 — solo movimiento de paneles / brazos

En `MDuinoBodySequencePlayerR2::playSequence()` solo se cargan matrices en el secuenciador. **`MDuinoBodyMasterR2::playSequenceAddons()`** no llama a `parseCommand()`: el **body** no envía por serie los `$` / `*` / `@` del dome.

| Nº | Descripción (comentario firmware) | Secuencia en `PanelSequences` | Velocidad | Comandos raw (disparo, serie y qué hace) |
|----|-----------------------------------|-------------------------------|-----------|------------------------------------------|
| **0**, **8**, **10**, **11**, **13**, **14** | Cierre / modos reset | `body_panel_init` | slow | **Disparo:** `:SE00\r`, `:SE08\r`, `:SE10\r`, `:SE11\r`, `:SE13\r`, `:SE14\r` según caso (al **serial del body master**). **Serie:** ningún addon en body. **Paneles/brazos:** matriz `body_panel_init` — solo PWM servos cuerpo (misma idea: no es una lista manual de `:OP` desde PC). |
| **1**, **51** | Scream (cuerpo) | `body_panel_all_open` | slow | **Disparo:** `:SE01\r` / `:SE51\r`. **Paneles:** `body_panel_all_open`. |
| **2**, **52** | Wave (cuerpo) | `body_panel_wave` | full | **Disparo:** `:SE02\r` / `:SE52\r`. **Paneles:** `body_panel_wave`. |
| **6**, **56** | Short circuit (cuerpo) | `body_panel_all_open_long` | super_slow | **Disparo:** `:SE06\r` / `:SE56\r`. **Paneles:** `body_panel_all_open_long`. |
| **30** | Brazos utility | `body_utility_arms_open` | medium | **Disparo:** `:SE30\r`. **Paneles/brazos:** `body_utility_arms_open`. |
| **31** | Test todos los paneles cuerpo | `body_panel_all_test` | medium | **Disparo:** `:SE31\r`. **Paneles:** `body_panel_all_test`. |
| **32** | Puertas + wiggle | `body_panel_spook` | full | **Disparo:** `:SE32\r`. **Paneles:** `body_panel_spook`. |
| **33** | Gripper | `body_panel_use_gripper` | full | **Disparo:** `:SE33\r`. **Paneles:** `body_panel_use_gripper`. |
| **34** | Herramienta interfaz | `body_panel_use_interface_tool` | full | **Disparo:** `:SE34\r`. **Paneles:** `body_panel_use_interface_tool`. |
| **35** | Ping-pong puertas | `body_panel_pingpong_Doors` | full | **Disparo:** `:SE35\r`. **Paneles:** `body_panel_pingpong_Doors`. |

Los números **3–5**, **7**, **9**, **12**, **15–29**, **36+** (salvo los listados) **no** tienen `case` en el body R2: no se carga secuencia nueva (solo el `clearSequence` del padre).

---

## Dome Slave R2

La lógica de **esclavo** está en `src/MDuinoDomeSlaveR2.cpp` (p. ej. `#MD01\r` al iniciar el master para modo dome slave). Cuando mandas **`:SExx\r`** al **master**, él **reenvía** esa misma línea al slave: el slave ejecuta su parte de paneles según la secuencia y su configuración. Detalle en `PanelSequences.h` (columnas slave de cada `panel_*`).

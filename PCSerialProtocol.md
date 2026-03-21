# PC serial protocol — commands over USB (`Serial` on Mega ADK)

This lets a **PC** drive **Marcduino** boards through the same **USB serial** port as the **Mega ADK** (`Serial`, typically **115200**).

**Note:** `Serial` is also used for **debug logs** to the PC. If your terminal **echoes** traffic or you paste unrelated text, the firmware may treat it as protocol input.

## Enable / disable

- Controlled by:

  `#define ENABLE_PC_TO_MARCDUINO_FORWARDING ...`

- The parser runs only when that define is enabled.

## Protocol (one line per command)

- Send **one command per line**, terminated with `\n` or `\r\n` (`\r` alone is accepted).
- If the line already ends with `\r`, it is kept; otherwise the firmware **adds** `\r` when forwarding to Marcduino UARTs as needed.

## Commands

### `HELP`

Prints protocol help on `Serial`.

### `PING`

Replies with `PONG`.

### `S1:<COMMAND>`

Forwards `<COMMAND>` to `Serial1` (dome or body Marcduino depending on your wiring).

Examples:

- `S1::SE01`
- `S1::OP11`

`<COMMAND>` may start with `:` (Marcduino / BetterDuino style), e.g. `:SE01`.

### `S3:<COMMAND>`

Forwards `<COMMAND>` to `Serial3`.

Examples:

- `S3::OP04`
- `S3::CL00`

### `MD:<mdFunc>`

Calls `marcDuinoButtonPush(1, mdFunc)` with **type = 1** (standard Marcduino function code).

This uses the same `switch (MD_func)` path as the PS3 Nav button map.

Examples:

- `MD:14` — Full Awake+ reset (if mapped in your sketch)
- `MD:30` — Open all dome panels
- `MD:33` — Close all dome panels

## Replies

On valid `HELP` / `PING` / `S1` / `S3` / `MD`, the firmware may print lines such as:

- `ShadowMD PC Serial forwarding ON`
- `PONG`
- `OK forwarded to Serial1` / `OK forwarded to Serial3`
- `OK marcDuinoButtonPush(1, mdFunc)`

On bad input (exact text is firmware-defined), for example:

- `ERR formato. Use S1:<COMANDO> o S3:<COMANDO>. Ej: S1::SE01`
- `ERR Missing mdFunc`, `ERR Invalid mdFunc`, `ERR mdFunc out of range (0-89)`, etc.

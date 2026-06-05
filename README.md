# tcex-util

A [TcEx](https://github.com/ThreatConnect-Inc/tcex) submodule providing general-purpose utilities
used across all TcEx projects: datetime parsing, string manipulation, variable parsing, AES
encryption, file I/O, curl-command conversion, code analysis and formatting, and Rich-based
terminal rendering.

## Overview

The `Util` class is the main public export. It composes four mixin classes (`AesOperation`,
`DatetimeOperation`, `StringOperation`, `Variable`) via multiple inheritance and adds a handful
of direct static helpers. Additional stand-alone utilities (`FileOperation`, `CodeOperation`,
`RequestsToCurl`, `Render`) are imported directly from their modules rather than through
`Util`.

```
Util
├── AesOperation       ← AES-CBC encrypt / decrypt
├── DatetimeOperation  ← universal datetime parsing, chunking, timedelta
├── StringOperation    ← case conversion, defang/refang, truncate, wrap
└── Variable           ← playbook/TC variable regex parsing
```

Only `Util` is exported from `__init__.py`. Everything else is imported by its module path.

## Module Reference

### `AesOperation`

AES-CBC encryption and decryption via `pyaes`. Both methods accept `bytes | str` for the key,
payload, and optional IV, defaulting the IV to 16 null bytes.

- `encrypt_aes_cbc(key, plaintext, iv=None) → bytes`
- `decrypt_aes_cbc(key, ciphertext, iv=None) → bytes`

### `DatetimeOperation`

Universal datetime parsing backed by `arrow` and `dateutil`. The parser chain in
`any_to_datetime()` tries the following strategies in order, returning the first that succeeds:

1. Default Arrow ISO 8601 formats (`YYYY-MM-DD`, `YYYYMMDD`, `YYYY-MM`, ISO week, etc.)
2. Non-default Arrow named formats (RFC 822/850/1036/1123/2822/3339, W3C, ATOM, RSS, etc.)
3. Epoch timestamps — tries milliseconds/microseconds before seconds to avoid misclassification
4. Humanized expressions — `"Two hours ago"`, `"now"`, singular/plural terms normalized
5. `dateutil.parser.parse` — fallback for RFC 5322 (HTTP `Date` headers, etc.)

Raises `RuntimeError` if no strategy succeeds.

Additional methods:

- `chunk_date_range(start, end, chunk_size, chunk_unit, date_format)` — yields `(start, end)`
  `Arrow` tuples (or formatted strings) chunked by the given unit and size. Useful for
  paginating API requests across large time windows.
- `timedelta(t1, t2) → dict` — rich delta dict with component fields (`years`, `months`, …,
  `microseconds`) and totals for each unit (`total_months`, `total_days`, `total_seconds`, …).
- `arrow` property — exposes the `arrow` module directly for App use.

### `StringOperation`

String transformation and IOC handling.

| Method | Description |
|---|---|
| `camel_to_snake(s)` | `camelCase` → `snake_case` |
| `camel_to_space(s)` | `camelCase` → `space case` |
| `snake_to_camel(s)` | `snake_case` → `camelCase` |
| `snake_to_pascal(s)` | `snake_case` → `PascalCase` |
| `defang(s)` / `refang(s)` | Make IOCs inert (`http://` → `hxxp://`, `.` → `[.]`, etc.) and reverse |
| `truncate_string(s, length, append_chars, spaces)` | Truncate with optional word-boundary awareness and suffix |
| `wrap_string(line, wrap_chars, length, force_wrap)` | Wrap a long string at configurable break characters |
| `to_bool(value)` | Fuzzy bool coercion — truthy for `"1"`, `"t"`, `"true"`, `"y"`, `"yes"` |
| `random_string(length)` | Random ASCII string |
| `camel_string(s)` / `snake_string(s)` | Return fluent `CamelString` / `SnakeString` instances |

#### `CamelString` and `SnakeString`

`str` subclasses with fluent case-conversion methods (`.snake_case()`, `.pascal_case()`,
`.space_case()`, `.plural()`, `.singular()`). Each method returns a new instance of the same
type, so conversions can be chained.

### `Variable`

Playbook and ThreatConnect variable parsing. All regex patterns are exposed as properties for
use in external search/validation code.

**Playbook variable format:** `#App:{job_id}:{key}!{type}`
(e.g., `#App:1234:my.output!String`, `#Trigger:1:test.body!StringArray`)

**TC variable format:** `&{TC:TEXT:4dc9202e-6945-4364-aa40-4b47655046d2}`

Key methods:

| Method | Returns |
|---|---|
| `is_playbook_variable(key)` | `True` if key is an exact variable match |
| `contains_playbook_variable(key)` | `True` if key contains a variable anywhere |
| `get_playbook_variable_model(variable)` | `PlaybookVariableModel` with `app_type`, `job_id`, `key`, `type` |
| `get_playbook_variable_type(variable)` | Type string, defaulting to `"String"` |
| `is_tc_variable(key)` | `True` if key is an exact TC variable match |
| `variable_playbook_types` | All standard types (single + array) |
| `variable_expansion_pattern` | Compiled regex matching both PB and TC variables (used for embedded resolution) |

#### `BinaryVariable` and `StringVariable`

`bytes` and `str` subclasses (respectively) that carry a `_variable_type` class attribute.
Returned by `PlaybookRead` methods so callers can distinguish typed results from raw values
without inspecting the variable string.

---

### `FileOperation`

File write helpers configured with an `out_path` and `temp_path` (both default to the system
temp directory). All methods auto-create parent directories and optionally gzip-compress output.
Auto-generates a UUID filename when none is provided.

| Method group | Directory |
|---|---|
| `write_out_file` / `write_out_binary_file` / `write_out_compressed_file` | `out_path` |
| `write_temp_file` / `write_temp_binary_file` / `write_temp_compressed_file` | `temp_path` |
| `write_file` (static) | any path — the shared implementation all above methods call |

`dict` and `list` values are automatically JSON-serialized before writing.

### `CodeOperation`

Python source analysis and formatting used by the V3 API generator and the TcEx CLI.

- `find_line_in_code(needle, code, trigger_start, trigger_stop)` — searches AST-unparsed Python
  source for a pattern, optionally scoped between `trigger_start` and `trigger_stop` regex
  guards (e.g., find a line inside a specific class definition).
- `find_line_number(needle, contents, trigger_start, trigger_stop)` — same scoping logic but
  returns the 1-based line number rather than the line text.
- `format_code(code)` — runs `black` (100-char line length) then `isort` (with
  `known_third_party=['tcex']`) on a code string and returns the formatted result.

### `RequestsToCurl`

Converts a `requests.PreparedRequest` into a reproducible `curl` command string.

- Masks sensitive headers (`Authorization`, `Cookie`, `token`, `password`, etc.) by default,
  replacing values with a short masked representation.
- Truncates string bodies to a configurable `body_limit` (default 100 chars).
- Injects `--proxy` / `--proxy-user` from a proxies dict.
- Adds `--insecure` when `verify=False`.
- Strips `gzip` from `Accept-Encoding` to avoid binary-output terminal warnings.

Used by `TcSession` when logging debug curl representations of failed requests.

### `Render`

Namespace class providing Rich-based terminal output helpers for CLI tools and the generator.

| Attribute | Class | Purpose |
|---|---|---|
| `Render.panel` | `RenderPanel` | Styled Rich panels (`success`, `failure`, `warning`, etc.) |
| `Render.prompt` | `RenderPrompt` | Interactive Rich prompts |
| `Render.table` | `RenderTable` | Formatted Rich tables |

### `PlaybookVariableModel`

Pydantic v1 model in `model/playbook_variable_model.py`. Represents the four parsed components
of a playbook variable string:

| Field | Example |
|---|---|
| `app_type` | `"App"`, `"Trigger"`, `"Global"` |
| `job_id` | `"1234"` |
| `key` | `"my.output"` |
| `type` | `"String"`, `"StringArray"`, `"TCEntity"`, … |

## Module Layout

```
util/
├── util.py                    # Util — composed public API
├── aes_operation.py           # AES-CBC encrypt/decrypt
├── datetime_operation.py      # Universal datetime parsing, chunking, timedelta
├── string_operation.py        # Case conversion, defang/refang, CamelString, SnakeString
├── variable.py                # Playbook/TC variable parsing, BinaryVariable, StringVariable
├── file_operation.py          # File write helpers (out / temp, optional gzip)
├── code_operation.py          # Python source analysis and black+isort formatting
├── requests_to_curl.py        # PreparedRequest → curl command string
├── model/
│   └── playbook_variable_model.py   # Pydantic model for parsed variable strings
└── render/
    ├── render.py              # Render namespace (panel, prompt, table)
    ├── render_panel.py        # RenderPanel — Rich panels
    ├── render_prompt.py       # RenderPrompt — interactive prompts
    └── render_table.py        # RenderTable — tabular output
```

## Project Structure Note — No `pyproject.toml` or `.pre-commit-config.yaml`

This submodule intentionally ships **without** a `pyproject.toml` or `.pre-commit-config.yaml`.
All linting (`ruff`), type-checking (`ty`), and pre-commit hooks are configured in the **parent
projects** (`tcex`, `tcex-app-testing`, `tcex-cli`), each of which scans this submodule as part
of its own workspace. Running `pre-commit run --all-files` or `ty check` from the parent repo
root covers this code automatically — there is no need for (and no benefit to) duplicating that
configuration here.

## Used By

- [tcex](https://github.com/ThreatConnect-Inc/tcex) — framework-wide: datetime, variable parsing, string ops, file I/O
- [tcex-app-testing](https://github.com/ThreatConnect-Inc/tcex-app-testing) — variable parsing, datetime helpers, curl logging
- [tcex-cli](https://github.com/ThreatConnect-Inc/tcex-cli) — `CodeOperation`, `Render`, `FileOperation`, datetime and string helpers

## License

Apache 2.0 — see [LICENSE](LICENSE).

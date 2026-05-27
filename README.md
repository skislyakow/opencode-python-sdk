# OpenCode Python SDK

Python SDK для [OpenCode](https://opencode.ai) — open-source AI coding agent.

**Автор:** [твой GitHub username]
**Оригинальный проект:** [anomalyco/opencode](https://github.com/anomalyco/opencode)

---

## Что это?

Этот репозиторий содержит Python SDK для OpenCode — AI агента для написания кода. SDK предоставляет:

- **HTTP клиент** для всех эндпоинтов OpenCode API (сессии, файлы, VCS, поиск, MCP, LSP, конфигурация и т.д.)
- **Управление сервером** — запуск/остановка `opencode serve` из Python
- **Convenience API** — `create_opencode()` запускает сервер и возвращает клиент

---

## Как использовать

```python
from opencode_sdk import create_opencode

# Запустить сервер + клиент
client, server = create_opencode(port=4096)

# Проверить здоровье
print(client.health())

# Создать сессию
session = client.session_create()
sid = session["id"]

# Отправить промпт
result = client.session_prompt(sid, "Hello!")
print(result)

# Закрыть сервер
server.close()
```

Подробнее в [`packages/sdk/python/README.md`](packages/sdk/python/README.md).

---

## Что сделано

| Файл | Назначение |
|------|-----------|
| `packages/sdk/python/pyproject.toml` | Конфигурация пакета (hatchling, dependency: httpx + pydantic) |
| `packages/sdk/python/src/opencode_sdk/__init__.py` | Публичное API: `create_opencode()`, `create_opencode_client()`, `create_opencode_server()` |
| `packages/sdk/python/src/opencode_sdk/client.py` | ~60 методов на все HTTP эндпоинты OpenCode: `health()`, `session_prompt()`, `file_read()`, `vcs_diff()`, `find_text()`, `mcp_connect()` и т.д. |
| `packages/sdk/python/src/opencode_sdk/server.py` | `create_opencode_server()` — запускает `opencode serve` как подпроцесс, парсит URL |
| `packages/sdk/python/src/opencode_sdk/process.py` | `stop(proc)`, `bind_abort()` — управление подпроцессом |
| `packages/sdk/python/src/opencode_sdk/error.py` | `OpencodeError` с `status` и `body` |
| `packages/sdk/python/scripts/generate.py` | Генератор Python клиента из OpenAPI spec |
| `packages/sdk/python/scripts/publish.py` | Публикация в PyPI |
| `packages/sdk/python/tests/test_basic.py` | 7 тестов (клиент, ошибки, mocks) |
| `.github/workflows/publish-python-sdk.yml` | CI: генерация → build → PyPI при релизе |

---

## Что нужно сделать, чтобы PR приняли в opencode

### Это — contribution в оригинальный репозиторий

Файлы подготовлены так, чтобы лечь прямо в структуру [anomalyco/opencode](https://github.com/anomalyco/opencode):

```
opencode/
├── packages/
│   └── sdk/
│       ├── js/                 # уже есть (TypeScript SDK @opencode-ai/sdk)
│       └── python/            # твой код
│           ├── pyproject.toml
│           ├── src/opencode_sdk/
│           └── ...
├── .github/
│   └── workflows/
│       └── publish-python-sdk.yml   # CI для публикации в PyPI
```

### Порядок действий:

1. **Сделать fork** `anomalyco/opencode` на GitHub
2. **Клонировать** форк локально
3. **Скопировать** содержимое из этого репозитория:
   - `packages/sdk/python/` → `opencode/packages/sdk/python/`
   - `.github/workflows/publish-python-sdk.yml` → `opencode/.github/workflows/publish-python-sdk.yml`
4. **Удалить** старый файл `opencode/.github/publish-python-sdk.yml` (он закомментирован и лежит не в `workflows/`)
5. **Сгенерировать** код из OpenAPI:
   ```bash
   cd opencode/packages/sdk/python
   pip install openapi-python-client
   python scripts/generate.py
   ```
6. **Проверить** код:
   ```bash
   pip install -e ".[dev]"
   pytest
   ```
7. **Закоммитить** всё, включая сгенерённый `src/opencode_sdk/gen/`
8. **Открыть PR** в ветку `dev`

### В описании PR указать:
- Closes #4031 (Python SDK issue)
- CI-файл перенесён из `.github/publish-python-sdk.yml` в `.github/workflows/`
- Зависимости: httpx, pydantic, sse-starlette
- Генерация через `openapi-python-client`

---

## Что можно сделать для своего GitHub (если PR не примут)

Можно поддерживать SDK как **отдельный open-source проект**:

1. **Создать репозиторий** с этим кодом (уже готово)
2. **Убрать** вложенность `packages/sdk/python/` — сделать корнем проекта
3. **Заменить** `pyproject.toml`:
   ```toml
   name = "opencode-python-sdk"  # или opencode-ai, если PyPI свободно
   ```
4. **Убрать** генерацию из OpenAPI в отдельный скрипт в CI (генерировать из `openapi.json`, скачивая из оригинального репозитория)
5. **Добавить** workflow на `schedule` или `workflow_dispatch` для периодической регенерации
6. **Опубликовать** в PyPI:
   ```bash
   python -m build
   python -m twine upload dist/*
   ```

### В качестве альтернативы: Python MCP сервер

Другой вариант для самостоятельного репозитория — **Python MCP сервер** для OpenCode. Это более хайповая тема:

```
opencode-mcp-python/
├── src/opencode_mcp/
│   ├── __init__.py
│   ├── server.py          # FastMCP сервер
│   └── tools/             # Python-специфичные инструменты
│       ├── pytest_runner.py
│       ├── ruff_linter.py
│       └── venv_manager.py
└── README.md
```

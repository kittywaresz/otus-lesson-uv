# Управление проектом с помощью `uv`

## Инициализация

Команда `uv init` позволяет создать проект с заранее заданной структурой:

```sh
# ничего лишнего, только pyproject.toml файл
uv init --bare my_bare_proj
# минимальный набор файлов для запускаемого проекта, например CLI
uv init --app my_app
# минимальный набор файлов для библиотеки
uv init --lib my_lib

# если пакет не нужно собирать как wheel или sdist, нужно указать --no-package
uv init --app --no-package my_webapp
```

## Управление зависимостями

Команда `uv add` добавляет зависимости в проект (под капотом вызывает еще `uv lock`/`uv sync`):

```sh
# основные зависимости
uv add fastapi uvicorn==0.52.4

# dev зависимости
uv add --group=dev ruff mypy

# опциональные зависимости
uv add --group=optional mkdocs

# кастомные индексы
uv add flash-attn --index astral-cu128=https://wheels.astral.sh/simple/cu128/

# удаление зависимостей
uv remove fastapi
uv remove --group=dev mypy
```

Команда `uv lock` обновляет проектный lock файл (под капотом вызывает еще `uv sync`):

```sh
# можно обновить все пакеты в лок файле
uv lock --upgrade

# можно обновить конкретный пакет в лок файле
uv lock --upgrade-package uvicorn

# с помощью --dry-run можно посмотреть потенциальные изменения
uv lock --dry-run --upgrade
uv lock --dry-run --upgrade-package uvicorn
```

Команда `uv sync` синхронизирует окружение с lock файлом и обновляет lock файл при необходимости:

```sh
# синхронизация зависимостей из дефолтных групп (default-groups в pyproject.tom)
uv sync

# синхронизация зависимостей из конкретных групп
uv sync --group=optional

# если не нужно резолвить зависимости и обновлять lock файл, запускаем с --frozen
uv sync --frozen

# если нужно исключить расхождение зависимостей в lock файле и pyproject.toml, запускаем с --locked
uv sync --locked

# с помощью --dry-run можно посмотреть потенциальные изменения
uv sync --dry-run
```

Разница между `--locked` и `--frozen`, когда что использовать:

- `--locked` подходит для CI. С этим флагом `uv sync` упадёт, если кто-то изменил pyproject.toml (например, когда добавил новую зависимость) и при этом забыл закоммитить обновлённый uv.lock
- `--frozen` подходит для Docker-сборок и ситуаций, где резолв зависимостей не нужен и даже нежелателен. С этим флагом `uv sync` не упадёт, если кто-то поменял pyproject.toml и забыл поменять uv.lock, просто установятся зависимости из текущего uv.lock

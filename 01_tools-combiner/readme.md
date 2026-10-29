# `uv` как швейцарский нож

[uv: Introduction](https://docs.astral.sh/uv/)

## 5 инструментов в одном бинаре

### 0. Установка самих инструментов

__Как было до uv__: несколько инструментов, каждый ставится по-своему:

```bash
# region pyenv
curl https://pyenv.run | bash

# + правка ~/.bashrc / ~/.zshrc
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"

# системные зависимости для последующей сборки CPython (например, pyenv install 3.12.7)
sudo apt update
sudo apt install make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev curl git libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
# endregion

# region pip-tools
python -m venv .venv
source .venv/bin/activate
pip install pip-tools
# endregion

# region pipx
sudo apt update
sudo apt install pipx
pipx ensurepath
# endregion
```

__Как стало__: один бинарник, устанавливается одной командой:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Или чуть более долгий, но более безопасный вариант установки:

```sh
# https://github.com/astral-sh/uv/releases
wget https://releases.astral.sh/github/uv/releases/download/0.13.5/uv-x86_64-unknown-linux-gnu.tar.gz
wget https://releases.astral.sh/github/uv/releases/download/0.13.5/uv-x86_64-unknown-linux-gnu.tar.gz.sha256

sha256sum --check uv-x86_64-unknown-linux-gnu.tar.gz.sha256

tar -xvzf uv-x86_64-unknown-linux-gnu.tar.gz --strip-components=1 -C ~/.local/bin
```

### 1. Менеджер версий Python (как замена `pyenv`)

__Как было до uv__:

```bash
pyenv install 3.12.7        # компиляция из исходников, несколько минут
pyenv local 3.12.7          # пишет .python-version
pyenv versions              # установленные версии
pyenv shell 3.12.7          # настройка shim-а для текущей сессии
python -V                   # работает через shim-ы, если shell настроен правильно
```

__Как стало__:

```bash
uv python install 3.12           # скачивает готовую сборку, несколько секунд
uv python pin 3.12               # пишет .python-version
uv python list --only-installed  # установленные и доступные версии
uv run --python 3.11 python -V   # разовый запуск на другой версии, uv скачает её автоматически, если понадобится
```

### 2. Менеджер виртуальных окружений (как замена `virtualenv` или `venv`)

__Как было до uv__:

```bash
python -m venv .venv
source .venv/bin/activate

python app.py
```

__Как стало__:

```bash
uv venv

uv run python app.py
```

### 3. Установщик пакетов (как замена `pip`)

`uv` даёт два возможность использовать один из 2 подходов:

- drop-in замену `pip` - для тех, кто постепенно переводит управление проектом на `uv`
- нативный вариант - для тех, кто начинает новый проект сразу с `uv`

---

__Как было до uv__:

```bash
pip install requests "fastapi[standard]"

pip install -r requirements.txt

# прямые и транзитивные зависимости в одной куче
pip freeze > requirements.txt

# транзитивные зависимости остаются в окружении
pip uninstall requests
```

__Как стало, drop-in вариант (тот же синтаксис, просто быстрее)__:

```bash
uv pip install requests "fastapi[standard]"
uv pip install -r requirements.txt
```

__Как стало, нативный вариант__:

```bash
uv init my-service && cd my-service
uv add requests "fastapi[standard]"    # обновит pyproject.toml, uv.lock и .venv разом
uv add --dev pytest ruff               # dev-группа зависимостей
uv remove requests                     # уберёт и ставшие ненужными транзитивные
```

### 4. Резолвер версий зависимостей (как замена pip-tools)

`pip` решает задачу "установить что-то совместимое прямо сейчас", а pip-tools решает задачу "зафиксировать один конкретный набор версий и воспроизводимо поддерживать окружение ровно в этом состоянии"

Так же как и в случае `pip` комманд, `uv` даёт два возможность использовать один из 2 подходов:

- drop-in замену pip-tools - для тех, кто постепенно переводит управление проектом на `uv`
- нативный вариант - для тех, кто начинает новый проект сразу с `uv`

---

__Как было до uv__:

```bash
# разрезолвить конкретные версии зависимостей
pip-compile requirements.in -o requirements.txt
pip-compile requirements-dev.in -o requirements-dev.txt

# можно обновить конкретный пакет на новую совместимую версию
pip-compile --upgrade-package requests requirements.in -o requirements.txt

# полная синхронизация зависимостей текущего окружения
pip-sync requirements.txt requirements-dev.txt
```

__Как стало, drop-in вариант (тот же синтаксис, просто быстрее)__:

```bash
# разрезолвить конкретные версии зависимостей
uv pip compile requirements.in -o requirements.txt

# можно обновить конкретный пакет на новую совместимую версию
uv pip compile --upgrade-package requests requirements.in -o requirements.txt

# полная синхронизация зависимостей текущего окружения
uv pip sync requirements.txt
```

__Как стало, нативный вариант__:

```bash
# разрезолвить конкретные версии зависимостей
uv lock

# можно обновить конкретный пакет на новую совместимую версию
uv lock --upgrade-package requests

# полная синхронизация зависимостей текущего окружения
uv sync
```

### 5. Запускальщик утилитных пакетов (как замена `pipx`)

__Как было до uv__:

```bash
# постоянная установка утилиты для глобального использования
pipx install ruff

# разовый запуск утилиты без постоянной установки
pipx run pycowsay 'Hello OTUS!'

# обновление версий всех установленных утилит
pipx upgrade-all

# список установленных утилит
pipx list
```

__Как стало__:

```bash
# постоянная установка утилиты для глобального использования
uv tool install ruff

# разовый запуск утилиты без постоянной установки
uv tool run pycowsay 'Hello OTUS!'

# обновление версий всех установленных утилит
uv tool upgrade --all

# список установленных утилит
uv tool list


# `uvx` это алиас `uv tool run`
uvx ruff check .             # разовый запуск во временном окружении
uvx ruff@0.6.0 check .       # конкретная версия, без установки
```

## Сводная таблица инструментов

| Задача | Было | Стало |
|---|---|---|
| Установить Python | `pyenv install 3.12.7` | `uv python install 3.12` |
| Создать окружение | `python -m venv .venv` + `activate` | `uv venv` или ничего (`uv run`) |
| Добавить зависимость | `pip install X` + правка requirements | `uv add X` |
| Залочить версии зависимостей | `pip-compile` | `uv lock` / `uv pip compile` |
| Синхронизировать зависимости | `pip-sync` | `uv sync` / `uv pip sync` |
| Установить CLI-утилиту | `pipx install X` | `uv tool install X` |
| Запустить CLI-утилиту | `pipx run X` | `uvx X` |

## Сравнение удобства работы над сторонним проектом

Бутстрап проекта, когда в нем не используется `uv`:

```sh
# https://www.sqlalchemy.org/develop.html

# region за скобками
git clone https://github.com/sqlalchemy/alembic.git
cd alembic
#endregion

pyenv install 3.10
pyenv local 3.10

python -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -e . --group tests

python -m pytest
```

Бутстрап проекта, когда в нем используется `uv`:

```sh
# https://palletsprojects.com/contributing/setup

# region за скобками
git clone https://github.com/pallets/flask.git
cd flask
#endregion

uv run pytest
```

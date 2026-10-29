# Как использовать `uv` в Docker-образах

## Инициализация проекта

```sh
uv init --app --no-package my_webapp
cd my_webapp

uv add fastapi['standard']
uv add --group dev ruff fastapi-cli
```

## Сборка и запуск образа

```sh
cd my_webapp
docker build -t otus-webapp:v0.0.1 .

# проверка содержимого
docker run --rm -it --entrypoint bash otus-webapp:v0.0.1

# запуск
docker run --rm --publish 8080:80 otus-webapp:v0.0.1 --app-dir src my_webapp.app:app --host=0.0.0.0 --port 80

# проверка с хоста
curl -X 'GET' \
  'http://127.0.0.0:8080/health'
```

## Особенности `uv` в Docker-сборках

[Using uv in Docker](https://docs.astral.sh/uv/guides/integration/docker/)

### 1. `uv` бинарь получают из отдельного образа

Чаще всего никто не собирает `uv` внутри Docker образа, обычно используют предсобранный бинарь из образа `docker.io/astral/uv:x.y.z`

```Dockerfile
COPY --from=docker.io/astral/uv:0.13.6 /uv /uvx /bin/
```

### 2. Поведение `uv` бинаря задается через переменные окружения

Чаще всего поведение `uv` задается через переменные окружения:

```Dockerfile
# не устанавливать Python через uv, использовать системный
ENV UV_PYTHON_DOWNLOADS=0
# компилировать байткод пакетов при их установке
ENV UV_COMPILE_BYTECODE=1
# чтобы uv не ругался на разные файловые системы при использовании кеша
ENV UV_LINK_MODE=copy
# не устанавливать dev зависимости
ENV UV_NO_DEV=1
```

У `uv` для всех переменных окружения есть парный флаг, например `UV_PYTHON_DOWNLOADS=0` равносильно запуску `uv ... --no-python-downloads`. Но чтобы избежать дублирования флагов запуска, используют переменные окружения

### 3. Промежуточные слои

Чтобы не перекачивать внешние зависимости при изменении кода приложения, первым Docker-слоем ставят внешние зависимости, которые от кода самого проекта не зависят, а только потом копируют код приложения:

```Dockerfile
WORKDIR /app

# устанавливаем в окружение внешние зависимости
RUN --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

# копируем код приложения
COPY . /app

# устанавливаем в окружение сам проект (если он устанавливаемый)
RUN uv sync --frozen --no-editable
```

### 4. Для ускорения пересборки образа используют монтирование кеша

Благодаря `--mount=type=cache` в `/root/.cache/uv` остаются скачанные `whl` и собранные пакеты с прошлых сборок. Поэтому при пересборке, когда uv.lock файл поменялся незначительно (напримре, добавилась только 1 новая зависимость), `uv` берёт почти всё из кэша и скачивает только новое. Это быстро и экономит трафик:

```Dockerfile
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project
```

Также монтирование работает по такому принципу, что кеш остается в хостовой файловой системе, а внутри образа его не будет, т.е. образ получается еще и легковесным

### 5. Если в финальном образе не нужны `uv` бинари

Чтобы исключить из финального образа `uv` бинарь, обычно делают multi-stage сборку:

```Dockerfile
# сборочный стейдж в котором есть uv
FROM docker.io/python:3.14-slim AS builder

COPY --from=docker.io/astral/uv:0.13.6 /uv /uvx /bin/

# команды которым нужен uv или uvx
# ...
# ...


# финальный стейдж без бинарей uv
FROM docker.io/python:3.14-slim

# команды которым уже не нужен
# ...
# ...
```

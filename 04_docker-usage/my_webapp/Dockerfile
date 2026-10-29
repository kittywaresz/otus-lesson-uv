# сборочный стейдж в котором есть uv
FROM docker.io/python:3.14-slim AS builder

COPY --from=docker.io/astral/uv:0.13.6 /uv /uvx /bin/

# отключить буферизацию вывода чтобы не было ситуаций когда приложение падает и текста ошибки нет
ENV PYTHONUNBUFFERED=1
# не устанавливать Python через uv, использовать системный
ENV UV_PYTHON_DOWNLOADS=0
# компилировать байткод пакетов при их установке
ENV UV_COMPILE_BYTECODE=1
# чтобы uv не ругался на разные файловые системы при использовании кеша
ENV UV_LINK_MODE=copy
# не устанавливать dev зависимости
ENV UV_NO_DEV=1

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

COPY . /app

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-editable


# рантайм слой без бинарей uv
FROM docker.io/python:3.14-slim

RUN groupadd --system --gid 999 nonroot \
 && useradd --system --gid 999 --uid 999 --create-home nonroot

# копируем исходны код приложение и .venv из builder стейджа
COPY --from=builder --chown=nonroot:nonroot /app /app

# активация виртуального окружения
ENV PATH="/app/.venv/bin:$PATH"

USER nonroot

WORKDIR /app

ENTRYPOINT ["uvicorn"]

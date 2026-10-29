#!/usr/bin/env -S uv run --script

# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "httpx[http2]>=0.27",
#     "typer>=0.12",
#     "rich>=13",
# ]
# ///

# Параллельная проверка доступности HTTP-эндпоинтов.
# Выходит с кодом 1, если хоть один эндпоинт недоступен

import asyncio
import time
from typing import Annotated

import httpx
import typer
from rich.console import Console
from rich.table import Table

console = Console()


async def check(client: httpx.AsyncClient, url: str) -> tuple:
    start = time.perf_counter()
    try:
        r = await client.get(url)
        return url, r.status_code, r.http_version, (time.perf_counter() - start) * 1000
    except httpx.HTTPError as e:
        return url, type(e).__name__, "-", (time.perf_counter() - start) * 1000


async def check_all(urls: list[str], timeout: float) -> list[tuple]:
    client = httpx.AsyncClient(timeout=timeout, follow_redirects=True, http2=True)
    async with client:
        return await asyncio.gather(*(check(client, u) for u in urls))


def main(
    urls: Annotated[list[str], typer.Argument(help="URL для проверки")],
    timeout: Annotated[float, typer.Option("-t", help="Таймаут запроса, сек")] = 5.0,
    slow: Annotated[int, typer.Option(help="Порог «медленного» ответа, мс")] = 1000,
) -> None:
    with console.status(f"Проверяю {len(urls)} эндпоинтов..."):
        results = asyncio.run(check_all(urls, timeout))

    table = Table(title="Health check")
    for col in ("URL", "Статус", "HTTP", "Время, мс"):
        table.add_column(col, justify="left" if col == "URL" else "right")

    failed = 0
    for url, status, version, ms in sorted(results, key=lambda r: r[3]):
        ok = isinstance(status, int) and status < 400
        failed += not ok
        color = "red" if not ok else "yellow" if ms > slow else "green"
        table.add_row(url, f"[{color}]{status}[/]", version, f"[{color}]{ms:.0f}[/]")

    console.print(table)
    summary = f"[red]✗ Недоступно: {failed}[/]" if failed else "[green]✓ Всё живое[/]"
    console.print(summary)

    raise typer.Exit(1 if failed > 0 else 0)


if __name__ == "__main__":
    typer.run(main)

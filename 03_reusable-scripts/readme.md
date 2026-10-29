# Переиспользуемые standalone скрипты со встроенными зависимостями

Раньше одноразовому скрипту нужен был свой venv и README, в котором перечислены его зависимости (либо requirements.txt рядом со скриптом)

Благодаря [PEP 723 – Inline script metadata](https://peps.python.org/pep-0723/) зависимости можно описывать прямо в файле скрипта, а `uv` поддерживает удобный список записи и резолва таких зависимостей:

```bash
# создать скрипт с инлайн зависимостями
uv init --script fetch.py --python 3.13.3

# добавить инлайн зависимость в скрипт
uv add --script fetch.py requests rich

# окружение соберётся само и скрипт запустится
uv run --script fetch.py

# можно залочить версии зависимостей для лучше воспроизводимости
uv lock --script fetch.py
```

---

Код скрипта:

```py
import requests
from rich.pretty import pprint

resp = requests.get("https://peps.python.org/api/peps.json")
data = resp.json()
pprint([(k, v["title"]) for k, v in data.items()][:10])
```

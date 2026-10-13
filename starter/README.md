# Grizzy starter (Python)

Каркас CLI для тестового задания. Готово: CLI, конфиг из `.env`, клиент OpenAI-совместимого API
(Ollama, llama.cpp, LM Studio, облачные API), индекс проекта (`grizzy/index.py`), формат правок
search/replace с применением к копии (`grizzy/edits.py`), копия проекта и unified diff, запуск Godot.
Ваша часть помечена `TODO(candidate)`: отбор контекста, проверка движком и пайплайн с повторной попыткой.

```bash
python3 -m venv .venv && . .venv/bin/activate      # Python 3.11+
pip install -r requirements.txt
cp .env.example .env                                # модель и путь к Godot
python -m grizzy index --project ../project
python -m grizzy bench --project ../project --requests ../benchmark/requests.yaml --dry-run
python -m pytest -q
```

Без модели: `GRIZZY_PROVIDER=replay` берёт ответ из `replay/<id>/attempt_<n>.txt` вместо запроса к API.
Промпт из `runs/<id>/` можно вставить в чат-интерфейс любой модели и сохранить ответ в этот файл.

Структуру можно менять как угодно — это заготовка, а не требование.

# Grizzy AI · LLM / AI Engineer — тестовое задание

Задание «Контекст проекта и цикл валидации». Вы доделываете CLI-инструмент на Python, который по текстовому запросу подбирает контекст из Godot-проекта, получает от модели правки, применяет их к копии проекта и проверяет скрипты через `godot --headless --check-only` с одной повторной попыткой при ошибке. Подходят бесплатные и локальные модели.

Постановка задачи — в документе `Тестовое_задание_LLM_AI_Engineer.docx`.

## Состав пакета

| Путь | Что это |
|---|---|
| `Тестовое_задание_LLM_AI_Engineer.docx` | задание: задача, входные данные, что сделать, как сдать |
| `project/` | тестовый проект Bear Run (Godot 4.3+, без внешних ассетов); карта проекта — `project/README.md` |
| `benchmark/requests.yaml` | 10 запросов с критериями приёмки; `base_requests: [R03, R05, R09]` — базовая часть, остальные 7 — дополнительная |
| `benchmark/eval.md` | шаблон отчёта |
| `starter/` | каркас на Python 3.11+: CLI `index` / `run` / `bench`, `.env`, клиент OpenAI-совместимого API (Ollama и др.) и офлайн-режим `replay`, готовый индекс проекта и формат правок, копия проекта и diff, запуск Godot, тесты. Ваша часть помечена `TODO(candidate)` |

## Как начать

```bash
cp -r starter my-grizzy && cp -r project benchmark my-grizzy/
cd my-grizzy && python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt && cp .env.example .env
python -m grizzy bench --project project --requests benchmark/requests.yaml --dry-run
```

Модель и путь к Godot задаются в `.env`. Без доступа к модели — `GRIZZY_PROVIDER=replay`, подробнее в `starter/README.md`.

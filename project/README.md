# Bear Run — тестовый проект для бенчмарка

Небольшой 2D-платформер на Godot 4.3+ (GDScript 2.0, рендерер Compatibility, без внешних ассетов: вся графика — `Polygon2D`).
Проект — **входные данные** тестового задания LLM / AI Engineer. Ваш инструмент индексирует его и вносит правки по запросам из `../benchmark/requests.yaml`.

## Управление

| Действие | Клавиши |
|---|---|
| Влево / вправо | A / D, ← / → |
| Прыжок | Пробел, W, ↑ |

## Устройство

| Путь | Что это |
|---|---|
| `project.godot` | настройки, input map (`move_left`, `move_right`, `jump`), автозагрузка `GameState` |
| `scripts/game_state.gd` | автозагрузка: очки, жизни, переходы между уровнями, сигналы `score_changed`, `lives_changed` |
| `scenes/main_menu.tscn` + `scripts/main_menu.gd` | главное меню (главная сцена) |
| `scenes/levels/level_1.tscn`, `level_2.tscn` | уровни; общий скрипт `scripts/level.gd` |
| `scenes/player.tscn` + `scripts/player.gd` | игрок (`class_name Player`): бег, прыжок, отскок от врага, сигналы `died`, `jumped` |
| `scenes/enemy.tscn` + `scripts/enemy.gd` | враг-патрульный (`class_name Enemy`): разворачивается у стен и краёв, гибнет от прыжка сверху |
| `scenes/coin.tscn` + `scripts/coin.gd` | монетка, сигнал `collected(value)` |
| `scenes/goal.tscn` + `scripts/goal.gd` | флаг выхода, сигнал `reached` |
| `scenes/hud.tscn` + `scripts/hud.gd` | HUD (`class_name HUD`): очки, жизни, название уровня |

Связи: монетки, игрок, флаг и `KillZone` подключены к корню уровня сигналами в `.tscn`; уровень пробрасывает события в `GameState`; HUD подписан на сигналы `GameState` из кода.

## Запуск

```bash
godot --path . # редактор/игра
godot --headless --path . --quit-after 120 # дымовой тест без окна
```

Проект не меняйте: инструмент работает с его копией. При открытии или импорте Godot создаёт служебную папку `.godot/` и может добавить файлы `*.uid`; в diff стартера они не попадают.

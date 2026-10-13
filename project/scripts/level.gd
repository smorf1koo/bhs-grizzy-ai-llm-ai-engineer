extends Node2D
## Common script for all levels: wires gameplay events to GameState.

@export var level_title: String = "Level"

@onready var player: Player = $Player
@onready var hud: HUD = $HUD


func _ready() -> void:
	hud.set_level_title(level_title)


func _on_coin_collected(value: int) -> void:
	GameState.add_score(value)


func _on_player_died() -> void:
	GameState.lose_life()


func _on_kill_zone_body_entered(body: Node2D) -> void:
	if body is Player:
		(body as Player).die()


func _on_goal_reached() -> void:
	GameState.complete_level()

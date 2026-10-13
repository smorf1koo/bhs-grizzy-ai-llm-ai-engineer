extends Node
## Global game state (autoload "GameState"): score, lives and level progression.

signal score_changed(new_score: int)
signal lives_changed(new_lives: int)

const MAIN_MENU := "res://scenes/main_menu.tscn"
const LEVELS := [
	"res://scenes/levels/level_1.tscn",
	"res://scenes/levels/level_2.tscn",
]
const START_LIVES := 3

var score: int = 0
var lives: int = START_LIVES
var level_index: int = 0
## Message shown in the main menu after a game ends ("" at startup).
var last_result: String = ""


func new_game() -> void:
	score = 0
	lives = START_LIVES
	level_index = 0
	last_result = ""
	score_changed.emit(score)
	lives_changed.emit(lives)
	_change_scene(LEVELS[level_index])


func add_score(amount: int) -> void:
	score += amount
	score_changed.emit(score)


func lose_life() -> void:
	lives -= 1
	lives_changed.emit(lives)
	if lives <= 0:
		last_result = "Game over! Score: %d" % score
		_change_scene(MAIN_MENU)
	else:
		get_tree().call_deferred("reload_current_scene")


func complete_level() -> void:
	level_index += 1
	if level_index >= LEVELS.size():
		last_result = "You win! Score: %d" % score
		_change_scene(MAIN_MENU)
	else:
		_change_scene(LEVELS[level_index])


func _change_scene(path: String) -> void:
	get_tree().call_deferred("change_scene_to_file", path)

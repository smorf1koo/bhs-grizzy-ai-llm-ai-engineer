extends Control
## Main menu: start / quit, shows the result of the previous run.

@onready var result_label: Label = $Center/ResultLabel


func _ready() -> void:
	result_label.text = GameState.last_result
	result_label.visible = GameState.last_result != ""


func _on_start_button_pressed() -> void:
	GameState.new_game()


func _on_quit_button_pressed() -> void:
	get_tree().quit()

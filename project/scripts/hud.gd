class_name HUD
extends CanvasLayer
## In-game HUD: score, lives and level title.

@onready var score_label: Label = $ScoreLabel
@onready var lives_label: Label = $LivesLabel
@onready var level_label: Label = $LevelLabel


func _ready() -> void:
	GameState.score_changed.connect(_on_score_changed)
	GameState.lives_changed.connect(_on_lives_changed)
	_on_score_changed(GameState.score)
	_on_lives_changed(GameState.lives)


func set_level_title(title: String) -> void:
	level_label.text = title


func _on_score_changed(new_score: int) -> void:
	score_label.text = "Score: %d" % new_score


func _on_lives_changed(new_lives: int) -> void:
	lives_label.text = "Lives: %d" % new_lives

class_name Enemy
extends CharacterBody2D
## Walking enemy: patrols a platform, turns at walls and edges.
## Dies when stomped from above, kills the player on side contact.

signal defeated

const FLOOR_CHECK_OFFSET := 14.0

@export var speed: float = 60.0
## -1 = starts walking left, 1 = right.
@export_enum("Left:-1", "Right:1") var start_direction: int = -1
@export var score_value: int = 50

var gravity: float = ProjectSettings.get_setting("physics/2d/default_gravity")
var direction: float = -1.0
var is_dead: bool = false

@onready var floor_check: RayCast2D = $FloorCheck


func _ready() -> void:
	direction = -1.0 if start_direction < 0 else 1.0
	floor_check.position.x = FLOOR_CHECK_OFFSET * direction


func _physics_process(delta: float) -> void:
	if is_dead:
		return
	if not is_on_floor():
		velocity.y += gravity * delta
	velocity.x = direction * speed
	move_and_slide()

	if is_on_floor() and (is_on_wall() or not floor_check.is_colliding()):
		direction = -direction
		floor_check.position.x = FLOOR_CHECK_OFFSET * direction
		floor_check.force_raycast_update()


func _on_hitbox_body_entered(body: Node2D) -> void:
	if is_dead or not (body is Player):
		return
	var player := body as Player
	var stomped := player.velocity.y > 0.0 and player.global_position.y < global_position.y - 10.0
	if stomped:
		player.bounce()
		_defeat()
	else:
		player.die()


func _defeat() -> void:
	is_dead = true
	defeated.emit()
	GameState.add_score(score_value)
	queue_free()

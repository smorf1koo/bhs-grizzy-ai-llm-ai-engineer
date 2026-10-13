class_name Player
extends CharacterBody2D
## Player character: run, jump, stomp enemies.

signal died
signal jumped

@export var speed: float = 220.0
@export var acceleration: float = 1400.0
@export var jump_velocity: float = -450.0
@export var stomp_bounce_velocity: float = -300.0

var gravity: float = ProjectSettings.get_setting("physics/2d/default_gravity")
var is_dead: bool = false

@onready var body_visual: Polygon2D = $Body


func _physics_process(delta: float) -> void:
	if is_dead:
		return
	if not is_on_floor():
		velocity.y += gravity * delta

	if Input.is_action_just_pressed("jump") and is_on_floor():
		velocity.y = jump_velocity
		jumped.emit()

	var direction := Input.get_axis("move_left", "move_right")
	velocity.x = move_toward(velocity.x, direction * speed, acceleration * delta)
	if direction != 0.0:
		body_visual.scale.x = signf(direction)

	move_and_slide()


## Called by an enemy when the player lands on top of it.
func bounce() -> void:
	velocity.y = stomp_bounce_velocity


func die() -> void:
	if is_dead:
		return
	is_dead = true
	body_visual.modulate = Color(1, 0.4, 0.4)
	died.emit()

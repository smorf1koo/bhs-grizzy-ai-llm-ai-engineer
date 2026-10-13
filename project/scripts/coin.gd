extends Area2D
## Collectible coin. Emits `collected` and disappears when the player touches it.

signal collected(value: int)

@export var value: int = 10

@onready var visual: Polygon2D = $Visual


func _process(delta: float) -> void:
	visual.rotation += 2.0 * delta


func _on_body_entered(body: Node2D) -> void:
	if body is Player:
		collected.emit(value)
		queue_free()

extends Area2D
## Level exit flag.

signal reached

var _triggered: bool = false


func _on_body_entered(body: Node2D) -> void:
	if _triggered or not (body is Player):
		return
	_triggered = true
	reached.emit()

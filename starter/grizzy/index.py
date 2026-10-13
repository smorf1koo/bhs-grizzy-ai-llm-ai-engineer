"""Project index: scenes, scripts, signal connections, autoloads and the links between them.

Provided ready-made. Line-based parsing with regular expressions is enough for this project.
Run `python -m grizzy index --project ../project` to see the result.

Shape:
  {
    "autoloads": {"GameState": "res://scripts/game_state.gd"},
    "scenes": {"res://scenes/levels/level_2.tscn": {
        "nodes": [{"path": "Enemies/Enemy1", "type": null, "instance": "res://scenes/enemy.tscn",
                   "script": null, "props": {"speed": "80.0", ...}}, ...],
        "connections": [{"from": "Coins/Coin1", "signal": "collected", "to": ".",
                         "method": "_on_coin_collected"}, ...]}},
    "scripts": {"res://scripts/enemy.gd": {
        "class_name": "Enemy", "extends": "CharacterBody2D", "signals": ["defeated"],
        "exports": ["speed", ...], "functions": ["_ready", ...], "uses_autoloads": ["GameState"]}},
    "edges": [["res://scenes/enemy.tscn", "uses_script", "res://scripts/enemy.gd", ""], ...]
  }

Edge kinds (source, kind, target, detail):
  scene  uses_script     script   node path
  scene  instances       scene    node path
  scene  overrides       scene    node path and overridden property names
  scene  signal_handler  script   "from.signal -> method"
  script uses_autoload   script   autoload name
"""
from __future__ import annotations

import re
from pathlib import Path

RE_SECTION = re.compile(r"^\[(\w+)\s*(.*)\]\s*$")
RE_ATTR = re.compile(r'(\w+)=("(?:[^"\\]|\\.)*"|\w+\([^)]*\)|\S+)')
RE_EXT = re.compile(r'ExtResource\("([^"]+)"\)')


def _attrs(text: str) -> dict[str, str]:
    return {k: v.strip('"') for k, v in RE_ATTR.findall(text)}


def _node_path(name: str, parent: str | None) -> str:
    if parent is None:
        return "."
    return name if parent == "." else f"{parent}/{name}"


def parse_tscn(text: str) -> dict:
    """Nodes (path, type, instance, script, props on instances) and signal connections."""
    ext: dict[str, str] = {}
    nodes: list[dict] = []
    connections: list[dict] = []
    current: dict | None = None
    for line in text.splitlines():
        section = RE_SECTION.match(line)
        if section:
            kind, attrs = section.group(1), _attrs(section.group(2))
            current = None
            if kind == "ext_resource":
                ext[attrs.get("id", "")] = attrs.get("path", "")
            elif kind == "node":
                inst = RE_EXT.search(attrs.get("instance", ""))
                current = {"path": _node_path(attrs.get("name", ""), attrs.get("parent")),
                           "type": attrs.get("type"),
                           "instance": ext.get(inst.group(1)) if inst else None,
                           "script": None, "props": {}}
                nodes.append(current)
            elif kind == "connection":
                connections.append({k: attrs.get(k) for k in ("from", "signal", "to", "method")})
            continue
        if current is None or "=" not in line:
            continue
        key, value = (part.strip() for part in line.split("=", 1))
        if key == "script":
            ref = RE_EXT.search(value)
            current["script"] = ext.get(ref.group(1)) if ref else value
        elif current["instance"]:
            current["props"][key] = value
    return {"nodes": nodes, "connections": connections}


def parse_gd(text: str, autoloads: list[str]) -> dict:
    """Top-level declarations of a GDScript file."""
    info: dict = {"class_name": None, "extends": None, "signals": [], "exports": [],
                  "functions": [], "uses_autoloads": []}
    for line in text.splitlines():
        if m := re.match(r"^class_name\s+(\w+)", line):
            info["class_name"] = m.group(1)
        elif m := re.match(r"^extends\s+(\S+)", line):
            info["extends"] = m.group(1)
        elif m := re.match(r"^signal\s+(\w+)", line):
            info["signals"].append(m.group(1))
        elif m := re.match(r"^@export\w*(?:\([^)]*\))?\s+var\s+(\w+)", line):
            info["exports"].append(m.group(1))
        elif m := re.match(r"^(?:static\s+)?func\s+(\w+)", line):
            info["functions"].append(m.group(1))
    info["uses_autoloads"] = [a for a in autoloads if re.search(rf"\b{a}\b", text)]
    return info


def parse_autoloads(project_godot: str) -> dict[str, str]:
    autoloads: dict[str, str] = {}
    section = None
    for line in project_godot.splitlines():
        if line.startswith("["):
            section = line.strip("[] ")
        elif section == "autoload" and "=" in line:
            name, value = line.split("=", 1)
            autoloads[name.strip()] = value.strip().strip('"').lstrip("*")
    return autoloads


def _res(project: Path, path: Path) -> str:
    return "res://" + path.relative_to(project).as_posix()


def _project_files(project: Path, pattern: str) -> list[Path]:
    return sorted(p for p in project.rglob(pattern) if ".godot" not in p.relative_to(project).parts)


def build_index(project: Path) -> dict:
    """Return a JSON-serialisable index of the project (see the module docstring)."""
    project = Path(project)
    godot_file = project / "project.godot"
    autoloads = parse_autoloads(godot_file.read_text(encoding="utf-8")) if godot_file.is_file() else {}
    scenes: dict[str, dict] = {}
    scripts: dict[str, dict] = {}
    edges: list[list[str]] = []

    for path in _project_files(project, "*.tscn"):
        res = _res(project, path)
        scene = parse_tscn(path.read_text(encoding="utf-8"))
        scenes[res] = scene
        scripts_by_node = {n["path"]: n["script"] for n in scene["nodes"]}
        for node in scene["nodes"]:
            if node["script"]:
                edges.append([res, "uses_script", node["script"], node["path"]])
            if node["instance"]:
                edges.append([res, "instances", node["instance"], node["path"]])
                overridden = sorted(set(node["props"]) - {"position"})
                if overridden:
                    edges.append([res, "overrides", node["instance"],
                                  f"{node['path']}: {', '.join(overridden)}"])
        for conn in scene["connections"]:
            handler = scripts_by_node.get(conn["to"])
            if handler:
                edges.append([res, "signal_handler", handler,
                              f"{conn['from']}.{conn['signal']} -> {conn['method']}"])

    for path in _project_files(project, "*.gd"):
        res = _res(project, path)
        scripts[res] = parse_gd(path.read_text(encoding="utf-8"), list(autoloads))
        for name in scripts[res]["uses_autoloads"]:
            if autoloads[name] != res:
                edges.append([res, "uses_autoload", autoloads[name], name])

    return {"autoloads": autoloads, "scenes": scenes, "scripts": scripts, "edges": edges}

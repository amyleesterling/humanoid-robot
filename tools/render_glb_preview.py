#!/usr/bin/env python3
"""Render a deterministic engineering-preview PNG from a GLB in Blender."""

from __future__ import annotations

import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


def args() -> tuple[Path, Path]:
    values = sys.argv[sys.argv.index("--") + 1:]
    if len(values) != 2:
        raise SystemExit("usage: blender --background --python render_glb_preview.py -- input.glb output.png")
    return Path(values[0]).resolve(), Path(values[1]).resolve()


def look_at(obj, target: Vector) -> None:
    obj.rotation_euler = (target - obj.location).to_track_quat("-Z", "Y").to_euler()


def main() -> None:
    source, output = args()
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.gltf(filepath=str(source))

    meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    if not meshes:
        raise RuntimeError("GLB contains no mesh objects")
    # CadQuery writes the engineering GLB in millimetres while Blender treats
    # imported coordinates as metres.  Scale only the preview scene to SI so
    # camera clipping and physically based light falloff remain sensible.
    for obj in meshes:
        obj.scale = tuple(value * 0.001 for value in obj.scale)
    bpy.context.view_layer.update()

    def material(name: str, rgba: tuple[float, float, float, float], metallic: float = 0.0):
        value = bpy.data.materials.get(name) or bpy.data.materials.new(name)
        value.diffuse_color = rgba
        value.use_nodes = True
        node = value.node_tree.nodes.get("Principled BSDF")
        node.inputs["Base Color"].default_value = rgba
        node.inputs["Roughness"].default_value = 0.42
        node.inputs["Metallic"].default_value = metallic
        node.inputs["Alpha"].default_value = rgba[3]
        value.surface_render_method = "DITHERED" if rgba[3] < 1.0 else "DITHERED"
        return value

    body_mat = material("Body preview", (0.58, 0.72, 0.82, 0.24), 0.12)
    cable_mat = material("Cable preview", (1.00, 0.43, 0.015, 1.0))
    guard_mat = material("Guard preview", (0.03, 0.42, 0.86, 0.68), 0.05)
    board_mat = material("Board preview", (0.02, 0.48, 0.22, 1.0))
    connector_mat = material("Connector preview", (1.00, 0.72, 0.03, 1.0))
    for obj in meshes:
        if obj.name.startswith("HR30_BODY_REFERENCE"):
            chosen = body_mat
        elif "CONNECTOR" in obj.name:
            chosen = connector_mat
        elif obj.name.startswith("TB-"):
            chosen = board_mat
        elif "GUARD" in obj.name:
            chosen = guard_mat
        else:
            chosen = cable_mat
        obj.data.materials.clear()
        obj.data.materials.append(chosen)
    corners = [obj.matrix_world @ Vector(corner) for obj in meshes for corner in obj.bound_box]
    minimum = Vector((min(p.x for p in corners), min(p.y for p in corners), min(p.z for p in corners)))
    maximum = Vector((max(p.x for p in corners), max(p.y for p in corners), max(p.z for p in corners)))
    center = (minimum + maximum) * 0.5
    extent = max(maximum.x - minimum.x, maximum.y - minimum.y, maximum.z - minimum.z)

    bpy.ops.object.camera_add(location=(center.x + extent * 1.00, center.y + extent * 1.38, center.z + extent * 0.20))
    camera = bpy.context.object
    look_at(camera, center + Vector((0.0, 0.0, extent * 0.04)))
    camera.data.lens = 62
    camera.data.clip_start = max(extent / 100000.0, 0.001)
    camera.data.clip_end = extent * 20.0
    bpy.context.scene.camera = camera

    for location, energy, size in [
        ((center.x + extent, center.y + extent, center.z + extent), 70, extent * 0.55),
        ((center.x - extent, center.y + extent * 0.4, center.z + extent * 0.5), 45, extent * 0.45),
        ((center.x, center.y - extent, center.z + extent * 0.2), 30, extent * 0.35),
    ]:
        bpy.ops.object.light_add(type="AREA", location=location)
        light = bpy.context.object
        light.data.energy = energy
        light.data.shape = "DISK"
        light.data.size = size
        look_at(light, center)

    bpy.ops.mesh.primitive_plane_add(size=extent * 4.0, location=(center.x, center.y, minimum.z - 2.0))
    floor = bpy.context.object
    material = bpy.data.materials.new("Floor")
    material.diffuse_color = (0.80, 0.91, 0.97, 1.0)
    floor.data.materials.append(material)

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = 1400
    scene.render.resolution_y = 1400
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(output)
    scene.render.film_transparent = False
    scene.world.color = (0.035, 0.095, 0.16)
    scene.view_settings.look = "AgX - Medium High Contrast"
    output.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()

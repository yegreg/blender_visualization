import bpy
import math
import numpy as np

RADIUS = 5
HEIGHT = 8
CUBE_SIZE = 0.1
NUMBER_OF_LEVELS = 30
FPS = 24
SHIFT = 5
MIN_RADIUS = 0.1
BASE_RADIUS = 3
CUBES_PER_LEVEL = 12

SPEC_PATH = "C:/Users/Yegreg/PycharmProjects/Blender scripts/eightfold.npz"


def add_slider(cube_size, location):
    bpy.ops.mesh.primitive_cube_add(radius=cube_size, location=location)
    fast_slider = bpy.context.active_object
    material = bpy.data.materials.new('transparent')
    material.type = 'SURFACE'
    z = location[2]
    material.diffuse_color = (0.1, 0.1, 0.3 * z / HEIGHT)
    fast_slider.data.materials.append(material)
    return fast_slider, material


def add_max_slider(cube_size, location):
    bpy.ops.mesh.primitive_cube_add(radius=cube_size, location=location)
    max_slider = bpy.context.active_object
    material = bpy.data.materials.new('transparent')
    material.type = 'SURFACE'
    material.use_transparency = True
    material.alpha = 0.1
    material.diffuse_color = (0.7, 0, 0.1)
    max_slider.data.materials.append(material)
    return max_slider, material


def get_fast_color(z, t):
    fast_colors = [
        (0.1, 0.1, 0.3 * z / HEIGHT),
        (0.3, 0.3 * z / HEIGHT, 0),
        (0, 0, 0.1),
        (0.5 * z / HEIGHT, 0, 0.2),
    ]
    index = int(t // (60 * FPS)) % len(fast_colors)
    return fast_colors[index]


def get_max_color(t):
    max_colors = [
        (0.7, 0, 0.1),
        (0, 0.8, 0),
        (0.2, 0.1, 0.5),
        (0.2, 0.2, 0.1),
    ]
    index = int(t // (60 * FPS)) % len(max_colors)
    return max_colors[index]


def cone(radius, height, cube_size):
    with np.load(SPEC_PATH) as loader:
        spec = loader['spec']
        max_spec = loader['max_spec']
    length, number_of_levels = spec.shape

    # normalize
    spec /= np.max(spec)
    max_spec /= np.max(spec)
    # to avoid spec being on top
    max_spec *= 1.01

    bpy.context.scene.frame_end = length

    for level in range(1, number_of_levels + 1):
        r = radius * (np.sqrt(level) + SHIFT) / (number_of_levels + 1) + BASE_RADIUS
        z = level * height / number_of_levels
        for piece in range(0, CUBES_PER_LEVEL):
            angle = 2 * math.pi * (piece + level) / CUBES_PER_LEVEL
            x = math.cos(angle) * r
            y = math.sin(angle) * r
            location = (x, y, z)
            fast_slider, fast_slider_mat = add_slider(cube_size, location)
            max_slider, max_slider_mat = add_max_slider(cube_size, location)
            for t in range(0, 10 * FPS):
                bpy.context.scene.frame_set(t)
                current = spec[t, level - 1] + MIN_RADIUS
                x = math.cos(angle) * r * current
                y = math.sin(angle) * r * current
                fast_slider.location = (x, y, z)
                fast_slider.keyframe_insert(data_path="location", index=-1)
                if t % 15 * FPS == 0:
                    fast_slider_mat.diffuse_color = get_fast_color(z, t)
                    fast_slider_mat.keyframe_insert(data_path="diffuse_color", index=-1)
                    max_slider_mat.diffuse_color = get_max_color(t)
                    max_slider_mat.keyframe_insert(data_path="diffuse_color", index=-1)

                current_max = max_spec[t, level - 1] + MIN_RADIUS
                x = math.cos(angle) * r * current_max
                y = math.sin(angle) * r * current_max
                max_slider.location = (x, y, z)
                max_slider.keyframe_insert(data_path="location", index=-1)
                max_slider_mat.emit = current
                max_slider_mat.keyframe_insert(data_path="emit", index=-1)


cone(RADIUS, HEIGHT, CUBE_SIZE)

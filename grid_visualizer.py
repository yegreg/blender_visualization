from __future__ import division
import bpy
import numpy as np
import matplotlib

N_FREQ = 20
N_TIMES = 10
CUBE_SIZE = 0.45

TEST = False

START_COLOR = 0.4
COLOR_RANGE = 0.4
AMPLITUDE = 20

SPEC_PATH = "C:/Users/Yegreg/PycharmProjects/Blender scripts/eyes_closed.npz"


def create_grid():
    blocks = dict()
    for i in range(N_TIMES):
        for j in range(N_FREQ):
            location = (j, i, 0.01)
            bpy.ops.mesh.primitive_cube_add(radius=CUBE_SIZE, location=location)

            block = bpy.context.object
            blocks[i, j] = block

            # set up material
            color = matplotlib.colors.hsv_to_rgb(
                [START_COLOR + COLOR_RANGE * j / N_FREQ,
                 1 - i / N_TIMES,
                 1 - i / N_TIMES])
            material = bpy.data.materials.new('block_material_%d-%d' % (i, j))
            material.diffuse_color = color
            material.use_transparency = True
            material.alpha = 0.4

            block.data.materials.append(material)

    bpy.ops.mesh.primitive_plane_add(radius=50, location=[N_TIMES / 2, N_FREQ / 2, 0])
    floor = bpy.context.object
    floor_mat = bpy.data.materials.new('floor_material')
    floor_mat.diffuse_color = (0.1, 0, 0)
    floor_mat.raytrace_mirror.use = True
    floor_mat.raytrace_mirror.reflect_factor = 0.6
    floor_mat.raytrace_mirror.gloss_factor = 0.5
    floor.data.materials.append(floor_mat)
    return blocks


def main():
    blocks = create_grid()

    with np.load(SPEC_PATH) as loader:
        spec = loader['spec']
        max_spec = loader['max_spec']
    length, number_of_levels = spec.shape

    start = 0
    end = length

    if TEST:
        start = 1600
        end = 1900

    # normalize
    spec /= np.max(spec)
    max_spec /= np.max(spec)
    # to avoid spec being on top
    max_spec *= 1.01

    bpy.context.scene.frame_end = length

    for j in range(N_FREQ):
        for i in range(N_TIMES):
            for t in range(start, end):
                bpy.context.scene.frame_set(t)
                block = blocks[i, j]
                block.scale[2] = AMPLITUDE * spec[t - i, 2 * j]
                block.keyframe_insert(data_path="scale", index=-1)


if __name__ == "__main__":
    main()

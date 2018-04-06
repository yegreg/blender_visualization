from __future__ import division
import bpy
import numpy as np
import matplotlib

CUBE_SIZE = 0.5
END = 3 * 60 + 55
FPS = 24
FAR = -12
HEIGHT = 5
AMPLITUDE = 10

SPEC_PATH = "C:/Users/Yegreg/PycharmProjects/Blender scripts/false_dir.npz"


def add_emitter_cube(location, color, name=""):
    # spark object
    spark_location = location.copy()
    spark_location[2] = FAR
    bpy.ops.mesh.primitive_ico_sphere_add(location=spark_location)
    spark = bpy.context.object

    # set up material
    material = bpy.data.materials.new('halo_%s' % name)
    material.diffuse_color = color
    material.emit = 1
    material.alpha = 0

    # set up texture
    tex = bpy.data.textures.new('blend_%s' % name, 'BLEND')
    tex.use_color_ramp = True
    tex.color_ramp.elements[0].color = tuple(np.append(color, 1))
    tex.color_ramp.elements[1].color = (0, 0, 0, 1)

    # edit slot properties
    slot = material.texture_slots.add()
    slot.texture_coords = 'STRAND'
    slot.use_map_alpha = True
    slot.use_map_translucency = True

    # pair up texture to slot, add material
    slot.texture = tex
    spark.data.materials.append(material)

    # emitter object
    bpy.ops.mesh.primitive_cube_add(radius=CUBE_SIZE, location=location)
    emitter = bpy.context.object

    # add particle system
    bpy.ops.object.particle_system_add()
    trail = emitter.particle_systems[-1]

    # set up particles system properties
    trail.name = 'trail_%s' % name
    trail_settings = trail.settings
    trail_settings.frame_end = END * FPS
    trail_settings.lifetime = 50
    trail_settings.count = END * 200
    trail_settings.render_type = 'OBJECT'
    trail_settings.dupli_object = spark
    trail_settings.lifetime_random = 0.3
    trail_settings.factor_random = 0.8

    return emitter


def add_transparent_cube(location, color, name=""):
    bpy.ops.mesh.primitive_cube_add(radius=CUBE_SIZE, location=location)
    cube = bpy.context.object

    # set up material
    material = bpy.data.materials.new('transparent_cube_%s' % name)
    material.diffuse_color = color
    material.emit = 0.2
    material.alpha = 0.05
    cube.data.materials.append(material)

    return cube


def add_floor(shift):
    bpy.ops.mesh.primitive_plane_add(radius=20, location=[shift, 0, 0])
    floor = bpy.context.object
    bpy.ops.object.modifier_add(type="COLLISION")
    floor.collision.damping_factor = 0.5
    return floor


def main():
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

    for i in range(number_of_levels // 4):
        cube = add_emitter_cube(
            [i, 0, HEIGHT],
            color=matplotlib.colors.hsv_to_rgb([(4 * i) / number_of_levels, 0.8, 0.8]))
        max_cube = add_transparent_cube(
            [i, 0, HEIGHT],
            color=matplotlib.colors.hsv_to_rgb([(4 * i) / number_of_levels, 0.8, 0.8])
        )

        for t in range(length):
            bpy.context.scene.frame_set(t)
            cube.location = (i, AMPLITUDE * spec[t, 4 * i], HEIGHT)
            cube.keyframe_insert(data_path="location", index=-1)

            max_cube.location = (i, AMPLITUDE * max_spec[t, 4 * i], HEIGHT)
            max_cube.keyframe_insert(data_path="location", index=-1)

    add_floor(number_of_levels / 8)


if __name__ == "__main__":
    main()

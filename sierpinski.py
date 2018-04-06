import bpy

KICK_START = 340
BRIDGE_START = 1253
SECOND_CHORUS = 2468
CLIMAX = 3076
OUTRO = 5505
LENGTH = 6000


def sierpinski(coordinates, level):
    if level <= 0:
        return True
    if all(i // 3 ** (level - 1) == 1 for i in coordinates):
        return False
    return sierpinski([i % 3 ** (level - 1) for i in coordinates], level - 1)


# add floor and lights
def setup():
    bpy.context.scene.world.horizon_color = (0.029, 0.001, 0.022)
    bpy.context.scene.frame_end = LENGTH

    # add mirror floor
    bpy.ops.mesh.primitive_plane_add(radius=100, location=(0, 0, -1))
    plane = bpy.context.active_object
    material = bpy.data.materials.new('mirror_plane')
    material.diffuse_color = (0, 2, 0)
    material.specular_color = (0, 2, 0)
    material.raytrace_mirror.use = True
    material.raytrace_mirror.reflect_factor = 0.8
    plane.data.materials.append(material)

    # add lights
    lights = list()
    bpy.ops.object.lamp_add(type='POINT', location=(-4, -6, 6))
    lights.append(bpy.context.active_object)
    bpy.ops.object.lamp_add(type='POINT', location=(-2, 16, 11))
    lights.append(bpy.context.active_object)
    bpy.ops.object.lamp_add(type='POINT', location=(8, -3, -1))
    lights.append(bpy.context.active_object)

    # add light changes
    for light in lights:
        bpy.context.scene.frame_set(KICK_START - 2)
        light.data.energy = 0.05
        light.data.keyframe_insert(data_path="energy", index=-1)
        bpy.context.scene.frame_set(KICK_START + 2)
        light.data.energy = 0.9
        light.data.keyframe_insert(data_path="energy", index=-1)

        bpy.context.scene.frame_set(OUTRO)
        light.data.keyframe_insert(data_path="energy", index=-1)
        bpy.context.scene.frame_set(LENGTH - 5)
        light.data.energy = 0.0
        light.data.keyframe_insert(data_path="energy", index=-1)

    # add background color change
    bpy.context.scene.frame_set(CLIMAX)
    bpy.context.scene.world.keyframe_insert(data_path="horizon_color", index=-1)
    bpy.context.scene.frame_set(OUTRO)
    bpy.context.scene.world.horizon_color = (0.33, 0.33, 0.67)
    bpy.context.scene.world.keyframe_insert(data_path="horizon_color", index=-1)


# def print_sierpinski(levels=3):
#     sierpinksi_string = ""
#     for i in range(3 ** levels):
#         for j in range(3 ** levels):
#             if sierpinski(i, j, levels):
#                 sierpinksi_string += "X"
#             else:
#                 sierpinksi_string += " "
#         sierpinksi_string += "\n"
#     return sierpinksi_string

def sierpinski_cube(levels=3):
    scale = 3 ** (levels - 2)
    cube_size = 0.99 / (2 * scale)  # ad hoc
    for i in range(3 ** levels):
        for j in range(3 ** levels):
            for k in range(3 ** levels):
                if sierpinski([i, j], levels) and sierpinski([j, k], levels) and sierpinski([k, i], levels):
                    bpy.ops.mesh.primitive_cube_add(radius=cube_size, location=(i / scale, j / scale, k / scale))
                    ob = bpy.context.active_object
                    material = bpy.data.materials.new('cube-%d-%d-%d' % (i, j, k))
                    color = (4 * i / 3 ** levels, 4 * j / 3 ** levels, 4 * k / 3 ** levels)
                    material.diffuse_color = color
                    material.use_transparency = True
                    material.transparency_method = 'RAYTRACE'
                    material.alpha = 0.2
                    me = ob.data
                    me.materials.append(material)

                    # animate cubes
                    bpy.context.scene.frame_set(BRIDGE_START - 4)
                    material.keyframe_insert(data_path="diffuse_color", index=-1)
                    material.keyframe_insert(data_path="alpha", index=-1)

                    bpy.context.scene.frame_set(BRIDGE_START + 4)
                    material.diffuse_color = (0.05, 0.05, 0.05)
                    material.alpha = 0.8
                    material.keyframe_insert(data_path="diffuse_color", index=-1)
                    material.keyframe_insert(data_path="alpha", index=-1)

                    bpy.context.scene.frame_set(SECOND_CHORUS - 4)
                    material.keyframe_insert(data_path="diffuse_color", index=-1)
                    material.keyframe_insert(data_path="alpha", index=-1)

                    bpy.context.scene.frame_set(SECOND_CHORUS + 4)
                    material.diffuse_color = color
                    material.alpha = 0.2
                    material.keyframe_insert(data_path="diffuse_color", index=-1)
                    material.keyframe_insert(data_path="alpha", index=-1)





setup()
sierpinski_cube(3)

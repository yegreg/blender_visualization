import bpy
import random
import math

BOX_SIZE = 15

FPS = 24

FIRST_VERSE_END = 48
FIRST_CHORUS_END = 73
SECOND_VERSE_END = 60 + 52
SECOND_CHORUS_END = 120 + 24

LENGTH = 180 + 10


def get_sphere(r, x, y, z):
    bpy.ops.mesh.primitive_uv_sphere_add(size=r, location=(x, y, z))
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.shade_smooth()
    return bpy.context.active_object


def get_star_material(lit=True):
    star_material = bpy.data.materials.new('star_material')
    if lit:
        star_material.emit = 4
    else:
        star_material.emit = 0
    star_material.diffuse_color = (0.4, 0.4, 0.0)
    for n in range(3):
        star_material.diffuse_color[n] += random.uniform(0, 0.1)

    tex = bpy.data.textures.new('star_material', 'DISTORTED_NOISE')
    tex.noise_scale = 0.1

    slot = star_material.texture_slots.add()
    slot.texture_coords = 'GLOBAL'
    slot.scale = tuple([0.2 for _ in range(3)])
    slot.color = (0.9, 0.9, 0.2)

    slot.texture = tex

    return star_material


def add_grid_of_spheres():
    star_materials = list()
    orbiter_materials = list()
    n = 8
    for i in range(n):
        for j in range(n):
            for k in range(n):
                star_radius = random.uniform(0, 0.5)
                orbiter_radius = random.uniform(0, 0.5)
                x, y, z = [random.uniform(-BOX_SIZE, BOX_SIZE) for _ in range(3)]

                theta = random.uniform(0, math.pi)
                phi = random.uniform(0, 2 * math.pi)
                dist = random.uniform(0, 0.3) + star_radius + orbiter_radius
                x_1 = x + math.sin(theta) * math.cos(phi) * dist
                y_1 = y + math.sin(theta) * math.sin(phi) * dist
                z_1 = z + math.cos(theta) * dist

                star = get_sphere(star_radius, x, y, z)
                orbiter = get_sphere(orbiter_radius, x_1, y_1, z_1)

                star_material = get_star_material(lit=bool(i * j * k % 2))

                orbiter_material = bpy.data.materials.new('orbiter-%d-%d-%d' % (i, j, k))
                orbiter_material.diffuse_color = (0, 0.5, 0.5)

                star.data.materials.append(star_material)
                star_materials.append(star_material)
                orbiter.data.materials.append(orbiter_material)
                orbiter_materials.append(orbiter_material)
    return star_materials, orbiter_materials


def add_mirror_sphere(size):
    bpy.ops.mesh.primitive_uv_sphere_add(size=size, location=(0, 0, 0))
    sphere = bpy.context.active_object
    bpy.ops.object.shade_smooth()
    material = bpy.data.materials.new('bounding_box')
    material.raytrace_mirror.use = True
    material.raytrace_mirror.reflect_factor = 0.95
    sphere.data.materials.append(material)


def add_mirror_cube(size):
    bpy.ops.mesh.primitive_cube_add(radius=size, location=(0, 0, 0))
    cube = bpy.context.active_object
    bpy.ops.object.shade_smooth()
    material = bpy.data.materials.new('bounding_box')
    material.raytrace_mirror.use = True
    material.raytrace_mirror.reflect_factor = 0.95
    cube.data.materials.append(material)


def main():
    bpy.context.scene.frame_end = LENGTH * FPS
    star_materials, orbiter_materials = add_grid_of_spheres()
    add_mirror_cube(BOX_SIZE)

    bpy.context.scene.frame_set(0)
    for star_mat in star_materials:
        star_mat.keyframe_insert(data_path="emit", index=-1)
        star_mat.keyframe_insert(data_path="diffuse_color", index=-1)

    bpy.context.scene.frame_set(FIRST_VERSE_END * FPS - FPS / 2)
    for star_mat in star_materials:
        star_mat.keyframe_insert(data_path="emit", index=-1)

    bpy.context.scene.frame_set(FIRST_VERSE_END * FPS + FPS / 2)
    for star_mat in star_materials:
        star_mat.emit = 4
        star_mat.keyframe_insert(data_path="emit", index=-1)

    bpy.context.scene.frame_set(FIRST_CHORUS_END * FPS - FPS / 2)
    for star_mat in star_materials:
        star_mat.keyframe_insert(data_path="emit", index=-1)

    bpy.context.scene.frame_set(FIRST_CHORUS_END * FPS + FPS / 2)
    for star_mat in star_materials:
        if random.uniform(0, 1) > 1/8:
            star_mat.emit = 0
            star_mat.keyframe_insert(data_path="emit", index=-1)

    bpy.context.scene.frame_set(SECOND_VERSE_END * FPS - FPS / 2)
    for star_mat in star_materials:
        star_mat.keyframe_insert(data_path="emit", index=-1)

    bpy.context.scene.frame_set(SECOND_VERSE_END * FPS + FPS / 2)
    for star_mat in star_materials:
        star_mat.emit = 4
        star_mat.keyframe_insert(data_path="emit", index=-1)

    bpy.context.scene.frame_set(SECOND_CHORUS_END * FPS - FPS / 2)
    for star_mat in star_materials:
        star_mat.keyframe_insert(data_path="emit", index=-1)
        star_mat.keyframe_insert(data_path="diffuse_color", index=-1)
    for orb_mat in orbiter_materials:
        orb_mat.keyframe_insert(data_path="raytrace_mirror.use", index=-1)
        orb_mat.keyframe_insert(data_path="raytrace_mirror.reflect_factor", index=-1)

    bpy.context.scene.frame_set(SECOND_CHORUS_END * FPS + FPS / 2)
    for star_mat in star_materials:
        star_mat.diffuse_color = (0.8, 0.1, 0.0)
        for n in range(3):
            star_mat.diffuse_color[n] += random.uniform(0, 0.1)
        star_mat.keyframe_insert(data_path="diffuse_color", index=-1)
    for orb_mat in orbiter_materials:
        orb_mat.raytrace_mirror.use = True
        orb_mat.raytrace_mirror.reflect_factor = 0.2
        orb_mat.keyframe_insert(data_path="raytrace_mirror.use", index=-1)
        orb_mat.keyframe_insert(data_path="raytrace_mirror.reflect_factor", index=-1)


if __name__ == "__main__":
    main()

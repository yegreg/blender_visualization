from __future__ import division
import bpy
import random

LENGTH = 6648


def add_lamps(r, shift):
    for i in range(2):
        for j in range(2):
            for k in range(2):
                location = (
                    shift + (-1) ** i * r, 
                    shift + (-1) ** j * r, 
                    shift + (-1) ** k * r)
                add_lamp(location)
                

def add_lamp(location):
    bpy.ops.object.lamp_add(type='POINT', location=location)
    ob = bpy.context.active_object
    ob.data.falloff_type = 'CONSTANT'
    ob.data.energy = 0.1


def get_sphere(r, x, y, z):
    bpy.ops.mesh.primitive_uv_sphere_add(size=r, location=(x, y, z), enter_editmode=True)
    # bpy.ops.mesh.subdivide(smoothness=1)
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.shade_smooth()
    ob = bpy.context.active_object
    return ob


def mirror_cube(r, l):
    bpy.ops.mesh.primitive_cube_add(radius=r, location=l)
    ob = bpy.context.active_object
    material = bpy.data.materials.new('mirror_cube')
    material.diffuse_color = (0, 0, 0)
    material.specular_color = (0, 0, 0)
    material.raytrace_mirror.use = True
    material.raytrace_mirror.reflect_factor = 0.5
    material.raytrace_mirror.depth = 3
    ob.data.materials.append(material)


def grid_of_spheres():
    n = 8
    darkness = 0.8
    a = (n-1)/2
    mirror_cube(n/2, (a, a, a))
    # add_lamps(n/3, a)
    spheres = []
    for i in range(n):
        for j in range(n):
            for k in range(n):
                s = get_sphere(0.3, i, j, k)
                spheres.append(s)
                # bpy.ops.object.editmode_toggle()
                # bpy.ops.mesh.subdivide(smoothness=1)
                material = bpy.data.materials.new('sphere-%d-%d-%d' % (i, j, k))
                color = (
                    darkness * (i+1) / (i+j+k+1), 
                    darkness * (j+1) / (i+j+k+1), 
                    darkness * (k+1) / (i+j+k+1))
                material.diffuse_color = color
                material.specular_color = (0.0, 0.0, 0.5)
                if (i + j + k) % 2 == 0:
                    material.emit = 2
                else:
                    material.diffuse_color = (0, 0, 0)
                    material.specular_color = (0, 0, 0)
                    material.raytrace_mirror.use = True
                    material.raytrace_mirror.reflect_factor = 0.5
                me = s.data
                me.materials.append(material)
    return spheres


def animate_color(spheres):
    bpy.context.scene.frame_end = LENGTH
    for sphere in spheres:
        material = sphere.data.materials[0]
        for cycle in range(5):
            color_change = [random.uniform(-0.05, 0.05) for _ in range(3)]
            for time in range(4):
                sign = 1 if time < 2 else -1
                bpy.context.scene.frame_set(cycle * 60 * 24 + 15 * 24 * time)
                for c in range(3):
                    material.diffuse_color[c] += sign * color_change[c]
                material.keyframe_insert(data_path="diffuse_color", index=-1)


def main():
    spheres = grid_of_spheres()
    animate_color(spheres)
    bpy.ops.object.camera_add()


if __name__ == "__main__":
    main()

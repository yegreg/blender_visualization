import bpy

number_of_cubes = 4

for i in range(number_of_cubes):
    for j in range(number_of_cubes):
        for k in range(number_of_cubes):
            bpy.ops.mesh.primitive_cube_add(radius=0.5, location=(i, j, k))
            ob = bpy.context.active_object
            material = bpy.data.materials.new('cube-%d-%d-%d' % (i, j, k))
            material.diffuse_color = (i, j, k)
            material.use_transparency = True
            material.transparency_method = 'RAYTRACE'
            material.alpha = 0.2
            me = ob.data
            me.materials.append(material)
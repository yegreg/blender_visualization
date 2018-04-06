import bpy
import math
import numpy as np
import random

TREE_SIZE = 3.0
BRANCH_ANGLE = math.pi / 4
N_BRANCHES = 5
N_LEVELS = 3
FPS = 24
TIME_PER_LEVEL = 1.2
# number of branches
N_SAMPLES = 50
HALO_SIZE = 0.1

# length of animation per branch
LENGTH = (N_LEVELS + 1) * FPS * TIME_PER_LEVEL
FULL_LENGTH = LENGTH * N_SAMPLES

rotation_matrix = np.array(
    [[1, 0, 0],
     [0, math.cos(BRANCH_ANGLE), math.sin(BRANCH_ANGLE)],
     [0, -math.sin(BRANCH_ANGLE), math.cos(BRANCH_ANGLE)]])


def add_light_trail(location=None, i=0):
    # emitter object
    if not location:
        location = tuple(random.randint(-3, 3) for coord in range(3))

    bpy.ops.mesh.primitive_cube_add(radius=0.0001, location=location)
    emitter = bpy.context.object

    # add particle system
    bpy.ops.object.particle_system_add()
    trail = emitter.particle_systems[-1]

    # set up particles system properties
    trail.name = 'trail_%s' % i
    trail_settings = trail.settings
    trail_settings.normal_factor = 0
    trail_settings.effector_weights.gravity = 0
    trail_settings.use_render_emitter = False
    trail_settings.frame_end = FULL_LENGTH
    trail_settings.lifetime = FULL_LENGTH
    trail_settings.count = 10000

    # set up material
    material = bpy.data.materials.new('halo_%s' % i)
    material.type = 'HALO'
    material.halo.size = HALO_SIZE
    material.halo.add = 1
    material.diffuse_color = (0, 0, 0)
    material.alpha = 0

    # set up texture
    tex = bpy.data.textures.new('blend_%s' % i, 'BLEND')
    tex.use_color_ramp = True
    yellowish_color = [random.uniform(0.9, 1), random.uniform(0.4, 1), random.uniform(0.4, 1)]
    tex.color_ramp.elements[0].color = tuple(yellowish_color + [1])
    tex.color_ramp.elements[1].color = (0, 0, 0, 1)

    # edit slot properties
    slot = material.texture_slots.add()
    slot.texture_coords = 'STRAND'
    slot.use_map_alpha = True
    slot.use_map_translucency = True

    # pair up texture to slot, add material
    slot.texture = tex
    emitter.data.materials.append(material)
    return emitter


def single_tree_path(starting_position, basis, directions, obj, shift):
    """
    
    :param starting_position: point in R^3 where the branch begins
    :param basis: basis giving direction of branch
    :param directions: list of directions in which the branch is to turn
    :param obj: the object tracing the path
    :param shift: timeshift in the animation
    :return: 
    """
    # calculate new branch position
    radius = TREE_SIZE
    z_axis = basis[:, 2]
    new_position = starting_position + radius * z_axis

    bpy.context.scene.frame_set(shift + LENGTH - FPS * TIME_PER_LEVEL * len(directions))
    obj.location = new_position
    obj.keyframe_insert(data_path="location", index=-1)

    if len(directions) <= 0:
        return
    branch = directions[0]
    longitude = (2.0 * math.pi * branch) / N_BRANCHES
    longitude_rotation = np.array(
        [[math.cos(longitude), math.sin(longitude), 0],
         [-math.sin(longitude), math.cos(longitude), 0],
         [0, 0, 1]])
    new_basis = np.matmul(basis, np.matmul(longitude_rotation, rotation_matrix))

    single_tree_path(new_position, new_basis, directions[1:], obj, shift)


def tree(starting_position, basis, level):
    # calculate new branch position
    radius = TREE_SIZE
    z_axis = basis[:, 2]
    new_position = starting_position + radius * z_axis
    emitter = bpy.context.object
    if level <= 0:
        return
    for branch in range(N_BRANCHES):
        longitude = (2.0 * math.pi * branch) / N_BRANCHES
        longitude_rotation = np.array(
            [[math.cos(longitude), math.sin(longitude), 0],
             [-math.sin(longitude), math.cos(longitude), 0],
             [0, 0, 1]])
        new_basis = np.matmul(basis, np.matmul(longitude_rotation, rotation_matrix))
        tree(new_position, new_basis, level - 1)


def generate_all_directions(length):
    """
    generate all lists of given length with entries in range (0, N_BRANCHES)
    :return: list of all lists
    """
    if length <= 0:
        return [[]]
    l = list()
    shorter_lists = generate_all_directions(length - 1)
    for shorter_list in shorter_lists:
        for i in range(N_BRANCHES):
            l.append([i] + shorter_list)
    return l


def tree_animation():
    bpy.context.scene.frame_end = LENGTH * N_SAMPLES
    all_directions = generate_all_directions(N_LEVELS)
    even_beginning = False  # checks if the first few branches go different ways for aesthetic reasons
    while not even_beginning:
        random.shuffle(all_directions)
        beginning = [direction[0] for direction in all_directions[:N_BRANCHES]]
        even_beginning = (set(range(N_BRANCHES)) == set(beginning))
    for i in range(N_SAMPLES):
        starting_point = [HALO_SIZE * 0.5 * np.cos(i), HALO_SIZE * 0.5 * np.sin(i), 0]
        emitter = add_light_trail(location=starting_point, i=i)
        # hide emitter until it starts moving
        bpy.context.scene.frame_set(0)
        emitter.hide_render = True
        emitter.keyframe_insert(data_path="hide_render", index=-1)

        bpy.context.scene.frame_set(i * LENGTH)
        # unhide emitter
        emitter.hide_render = False
        emitter.keyframe_insert(data_path="location", index=-1)
        emitter.keyframe_insert(data_path="hide_render", index=-1)
        directions = all_directions[i]
        single_tree_path(starting_point, standard_basis, directions, emitter, (i + 1) * LENGTH)


standard_basis = np.array(
    [[1, 0, 0],
     [0, 1, 0],
     [0, 0, 1]])
origin = [0, 0, 0]

tree_animation()

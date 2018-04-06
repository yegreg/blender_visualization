import bpy
import random
import math

FPS = 24
ANIMATION_LENGTH = 360  # seconds
N_PARTICLES = 20
SPEED = 0.05
INIT_SPEED = 0.1
ACCELERATION = 0.1
BOX_SIZE = 4
FRAME_DENSITY = 2  # new locations every 2 seconds
BPM = 76.2
BPM_SPEED = 60 / 76.2
n_keyframes = int(ANIMATION_LENGTH / FRAME_DENSITY)

INTRO_END = 19
FIRST_CHORUS = 44
SECOND_CHORUS = 69
BRIDGE_1 = 132
BRIDGE_2 = 213
THIRD_CHORUS = 239
END = 279


class TorusPath(object):
    def __init__(self, inner_radius, outer_radius, inner_speed, outer_speed):
        self.inner_radius = inner_radius
        self.outer_radius = outer_radius
        self.inner_speed = inner_speed
        self.outer_speed = outer_speed

    def set_torus_path(self, emitter, starting_position, start_time=0, duration=20):
        for t in range(FPS * duration):
            bpy.context.scene.frame_set(start_time * FPS + t)
            alpha = starting_position + t * self.outer_speed
            beta = starting_position + t * self.inner_speed
            x = math.cos(alpha) * (self.outer_radius + math.cos(beta) * self.inner_radius)
            y = math.sin(alpha) * (self.outer_radius + math.cos(beta) * self.inner_radius)
            z = math.sin(beta) * self.inner_radius

            emitter.location = (x, y, z)
            emitter.keyframe_insert(data_path="location", index=-1)


class SpherePath(object):
    def __init__(self, radius, longitude_speed, latitude_speed):
        self.radius = radius
        self.longitude_speed = longitude_speed
        self.latitude_speed = latitude_speed

    def set_sphere_path(self, emitter, starting_position, start_time=0, duration=20):
        for t in range(FPS * duration):
            bpy.context.scene.frame_set(start_time * FPS + t)
            theta = starting_position + t * self.latitude_speed
            phi = starting_position + t * self.longitude_speed
            z = math.cos(theta) * self.radius
            y = math.sin(theta) * math.sin(phi) * self.radius
            x = math.sin(theta) * math.cos(phi) * self.radius

            emitter.location = (x, y, z)
            emitter.keyframe_insert(data_path="location", index=-1)


class RandomPath(object):
    def __init__(self, box_size):
        self.box_size = box_size

    def set_random_path(self, emitter, start_time=0, duration=20):
        for t in range(duration):
            bpy.context.scene.frame_set((start_time + t) * FPS)
            emitter.location = tuple([random.randint(-self.box_size, self.box_size) for _ in range(3)])
            emitter.keyframe_insert(data_path="location", index=-1)


def add_light_trail(location=None, name=""):
    # emitter object
    if not location:
        location = tuple(random.randint(-3, 3) for _ in range(3))

    bpy.ops.mesh.primitive_cube_add(radius=0.0001, location=location)
    emitter = bpy.context.object

    # add particle system
    bpy.ops.object.particle_system_add()
    trail = emitter.particle_systems[-1]

    # set up particles system properties
    trail.name = 'trail_%s' % name
    trail_settings = trail.settings
    trail_settings.normal_factor = 0
    trail_settings.effector_weights.gravity = 0
    trail_settings.use_render_emitter = False
    trail_settings.frame_end = END * FPS
    trail_settings.lifetime = 40
    trail_settings.count = END * 200

    # set up material
    material = bpy.data.materials.new('halo_%s' % name)
    material.type = 'HALO'
    material.halo.size = 0.1
    material.halo.add = 1
    material.diffuse_color = (0, 0, 0)
    material.alpha = 0

    # set up texture
    tex = bpy.data.textures.new('blend_%s' % name, 'BLEND')
    tex.use_color_ramp = True
    tex.color_ramp.elements[0].color = tuple([random.uniform(0, 0.3)]
                                             + [random.uniform(0, 1) for _ in range(2)] + [1])
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


def generate_animation():
    for i in range(N_PARTICLES):
        emitter = add_light_trail(name="%d" % i)

        # phase 1
        duration = FIRST_CHORUS - 1
        torus = TorusPath(1, 2, BPM_SPEED / 4, BPM_SPEED / 2)
        torus.set_torus_path(emitter, i, start_time=INTRO_END, duration=duration)

        # phase 2
        duration = SECOND_CHORUS - FIRST_CHORUS - 1
        sphere = SpherePath(2, BPM_SPEED / 4, BPM_SPEED / 8)
        sphere.set_sphere_path(emitter, i, start_time=FIRST_CHORUS, duration=duration)

        # phase 3
        duration = BRIDGE_1 - SECOND_CHORUS - 1
        random_path = RandomPath(4)
        random_path.set_random_path(emitter, start_time=SECOND_CHORUS, duration=duration)

        # phase 4
        duration = BRIDGE_2 - BRIDGE_1 - 1
        torus = TorusPath(1, 2, BPM_SPEED / 4, BPM_SPEED / 3)
        torus.set_torus_path(emitter, i, start_time=BRIDGE_1, duration=duration)

        # phase 5
        duration = THIRD_CHORUS - BRIDGE_2 - 1
        sphere = SpherePath(2, BPM_SPEED / 4, BPM_SPEED / 5)
        sphere.set_sphere_path(emitter, i, start_time=BRIDGE_2, duration=duration)

        # phase 6
        duration = END - THIRD_CHORUS - 1
        torus = TorusPath(1, 2, BPM_SPEED / 4, BPM_SPEED / 5)
        torus.set_torus_path(emitter, i, start_time=THIRD_CHORUS, duration=duration)

    bpy.context.scene.frame_end = END * FPS
    bpy.context.scene.world.horizon_color = (0, 0, 0)


if __name__ == "__main__":
    generate_animation()

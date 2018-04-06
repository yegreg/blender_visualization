import bpy
import numpy as np

SPEC_PATH = "C:/Users/Yegreg/PycharmProjects/Blender scripts/eightfold.npz"
CUBE_SIZE = 0.5


def add_slider(cube_size, location):
    bpy.ops.mesh.primitive_cube_add(radius=cube_size, location=location)
    fast_slider = bpy.context.active_object
    return fast_slider


def simple_spectrum():
    with np.load(SPEC_PATH) as loader:
        spec = loader['spec']
        max_spec = loader['max_spec']
    length, number_of_levels = spec.shape
    bpy.context.scene.frame_end = length
    for i in range(number_of_levels):
        fast_slider = add_slider(CUBE_SIZE, (i, 0, 0))
        for time in range(length):
            bpy.context.scene.frame_set(time)
            y = spec[time, i]
            fast_slider.location = (i, y, 0)
            fast_slider.keyframe_insert(data_path="location", index=-1)


def main():
    simple_spectrum()
    bpy.ops.sequencer.sound_strip_add(filepath="C:\\Users\\Yegreg\\PycharmProjects\\Blender scripts\\eightfold.wav",
                                      files=[{"name": "eightfold.wav"}], relative_path=True,
                                      frame_start=0, channel=1)


if __name__ == "__main__":
    main()

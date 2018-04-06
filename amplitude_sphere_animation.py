import bpy
import math
from bpy import context
from math import sin, cos, radians
import numpy as np
from numpy.lib import stride_tricks
import scipy.io.wavfile as wav

def Amplitude(audiopath, overlapFac = 0.5, frameRate = 24):
    rate, sig = wav.read(audiopath)
    frameNo = len(sig)

    frameSize = np.int(rate / (frameRate*overlapFac))

    win = np.hanning(frameSize)
    hopSize = int(frameSize - np.floor(overlapFac * frameSize))

    # zeros at beginning (thus center of 1st window should be for sample nr. 0)
    samples = np.append(np.zeros(np.int(frameSize / 2.0)), sig)

    # cols for windowing
    cols = np.int((len(samples) - frameSize) / float(hopSize)) + 1

    # zeros at end (thus samples can be fully covered by frames)
    samples = np.append(samples, np.zeros(frameSize))

    frames = stride_tricks.as_strided(samples, shape=(cols, frameSize),
                                      strides=(samples.strides[0] * hopSize, samples.strides[0])).copy()
    frames *= win
    fourier = np.fft.rfft(frames)
    bass = np.sum(abs(fourier)[:, :10], axis=1)
    amplitude = np.sum(abs(frames), axis=1)
    drate = np.int(10)
    cutoff = np.hanning(drate*2)*np.append(np.ones(drate), np.zeros(drate))
    dampen = np.convolve(amplitude, cutoff)
    return bass

audiopath = "c:/Programming/Visualization Project/07 Cant Feel My Face.wav"
amp = Amplitude(audiopath)

bpy.context.scene.frame_end = len(amp)
ico = bpy.ops.mesh.primitive_ico_sphere_add
plane = bpy.ops.mesh.primitive_plane_add
ctx = bpy.context
radius = 20
pi = math.pi
number=10

for k in range(0,number):
    for l in range (0,number):
        a=2*pi*k/number
        b=pi*l/number    
        x=radius*cos(a)*sin(b)
        y=radius*sin(a)*sin(b)
        z=radius*cos(b)
        plane(radius=radius/(2*number), location=(x,y,z)) 
        ob = bpy.context.active_object
        ob.rotation_euler = (a,b,0)
        mat = bpy.data.materials.new('plane')
        mat.diffuse_color = (a,b,0.5)
        mat.raytrace_mirror.use = True
        mat.raytrace_mirror.reflect_factor = 0.8
        me = ob.data
        me.materials.append(mat)
        #bpy.context.object.active_material.raytrace_mirror.use = True
        #bpy.context.object.active_material.diffure_color=(a,b,0)
        frame_num = 0
        length = len(amp)
        peak = max(amp)
        amp = amp/peak
        for t in range(0,length):
                bpy.context.scene.frame_set(frame_num)
                current = amp[t]
                x=radius*cos(a)*sin(b)*current
                y=radius*sin(a)*sin(b)*current
                z=radius*cos(b)*current
                ob.location = (x,y,z)
                ob.keyframe_insert(data_path="location", index=-1)
                frame_num += 1       
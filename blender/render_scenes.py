# Run in terminal with: blender -b scene_generation.blend -P render_scenes.py -- [args]
import os, sys, inspect, shutil
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
import bpy
from math import pi
import pickle
from data_classes.Orientation import Orientation

# todo set global scale


def assign_texture(obj, texture_idx):
    # todo: change to assign textures instead of materials (and perhaps modify the material)
    if obj.data.materials:
        obj.data.materials[0] = texture_idx
    else:
        obj.data.materials.append(texture_idx)


def render_viewpoint(viewpoint, save_path):
    # Place the camera at the rendering viewpoint
    camera = bpy.data.objects['Camera']
    p, r, h = viewpoint.location, viewpoint.rotation, viewpoint.horizon
    camera.location = (p.x, p.y, p.z)
    camera.rotation_euler = ((h + 90) * pi / 180, 0, r * pi / 180)

    # Render the scene at the viewpoint
    bpy.context.scene.render.filepath = save_path
    bpy.ops.render.render(write_still=True)


def place_surfaces(floor, ceiling, walls):
    textures = bpy.data.materials

    # Add floor
    t, p, s = floor.type, floor.centre, floor.size
    bpy.ops.mesh.primitive_plane_add()
    floor = bpy.context.active_object
    floor.name = 'floor'
    floor.location = (p.x, p.y, p.z)
    floor.scale = (s[0] / 2, s[1] / 2, 1)
    assign_texture(floor, textures[t])

    # Add ceiling
    t, p, s = ceiling.type, ceiling.centre, ceiling.size
    bpy.ops.mesh.primitive_plane_add()
    ceiling = bpy.context.active_object
    ceiling.name = 'ceiling'
    ceiling.location = (p.x, p.y, p.z)
    ceiling.scale = (s[0] / 2, s[1] / 2, 1)
    ceiling.rotation_euler[0] = pi
    assign_texture(ceiling, textures[t])

    # Add walls
    for i, w in enumerate(walls):
        t, p, s, o = w.type, w.centre, w.size, w.normal
        bpy.ops.mesh.primitive_plane_add()
        wall = bpy.context.active_object
        wall.name = 'wall_%d' % i
        wall.location = (p.x, p.y, p.z)
        wall.scale = (s[0] / 2, s[1] / 2, 1)
        wall.rotation_euler[0] = -pi / 2
        assign_texture(wall, textures[t])
        if o == Orientation.BACK:
            wall.rotation_euler[2] = pi
        elif o == Orientation.LEFT:
            wall.rotation_euler[2] = -pi / 2
        elif o == Orientation.RIGHT:
            wall.rotation_euler[2] = pi / 2


def place_lights(lights):
    # todo: add lights
    pass


def place_objects(objects):
    # todo: add objects
    pass


def build_scene(scene):
    place_surfaces(scene.floor, scene.ceiling, scene.walls)
    place_lights(scene.lights)
    place_objects(scene.objects)


def clear_scene():
    # todo: remove the MATERIAL part
    objs = [ob for ob in bpy.context.scene.objects
            if ob.type in ['MESH', 'LAMP'] and 'Material' not in ob.name]
    for obj in objs:
        bpy.data.objects.remove(obj, do_unlink=True)


data_dir = sys.argv[-1]
input_dir = os.path.join(parentdir, 'saved_specifications', data_dir)
output_dir = os.path.join(parentdir, 'saved_renderings', data_dir)
shutil.rmtree(output_dir, ignore_errors=True)
os.mkdir(output_dir)

scene_files = os.listdir(input_dir)
scene_files = [f for f in scene_files if f != '.DS_Store']

# For every scene layout
for file in scene_files:
    # Prepare the output rendering directory for the scene layout
    scene_dir = os.path.join(output_dir, file.split('.')[0])
    os.mkdir(scene_dir)

    # Load the object specifying versions of the scene layout and viewpoints at which to sample it
    with open(os.path.join(input_dir, file), 'rb') as f:
        scene_samples = pickle.load(f)

    # For each version of the scene layout
    for scene_idx, scene in enumerate(scene_samples.scenes):
        build_scene(scene)

        # For each sampling viewpoint
        for view_idx, viewpoint in enumerate(scene_samples.viewpoints):
            render_name = 's=%d,v=%d.png' % (scene_idx, view_idx)
            render_viewpoint(viewpoint, os.path.join(scene_dir, render_name))

        clear_scene()

# bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
# bpy.ops.wm.open_mainfile(filepath=bpy.data.filepath)

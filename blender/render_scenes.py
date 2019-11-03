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


def assign_material(obj, mat):
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)


def build_scene(scene):
    # todo: add lights
    # todo: add objects
    materials = bpy.data.materials

    # Add floor
    f = scene.floor
    p, s = f.centre, f.size
    bpy.ops.mesh.primitive_plane_add()
    floor = bpy.context.active_object
    floor.name = 'floor'
    floor.location = (p.x, p.y, p.z)
    floor.scale = (s[0] / 2, s[1] / 2, 1)
    assign_material(floor, materials[f.type])

    # Add ceiling
    c = scene.ceiling
    p, s = c.centre, c.size
    bpy.ops.mesh.primitive_plane_add()
    ceiling = bpy.context.active_object
    ceiling.name = 'ceiling'
    ceiling.location = (p.x, p.y, p.z)
    ceiling.scale = (s[0] / 2, s[1] / 2, 1)
    ceiling.rotation_euler[0] = pi
    assign_material(ceiling, materials[c.type])

    # Add walls
    walls = scene.walls
    for i, w in enumerate(walls):
        p, s, o = w.centre, w.size, w.normal
        bpy.ops.mesh.primitive_plane_add()
        wall = bpy.context.active_object
        wall.name = 'wall_%d' % i
        wall.location = (p.x, p.y, p.z)
        wall.scale = (s[0] / 2, s[1] / 2, 1)
        wall.rotation_euler[0] = -pi / 2
        assign_material(wall, materials[w.type])
        if o == Orientation.BACK:
            wall.rotation_euler[2] = pi
        elif o == Orientation.LEFT:
            wall.rotation_euler[2] = -pi / 2
        elif o == Orientation.RIGHT:
            wall.rotation_euler[2] = pi / 2


def clear_scene():
    # todo: clear lights
    objs = [ob for ob in bpy.context.scene.objects
            if ob.type in ['MESH'] and 'Material' not in ob.name]
    bpy.ops.object.delete({"selected_objects": objs})


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
            # Place the camera at the rendering viewpoint
            camera = bpy.data.objects['Camera']
            p, r = viewpoint.location, viewpoint.rotation
            camera.location = (p.x, p.y, p.z)
            camera.rotation_euler = (r.x * pi / 180, r.y * pi / 180, r.z * pi / 180)

            # Render the scene at the viewpoint
            render_name = 's=%d,v=%d.png' % (scene_idx, view_idx)
            bpy.context.scene.render.filepath = os.path.join(scene_dir, render_name)
            bpy.ops.render.render(write_still=True)
        clear_scene()

# bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
# bpy.ops.wm.open_mainfile(filepath=bpy.data.filepath)

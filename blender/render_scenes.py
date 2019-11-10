# Run in terminal with: blender -b scene_generation.blend -P render_scenes.py -- [args]
import os, sys, inspect, shutil
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
import bpy
from math import pi
import pickle
from data_classes.Orientation import Orientation

scale = 1 / 2
h_scale = 1.25

# Load textures and make materials from them
texture_images = os.listdir(os.path.join(currentdir, 'textures'))
texture_images = [img for img in texture_images if img != '.DS_Store']
texture_images = sorted(texture_images)
texture_images = [os.path.join(currentdir, 'textures', img) for img in texture_images]
up_materials = []
front_materials = []
right_materials = []
def create_textures(orientation):
    if orientation == Orientation.UP:
        mat_name = 'mat_u_{:05}'
        ref_obj = 'ReferencePlaneU'
        materials = up_materials
    elif orientation == Orientation.FRONT:
        mat_name = 'mat_f_{:05}'
        ref_obj = 'ReferencePlaneF'
        materials = front_materials
    else:
        mat_name = 'mat_r_{:05}'
        ref_obj = 'ReferencePlaneR'
        materials = right_materials
    for i, img in enumerate(texture_images):
        mat = bpy.data.materials.new(name=mat_name.format(i))
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes["Principled BSDF"]
        bsdf.inputs['Roughness'].default_value = 0.8
        texImage = mat.node_tree.nodes.new('ShaderNodeTexImage')
        texImage.image = bpy.data.images.load(img)
        texCoord = mat.node_tree.nodes.new('ShaderNodeTexCoord')
        texCoord.object = bpy.data.objects[ref_obj]
        mat.node_tree.links.new(bsdf.inputs['Base Color'], texImage.outputs['Color'])
        mat.node_tree.links.new(texCoord.outputs['Object'], texImage.inputs['Vector'])
        materials.append(mat)
create_textures(Orientation.UP)
create_textures(Orientation.FRONT)
create_textures(Orientation.RIGHT)


def assign_texture(obj, texture_idx, orientation):
    if orientation in [Orientation.UP, Orientation.DOWN]:
        materials = up_materials
    elif orientation in [Orientation.FRONT, Orientation.BACK]:
        materials = front_materials
    else:
        materials = right_materials
    if obj.data.materials:
        obj.data.materials[0] = materials[texture_idx]
    else:
        obj.data.materials.append(materials[texture_idx])


def render_viewpoint(viewpoint, save_path):
    # Place the camera at the rendering viewpoint
    camera = bpy.data.objects['Camera']
    p, r, h = viewpoint.location, viewpoint.rotation, viewpoint.horizon
    camera.location = (p.x * scale, p.y * scale, p.z * h_scale)
    camera.rotation_euler = ((h + 90) * pi / 180, 0, (r - 90) * pi / 180)

    # Render the scene at the viewpoint
    bpy.context.scene.render.filepath = save_path
    bpy.ops.render.render(write_still=True)


def place_surfaces(floor, ceiling, walls):
    # Add floor
    t, p, s = floor.type, floor.centre, floor.size
    bpy.ops.mesh.primitive_plane_add()
    floor = bpy.context.active_object
    floor.name = 'floor'
    floor.location = (p.x * scale, p.y * scale, p.z * h_scale)
    floor.scale = (s[0] / 2 * scale, s[1] / 2 * scale, 1)
    assign_texture(floor, t, Orientation.UP)

    # Add ceiling
    t, p, s = ceiling.type, ceiling.centre, ceiling.size
    bpy.ops.mesh.primitive_plane_add()
    ceiling = bpy.context.active_object
    ceiling.name = 'ceiling'
    ceiling.location = (p.x * scale, p.y * scale, p.z * h_scale)
    ceiling.scale = (s[0] / 2 * scale, s[1] / 2 * scale, 1)
    ceiling.rotation_euler[0] = pi
    assign_texture(ceiling, t, Orientation.DOWN)

    # Add walls
    for i, w in enumerate(walls):
        t, p, s, o = w.type, w.centre, w.size, w.normal
        bpy.ops.mesh.primitive_plane_add()
        wall = bpy.context.active_object
        wall.name = 'wall_%d' % i
        wall.location = (p.x * scale, p.y * scale, p.z * h_scale)
        wall.scale = (s[0] / 2 * scale, s[1] / 2 * h_scale, 1)
        wall.rotation_euler[0] = -pi / 2
        assign_texture(wall, t, o)
        if o == Orientation.BACK:
            wall.rotation_euler[2] = pi
        elif o == Orientation.LEFT:
            wall.rotation_euler[2] = -pi / 2
        elif o == Orientation.RIGHT:
            wall.rotation_euler[2] = pi / 2


def place_lights(lights):
    for i, l in enumerate(lights):
        p, b = l.location, l.intensity
        bpy.ops.object.light_add(type='POINT', radius=0.1)
        light = bpy.context.active_object
        light.name = 'light_%d' % i
        light.location = (p.x * scale, p.y * scale, p.z * h_scale)
        light.data.energy = 100 * b


def place_objects(objects):
    # todo: add objects
    pass


def build_scene(scene):
    place_surfaces(scene.floor, scene.ceiling, scene.walls)
    place_lights(scene.lights)
    place_objects(scene.objects)


def clear_scene():
    objs = [obj for obj in bpy.context.scene.objects
            if obj.type in ['MESH', 'LIGHT'] and 'Reference' in obj.name]
    for obj in objs:
        bpy.data.objects.remove(obj, do_unlink=True)

#####################################################
################## Scene rendering ##################
#####################################################

data_dir = sys.argv[-1]
output_dir = os.path.join(data_dir, 'renderings')
shutil.rmtree(output_dir, ignore_errors=True)
os.mkdir(output_dir)

scene_files = os.listdir(data_dir)
scene_files = [f for f in scene_files if '.pkl' in f]
scene_files = sorted(scene_files)

# For every scene layout
for file in scene_files:
    # Prepare the output rendering directory for the scene layout
    scene_dir = os.path.join(output_dir, file.split('.')[0])
    os.mkdir(scene_dir)

    # Load the object specifying versions of the scene layout and viewpoints at which to sample it
    with open(os.path.join(data_dir, file), 'rb') as f:
        scene_samples = pickle.load(f)

    # For each version of the scene layout
    for scene_idx, scene in enumerate(scene_samples.scenes):
        build_scene(scene)

        # For each sampling viewpoint
        for view_idx, viewpoint in enumerate(scene_samples.viewpoints):
            render_name = 's=%d,v=%d.png' % (scene_idx, view_idx)
            render_viewpoint(viewpoint, os.path.join(scene_dir, render_name))

        clear_scene()
    break

# bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
# bpy.ops.wm.open_mainfile(filepath=bpy.data.filepath)

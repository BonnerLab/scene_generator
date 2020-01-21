import os, sys, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
import bpy
from math import pi
import pickle
from data_classes.Orientation import Orientation

texture_dir = 'textures'

# Load textures and make materials from them
texture_images = os.listdir(os.path.join(currentdir, texture_dir))
texture_images = [img for img in texture_images if img != '.DS_Store']
texture_images = sorted(texture_images)
texture_images = [os.path.join(currentdir, texture_dir, img) for img in texture_images]
up_materials = []
front_materials = []
right_materials = []


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


def place_surfaces(floor, ceiling, walls, scale, h_scale):
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


def place_lights(lights, scale, h_scale):
    for i, l in enumerate(lights):
        p, b, r = l.location, l.intensity, l.radius
        bpy.ops.object.light_add(type='POINT', radius=0.1)
        light = bpy.context.active_object
        light.name = 'light_%d' % i
        light.location = (p.x * scale, p.y * scale, p.z * h_scale)
        light.data.energy = 100 * b
        light.data.shadow_soft_size = r


def place_objects(objects, scale, h_scale):
    # todo: add objects
    pass


def reset_scene():
    bpy.ops.wm.read_homefile(filepath='scene_generation.blend')

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
        materials.clear()
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


def build_scene(scene, scale, h_scale):
    reset_scene()
    place_surfaces(scene.floor, scene.ceiling, scene.walls, scale, h_scale)
    place_lights(scene.lights, scale, h_scale)
    place_objects(scene.objects, scale, h_scale)


#####################################################
################## Scene building ###################
#####################################################


if __name__ == '__main__':
    assert len(sys.argv) == 7

    scale = 1 / 2.5
    h_scale = 1.25

    scene_file = sys.argv[6]

    with open(scene_file, 'rb') as f:
        scene = pickle.load(f).scenes[0]

    build_scene(scene, scale, h_scale)

    bpy.ops.wm.save_as_mainfile(filepath=scene_file.replace('.pkl', '.blend'))

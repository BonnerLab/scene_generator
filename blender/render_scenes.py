# Run in terminal with: blender -b scene_generation.blend -P render_scenes.py -- [args]
import os, sys, inspect, shutil
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
import bpy
from math import pi
import pickle
import numpy as np
from blender.build_scene import build_scene


def render_viewpoint(viewpoint, save_path, scale, h_scale):
    # Place the camera at the rendering viewpoint
    camera = bpy.data.objects['Camera']
    p, r, h = viewpoint.location, viewpoint.rotation, viewpoint.horizon
    camera.location = (p.x * scale, p.y * scale, p.z * h_scale)
    camera.rotation_euler = ((h + 90) * pi / 180, 0, (r - 90) * pi / 180)

    # Render the scene at the viewpoint
    bpy.context.scene.render.filepath = save_path
    bpy.ops.render.render(write_still=True)


def normalize_locations(data_dir):
    """
    Utility function to run on the dataset before any training
    in order to normalize the viewpoint locations to range (-1, 1)
    :param data_dir:
    """
    output_dir = os.path.join(data_dir, 'renderings')
    scenes = os.listdir(output_dir)
    scenes = [s for s in scenes if s != '.DS_Store']
    scenes = [os.path.join(output_dir, s) for s in scenes]
    viewpoints = [os.path.join(s, 'viewpoints.npy') for s in scenes]
    max_range = 0
    for path in viewpoints:
        viewpoint = np.load(path)
        r = np.fabs(viewpoint[:, 0:2]).max()
        if r > max_range:
            max_range = r
    for path in viewpoints:
        viewpoint = np.load(path)
        viewpoint[:, 0:2] = viewpoint[:, 0:2] / max_range
        np.save(path, viewpoint)
    np.save(os.path.join(data_dir, 'scale_factor.npy'), max_range)


#####################################################
################## Scene rendering ##################
#####################################################

if __name__ == '__main__':
    assert len(sys.argv) == 7 or len(sys.argv) == 9

    scale = 1 / 2.5
    h_scale = 1.25

    data_dir = sys.argv[6]
    output_dir = os.path.join(data_dir, 'renderings')
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    scene_files = os.listdir(data_dir)
    scene_files = [f for f in scene_files if '.pkl' in f]
    scene_files = sorted(scene_files)

    # Batch rendering
    if len(sys.argv) > 7:
        start_index, num_renders = sys.argv[7:9]
        start_index = int(start_index)
        end_index = start_index + int(num_renders)
        scene_files = scene_files[start_index:end_index]

    # For every scene layout
    for file in scene_files:
        # Prepare the output rendering directory for the scene layout
        scene_dir = os.path.join(output_dir, file.split('.')[0])
        shutil.rmtree(scene_dir, ignore_errors=True)
        os.mkdir(scene_dir)

        # Load the object specifying versions of the scene layout and viewpoints at which to sample it
        with open(os.path.join(data_dir, file), 'rb') as f:
            scene_samples = pickle.load(f)

        # For each version of the scene layout
        for scene_idx, scene in enumerate(scene_samples.scenes):
            build_scene(scene, scale, h_scale)

            # Render the scene from each viewpoint
            viewpoints_array = []
            for view_idx, viewpoint in enumerate(scene_samples.viewpoints):
                render_name = 's={:05d},v={:05d}.jpg'.format(scene_idx, view_idx)
                render_viewpoint(viewpoint, os.path.join(scene_dir, render_name), scale, h_scale)
                viewpoints_array.append([viewpoint.location.x - scene.floor_plan.shape[0] / 2,
                                         viewpoint.location.y - scene.floor_plan.shape[1] / 2,
                                         viewpoint.rotation * pi / 180, viewpoint.horizon * pi / 180])

            # Save the rendered data
            viewpoints_array = np.array(viewpoints_array, dtype=np.float32)
            np.save(os.path.join(scene_dir, 'viewpoints.npy'), viewpoints_array)

    # normalize_locations(data_dir)

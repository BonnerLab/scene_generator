import json
import pickle
import os
import shutil
from argparse import ArgumentParser
import numpy as np
from tqdm import tqdm
import random
random.seed(27)
from PIL import Image
from data_classes.SceneSamples import SceneSamples
from generators.layout import random_scene
from generators.textures import random_textures
from generators.lighting import random_lighting, grid_lighting
from generators.objects import random_objects
from generators.viewpoints import random_viewpoints


def get_centre_fixation(scene):
    points = np.array(scene.navigable_points(include_objects=False))
    fixation = [(np.min(points[:, 0]) + np.max(points[:, 0])) / 2,
              (np.min(points[:, 1]) + np.max(points[:, 1])) / 2]
    return fixation


def get_outward_fixation(scene):
    x_max, y_max = scene.floor_plan.shape
    edge_points = [(x, 0) for x in range(x_max + 1)] + \
                  [(0, y) for y in range(y_max + 1)] + \
                  [(x, y_max) for x in range(x_max + 1)] + \
                  [(x_max, y) for y in range(y_max + 1)]
    fixation = random.sample(edge_points, 1)[0]
    return fixation

parser = ArgumentParser(description='Generative Query Network training')
parser.add_argument('--config_file', required=True, type=str, help='path to the configuration file')
parser.add_argument('--save_dir', required=True, type=str, help='path to save the generated scenes')
parser.add_argument('--num_scenes', default=1000, type=int, help='number of scenes to generate')
args = parser.parse_args()

shutil.rmtree(args.save_dir, ignore_errors=True)
os.mkdir(args.save_dir)

with open(args.config_file) as f:
    config = json.loads(f.read())

if 'centre' in config['viewpoints']:
    centre_or_edge = config['viewpoints']['centre']
    if centre_or_edge:
        centre_views = True
        outward_views = False
    else:
        centre_views = False
        outward_views = True
    del config['viewpoints']['centre']
else:
    centre_views = False
    outward_views = False

grid_light = config['lighting']['grid']
del config['lighting']['grid']

demo_floor_plans = []
for i in tqdm(range(args.num_scenes)):
    scene = random_scene(**config['layout'])
    scene = random_textures(scene, **config['textures'])
    scene = random_objects(scene, **config['objects'])

    if grid_light:
        scene = grid_lighting(scene, **config['lighting'])
    else:
        scene = random_lighting(scene, **config['lighting'])

    if centre_views:
        fixation = get_centre_fixation(scene)
    elif outward_views:
        fixation = get_outward_fixation(scene)
    else:
        fixation = None
    viewpoints = random_viewpoints(scene, fixation=fixation, **config['viewpoints'])

    scene_sample = SceneSamples([scene], viewpoints)
    with open(os.path.join(args.save_dir, '{:07d}.pkl'.format(i)), 'wb') as f:
        pickle.dump(scene_sample, f)
    if i < 16:
        demo_floor_plans.append(scene_sample.visualize())

grid = Image.new('RGB', (500 * 4, 500 * 4))
for i in range(0, 4 * 500, 500):
    for j in range(0, 4 * 500, 500):
        fp = demo_floor_plans.pop(0)
        grid.paste(fp, (i, j))
grid.save(os.path.join(args.save_dir, 'samples.png'))

import json
import pickle
import os
import shutil
from argparse import ArgumentParser
import numpy as np
import random
random.seed(27)
from PIL import Image
from data_classes.SceneSamples import SceneSamples
from generators.layout import random_scene
from generators.textures import random_textures
from generators.lighting import random_lighting
from generators.objects import random_objects
from generators.viewpoints import random_viewpoints

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
    centre_views = config['viewpoints']['centre']
    del config['viewpoints']['centre']
else:
    centre_views = False

demo_floor_plans = []
for i in range(args.num_scenes):
    scene = random_scene(**config['layout'])
    scene = random_textures(scene, **config['textures'])
    scene = random_lighting(scene, **config['lighting'])
    scene = random_objects(scene, **config['objects'])

    if centre_views:
        points = np.array(scene.navigable_points(include_objects=False))
        centre = [(np.min(points[:, 0]) + np.max(points[:, 0])) / 2,
                  (np.min(points[:, 1]) + np.max(points[:, 1])) / 2]
    else:
        centre = None
    viewpoints = random_viewpoints(scene, centre=centre, **config['viewpoints'])

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

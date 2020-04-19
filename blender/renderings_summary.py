import os
from argparse import ArgumentParser
from PIL import Image

w, h = 480, 270


def scene_grid(dir):
    grid = Image.new('RGB', (480*2 + 5*1, 270*3 + 5*2))
    images = os.listdir(dir)
    images = [i for i in images if '.jpg' in i]
    images = sorted(images)
    images = [os.path.join(dir, i) for i in images]
    images = [Image.open(i) for i in images]
    for i in range(2):
        for j in range(3):
            image = images.pop(0)
            grid.paste(image, (i * w + i * 5, j * h + j * 5))
    return grid


parser = ArgumentParser(description='Generate a summary image of renderings from multiple scenes')
parser.add_argument('--data_dir', required=True, type=str, help='path to the generated scenes')
args = parser.parse_args()

assert os.path.exists(os.path.join(args.data_dir, 'renderings'))

scenes = os.listdir(os.path.join(args.data_dir, 'renderings'))
scenes = [s for s in scenes if s != '.DS_Store']
scenes = [os.path.join(args.data_dir, 'renderings', s) for s in scenes]
scenes = sorted(scenes)
scenes = scenes[:16]

scene_samples = [scene_grid(s) for s in scenes]
summary_grid = Image.new('RGB', (scene_samples[0].width * 4 + 5 * 30,
                                 scene_samples[0].height * 4 + 5 * 30))

for i in range(4):
    for j in range(4):
        summary_grid.paste(scene_samples[i * 4 + j],
                           (i * scene_samples[0].width + (i + 1) * 30,
                            j * scene_samples[0].height + (j + 1) * 30))

summary_grid.save(os.path.join(args.data_dir, 'samples_rendering.png'))

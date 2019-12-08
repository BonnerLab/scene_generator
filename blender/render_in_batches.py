import os
import sys

assert len(sys.argv) == 4

blender_path, data_dir, batch_size = sys.argv[1:4]
batch_size = int(batch_size)

scene_files = os.listdir(data_dir)
scene_files = [f for f in scene_files if '.pkl' in f]
num_scenes = len(scene_files)

print('NUM BATCHES TO RENDER: {}'.format(num_scenes // batch_size))
for i, start_index in enumerate(range(0, num_scenes, batch_size)):
    print('RENDERING BATCH {}'.format(i))
    os.system('sh render_batch.sh {} {} {} {}'.format(blender_path, data_dir, start_index, batch_size))

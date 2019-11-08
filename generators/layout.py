import numpy as np
import random
from data_classes.Scene import Scene
from data_classes.Orientation import Orientation


def random_scene(min_patches=3, max_patches=5, min_patch_size=(8, 8), max_patch_size=(20, 20), canvas_size=100):
    assert min_patch_size[0] % 4 == 0 and min_patch_size[1] % 4 == 0
    assert max_patch_size[0] % 4 == 0 and max_patch_size[1] % 4 == 0

    floor_plan = np.zeros((canvas_size, canvas_size), dtype=np.bool)
    n_patches = random.randint(min_patches, max_patches)
    patches_succeeded = 0

    # Place a seed patch in the centre
    patch_size = (max_patch_size[0], max_patch_size[1])
    if random.random():
        patch_size = (patch_size[1], patch_size[0])
    floor_plan[canvas_size // 2 - patch_size[0] // 2: canvas_size // 2 + patch_size[0] // 2,
               canvas_size // 2 - patch_size[1] // 2: canvas_size // 2 + patch_size[1] // 2] = True
    patches_succeeded += 1

    while patches_succeeded < n_patches:
        patch_size = (random.randint(min_patch_size[0] // 4, max_patch_size[0] // 4),
                      random.randint(min_patch_size[1] // 4, max_patch_size[1] // 4))
        if random.random():
            patch_size = (patch_size[1], patch_size[0])
        patch_size = np.array(patch_size) * 4

        # Try and slide the patch into the existing floor plan from a random direction
        direction = random.sample([Orientation.LEFT, Orientation.FRONT, Orientation.RIGHT, Orientation.BACK], 1)[0]
        if direction == Orientation.LEFT:
            increment = np.array([-2, 0])
            start = np.array([canvas_size - patch_size[0], random.randint(0, (canvas_size - patch_size[1]) // 2) * 2])
        elif direction == Orientation.FRONT:
            increment = np.array([0, 2])
            start = np.array([random.randint(0, (canvas_size - patch_size[0]) // 2) * 2, 0])
        elif direction == Orientation.RIGHT:
            increment = np.array([2, 0])
            start = np.array([0, random.randint(0, (canvas_size - patch_size[1]) // 2) * 2])
        else:
            increment = np.array([0, -2])
            start = np.array([random.randint(0, (canvas_size - patch_size[0]) // 2) * 2, canvas_size - patch_size[1]])

        while not out_of_bounds(start, patch_size, canvas_size):
            if valid_placement(start, patch_size, floor_plan):
                floor_plan[start[0]:start[0] + patch_size[0], start[1]:start[1] + patch_size[1]] = True
                patches_succeeded += 1
                break
            else:
                start = start + increment

    return Scene(floor_plan)


def valid_placement(start_corner, patch_size, floor_plan):
    # Check if half of the patch on either dimension fully overlaps with the floor
    if (floor_plan[start_corner[0]:start_corner[0] + patch_size[0] // 2,                        # Left half
        start_corner[1]:start_corner[1] + patch_size[1]]).all() or \
            (floor_plan[start_corner[0] + patch_size[0] // 2:start_corner[0] + patch_size[0],  # Right half
             start_corner[1]:start_corner[1] + patch_size[1]]).all() or \
            (floor_plan[start_corner[0]:start_corner[0] + patch_size[0],                        # Front half
             start_corner[1] + patch_size[1] // 2:start_corner[1] + patch_size[1]]).all() or \
            (floor_plan[start_corner[0]:start_corner[0] + patch_size[0],                        # Back half
             start_corner[1]:start_corner[1] + patch_size[1] // 2]).all():
        return True
    return False


def out_of_bounds(start_corner, patch_size, canvas_size):
    if (start_corner < 0).any():
        return True
    if (start_corner + patch_size > canvas_size).any():
        return True
    return False

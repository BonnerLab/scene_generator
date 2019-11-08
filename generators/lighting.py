import random
import numpy as np
from data_classes.Light import Light
from data_classes.Point import Point


def random_lighting(scene, tiles_to_light_range=(80, 100), min_padding=5, intensity_range=(0.75, 1.0)):
    scene = scene.copy()
    tiles_to_light = random.randint(*tiles_to_light_range)
    n_lights = scene.floor_plan.sum() // tiles_to_light
    lights_succeeded = 0
    locations_available = scene.navigable_points(include_objects=False)
    random.shuffle(locations_available)
    placed = np.zeros_like(scene.floor_plan, dtype=np.bool)
    while lights_succeeded < n_lights and len(locations_available) > 0:
        x, y = locations_available.pop()
        if placed[max(x - min_padding + 1, 0):min(x + min_padding, placed.shape[0]),
                  max(y - min_padding + 1, 0):min(y + min_padding, placed.shape[1])].any():
            continue
        intensity = random.uniform(*intensity_range)
        light = Light(Point(x, y, 1.75), intensity)
        scene.add_light(light)
        placed[x, y] = True
        lights_succeeded += 1
    return scene

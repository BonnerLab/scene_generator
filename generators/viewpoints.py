import random
import numpy as np
import math
from data_classes.Viewpoint import Viewpoint
from data_classes.Point import Point


def random_viewpoints(scene, num_views=5, min_view_padding=5, min_boundary_padding=1,
                      height=1.0, max_horizon_offset=20, centre=None, max_centre_offset=20):
    viewpoints = []
    viewpoints_succeeded = 0
    locations_available = scene.navigable_points()
    random.shuffle(locations_available)
    placed = np.zeros_like(scene.object_floor_plan, dtype=np.bool)
    boundaries = (scene.object_floor_plan == False)
    while viewpoints_succeeded < num_views and len(locations_available) > 0:
        x, y = locations_available.pop()
        if placed[max(x - min_view_padding + 1, 0):min(x + min_view_padding, placed.shape[0]),
           max(y - min_view_padding + 1, 0):min(y + min_view_padding, placed.shape[1])].any():
            continue
        if boundaries[max(x - min_boundary_padding + 1, 0):min(x + min_boundary_padding, boundaries.shape[0]),
           max(y - min_boundary_padding + 1, 0):min(y + min_boundary_padding, boundaries.shape[1])].any():
            continue
        h = random.uniform(-max_horizon_offset, 0)
        if centre is not None:
            offset = random.uniform(-max_centre_offset, max_centre_offset)
            r = math.atan2(centre[1] - y, centre[0] - x) * 180 / math.pi + offset
        else:
            focus = random.sample(scene.navigable_points(include_objects=False), 1)[0]
            r = math.atan2(focus[1] - y, focus[0] - x) * 180 / math.pi
        v = Viewpoint(Point(x, y, height), rotation=r, horizon=h)
        viewpoints.append(v)
        placed[x, y] = True
        viewpoints_succeeded += 1
    return viewpoints

import random
import math
from data_classes.Viewpoint import Viewpoint
from data_classes.Point import Point


def random_viewpoints(scene, num_views, min_padding=1, height_range=(1.0, 1.0), max_horizon_offset=15,
                      centre=None, max_centre_offset=15):
    # todo: test
    viewpoints = []
    locations_available = scene.navigable_points()
    fp = scene.object_floor_plan
    for l in locations_available:
        if not fp[max(l[0] - min_padding, 0):min(l[0] + min_padding, fp.shape[0]),
                  max(l[1] - min_padding, 0):min(l[1] + min_padding, fp.shape[1])].all():
            _ = locations_available.pop()
    random.shuffle(locations_available)
    for _ in range(num_views):
        x, y = locations_available.pop()
        z = random.uniform(*height_range)
        h = random.uniform(-max_horizon_offset, max_horizon_offset)
        if centre is not None:
            offset = random.uniform(-max_centre_offset, max_centre_offset)
            r = math.atan2(centre[1] - y, centre[0] - x) * 180 / math.pi + offset
        else:
            focus = random.sample(scene.navigable_points(include_objects=False), 1)
            r = math.atan2(focus[1] - y, focus[0] - x) * 180 / math.pi
        v = Viewpoint(Point(x, y, z), rotation=r, horizon=h)
        viewpoints.append(v)
    return viewpoints

import random
from copy import deepcopy
import numpy as np
from PIL import Image
from data_classes.Point import Point
from data_classes.Object import Object
from data_classes.Surface import Surface
from data_classes.Orientation import Orientation


class Scene:

    def __init__(self, floor_plan: np.ndarray):
        floor_plan = deepcopy(floor_plan)
        floor_plan = Scene.squeeze_floor_plan(floor_plan)
        self.floor_plan = floor_plan
        self.object_floor_plan = floor_plan.copy()
        self.floor, self.ceiling, self.walls = Scene.make_surfaces(floor_plan)
        self.objects = []
        self.lights = []

    def navigable_points(self):
        return np.argwhere(self.object_floor_plan).tolist()

    def add_random_object(self, type, size):
        rotation = random.choice([Orientation.LEFT, Orientation.FRONT, Orientation.RIGHT, Orientation.BACK])
        object = Object(type, Point(0, 0, 0), rotation, size)
        candidate_positions = self.navigable_points()
        random.shuffle(candidate_positions)
        for x, y in candidate_positions:
            object.position = Point(x, y, 0)
            if self.add_object(object):
                return True
        return False

    def add_object(self, object: Object):
        if not self.fits(object):
            return False
        self.objects.append(object)
        sx, sy = object.size
        if object.rotation in [Orientation.FRONT, Orientation.BACK]:
            sx, sy = sy, sx
        for x in range(object.position.x - sx // 2, object.position.x + sx // 2):
            for y in range(object.position.y - sy // 2, object.position.y + sy // 2):
                self.object_floor_plan[x, y] = False

        return True

    def add_light(self, light):
        self.lights.append(light)

    def fits(self, object: Object):
        sx, sy = object.size
        if object.rotation in [Orientation.FRONT, Orientation.BACK]:
            sx, sy = sy, sx
        for x in range(object.position.x - sx // 2, object.position.x + sx // 2):
            for y in range(object.position.y - sy // 2, object.position.y + sy // 2):
                if not self.object_floor_plan[x, y]:
                    return False
        return True

    def visualize_floor_plan(self, with_objects=False):
        floor_plan = self.object_floor_plan if with_objects else self.floor_plan
        image = floor_plan.astype(np.uint8)
        image = image * 255
        image = Image.fromarray(image)
        width, height = image.width, image.height
        if width > height:
            new_width, new_height = 500, int(500 * height/width)
        else:
            new_width, new_height = int(500 * width/height), 500
        image = image.resize((new_width, new_height))
        image.show()

    @classmethod
    def squeeze_floor_plan(cls, floor_plan):
        x_min = 0
        while not np.any(floor_plan[x_min, :]):
            x_min += 1
        x_max = floor_plan.shape[0] - 1
        while not np.any(floor_plan[x_max, :]):
            x_max -= 1
        y_min = 0
        while not np.any(floor_plan[:, y_min]):
            y_min += 1
        y_max = floor_plan.shape[1] - 1
        while not np.any(floor_plan[:, y_max]):
            y_max -= 1
        floor_plan = floor_plan[x_min - 1:x_max + 2, y_min - 1:y_max + 2]
        return floor_plan

    @classmethod
    def make_surfaces(cls, floor_plan):
        floor = Surface(0, centre=Point(floor_plan.shape[0] // 2, floor_plan.shape[1] // 2, 0),
                        normal=Orientation.UP, size=(floor_plan.shape[0] - 2, floor_plan.shape[1] - 2))
        ceiling = Surface(0, centre=Point(floor_plan.shape[0] // 2, floor_plan.shape[1] // 2, 2),
                          normal=Orientation.DOWN, size=(floor_plan.shape[0] - 2, floor_plan.shape[1] - 2))

        # Find first corner at the top left
        x_global_start, y_global_start = 1, 1
        while not floor_plan[x_global_start, y_global_start]:
            x_global_start += 1
        x_start, y_start = x_global_start, y_global_start
        direction = Orientation.FRONT

        walls = []
        while True:
            x, y = x_start, y_start

            if direction == Orientation.FRONT:
                while not floor_plan[x - 1, y] and floor_plan[x, y]:
                    y += 1
                x_end, y_end = x, y
                walls.append(Surface(0, centre=Point(x, y_start + (y_end - y_start) // 2, 1),
                                     normal=Orientation.RIGHT, size=(y_end - y_start, 2)))
                x_start, y_start = x, y
                if floor_plan[x - 1, y]:
                    direction = Orientation.LEFT
                else:
                    direction = Orientation.RIGHT

            elif direction == Orientation.LEFT:
                while not floor_plan[x - 1, y - 1] and floor_plan[x - 1, y]:
                    x -= 1
                x_end, y_end = x, y
                walls.append(Surface(0, centre=Point(x_start - (x_start - x_end) // 2, y, 1),
                                     normal=Orientation.FRONT, size=(x_start - x_end, 2)))
                x_start, y_start = x, y
                if floor_plan[x - 1, y - 1]:
                    direction = Orientation.BACK
                else:
                    direction = Orientation.FRONT

            elif direction == Orientation.BACK:
                while not floor_plan[x, y - 1] and floor_plan[x - 1, y - 1]:
                    y -= 1
                x_end, y_end = x, y
                walls.append(Surface(0, centre=Point(x, y_start - (y_start - y_end) // 2, 1),
                                     normal=Orientation.LEFT, size=(y_start - y_end, 2)))
                x_start, y_start = x, y
                if floor_plan[x, y - 1]:
                    direction = Orientation.RIGHT
                else:
                    direction = Orientation.LEFT

            else:
                while not floor_plan[x, y] and floor_plan[x, y - 1]:
                    x += 1
                x_end, y_end = x, y
                walls.append(Surface(0, centre=Point(x_start + (x_end - x_start) // 2, y, 1),
                                     normal=Orientation.BACK, size=(x_end - x_start, 2)))
                x_start, y_start = x, y
                if floor_plan[x, y]:
                    direction = Orientation.FRONT
                else:
                    direction = Orientation.BACK

            if (x_start, y_start) == (x_global_start, y_global_start) and direction == Orientation.FRONT:
                break

        return floor, ceiling, walls

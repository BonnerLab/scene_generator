from data_classes.Point import Point


class Light:

    def __init__(self, position: Point, direction: Point, intensity: int):
        self.position = position
        self.direction = direction
        self.intensity = intensity

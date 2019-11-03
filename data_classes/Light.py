from data_classes.Point import Point


class Light:

    def __init__(self, position: Point, intensity: int):
        self.position = position
        self.intensity = intensity

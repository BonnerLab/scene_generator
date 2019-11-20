from data_classes.Point import Point


class Light:

    def __init__(self, location: Point, intensity: float, radius: float):
        self.location = location
        self.intensity = intensity
        self.radius = radius

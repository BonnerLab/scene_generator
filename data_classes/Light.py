from data_classes.Point import Point


class Light:

    def __init__(self, location: Point, intensity: float):
        self.location = location
        self.intensity = intensity

from data_classes.Point import Point


class Viewpoint:

    def __init__(self, location: Point, rotation: Point):
        self.location = location
        self.rotation = rotation

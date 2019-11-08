from typing import List
from data_classes.Scene import Scene
from data_classes.Viewpoint import Viewpoint


class SceneSamples:

    def __init__(self, scenes: List[Scene], viewpoints: List[Viewpoint]):
        self.scenes = scenes
        self.viewpoints = viewpoints

    def visualize_viewpoints(self):
        # todo: plot point and arrow for every location and rotation of viewpoints on top of the floor plan
        pass

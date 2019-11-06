from typing import List
from data_classes.Scene import Scene
from data_classes.Viewpoint import Viewpoint


class SceneSamples:

    def __init__(self, scenes: List[Scene], viewpoints: List[Viewpoint]):
        self.scenes = scenes
        self.viewpoints = viewpoints

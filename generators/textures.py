import random


def random_textures(scene, floor_range=(0, 0), ceiling_range=(0, 0), wall_range=(0, 0)):
    scene = scene.copy()
    scene.floor.type = random.randint(*floor_range)
    scene.ceiling.type = random.randint(*ceiling_range)
    for w in scene.walls:
        w.type = random.randint(*wall_range)
    return scene


def fixed_textures(scene, floor=0, ceiling=0, wall=0):
    scene = scene.copy()
    scene.floor.type = floor
    scene.ceiling.type = ceiling
    for w in scene.walls:
        w.type = wall
    return scene

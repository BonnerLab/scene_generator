import random


def random_objects(scene, object_ranges, sizes):
    assert len(object_ranges) == len(sizes)
    scene = scene.copy()
    objects = []
    for type, type_range in enumerate(object_ranges):
        objects += [type for _ in range(random.randint(*type_range))]
    random.shuffle(objects)
    for type in objects:
        size = sizes[type]
        _ = scene.randomly_place_object(type, size)
    return scene

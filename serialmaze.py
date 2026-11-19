from app.services.content_service import ContentService
from app.services.meatfighter_maze_generator import MeatFighterMazeGenerator

generator = MeatFighterMazeGenerator()
original = generator.generate()

serialized = ContentService._serialize_maze(original)
restored = ContentService.restore_maze(serialized)

assert original.width == restored.width
assert original.height == restored.height
assert len(original.solution) == len(restored.solution)

for original_node, restored_node in zip(
    original.all_nodes(),
    restored.all_nodes(),
):
    for direction in ContentService.NODE_DIRECTIONS:
        original_target = getattr(original_node, direction)
        restored_target = getattr(restored_node, direction)

        original_id = (
            ContentService._node_id(original_target)
            if original_target else None
        )
        restored_id = (
            ContentService._node_id(restored_target)
            if restored_target else None
        )

        assert original_id == restored_id

assert [
    ContentService._node_id(node) for node in original.solution
] == [
    ContentService._node_id(node) for node in restored.solution
]

assert ContentService._node_id(original.start) == ContentService._node_id(restored.start)
assert ContentService._node_id(original.finish) == ContentService._node_id(restored.finish)

print("MAZE SERIALIZATION TEST: PASSED")
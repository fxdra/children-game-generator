from erbsland_maze import (
    SvgSetup,
    SvgLayout,
    GeneratorSetup,
    Generator,
    PathEnd,
    Placement,
)


svg_setup = SvgSetup(
    width=180.0,
    height=240.0,
    side_length=12.0,
)

generator_setup = GeneratorSetup(
    path_ends=[
        PathEnd(
            Placement.TOP_LEFT,
            name="START",
        ),
        PathEnd(
            Placement.BOTTOM_RIGHT,
            name="FINISH",
        ),
    ],
    verbose=True,
)

svg_layout = SvgLayout(svg_setup)

generator = Generator(
    svg_layout,
    generator_setup,
)


print("\n=== 1. PREPARE ROOMS ===")
generator.prepare_rooms()


print("\n=== 2. PREPARE PATH ENDS ===")
generator._prepare_path_ends()

print(
    "Path end rooms:",
    len(generator.path_end_rooms),
)

for room in generator.path_end_rooms:
    print(
        "Endpoint:",
        room.location,
        "type:",
        room.type,
    )


print("\n=== 3. GENERATE MAZE ===")
generator.generate_maze()


print("\n=== 4. FINAL ROOM GRID ===")
rooms = generator.room_grid.get_all_rooms()
connections = generator.room_grid.get_all_connections()

print("Rooms:", len(rooms))
print("Connections:", len(connections))


print("\n=== 5. CONNECTION STATUS ===")

closed = 0
open_connections = 0

for connection in connections:
    if connection.is_closed:
        closed += 1
    else:
        open_connections += 1

print("Closed:", closed)
print("Open:", open_connections)
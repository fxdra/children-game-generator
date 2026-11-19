from erbsland_maze import (
    Generator,
    GeneratorSetup,
    PathEnd,
    Placement,
    SvgLayout,
    SvgSetup,
)


class MazeGenerator:
    def __init__(
        self,
        width_mm: float = 180.0,
        height_mm: float = 240.0,
        side_length_mm: float = 12.0,
    ):
        self.width_mm = float(width_mm)
        self.height_mm = float(height_mm)
        self.side_length_mm = float(side_length_mm)

        self.generator = None

    def generate(self):
        svg_setup = SvgSetup(
            width=self.width_mm,
            height=self.height_mm,
            side_length=self.side_length_mm,
        )

        svg_layout = SvgLayout(svg_setup)

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
            verbose=False,
        )

        self.generator = Generator(
            svg_layout,
            generator_setup,
        )

        self.generator.prepare_rooms()
        self.generator.generate_maze()
        self.generator.connect_longest_path()
        self.generator.verify_maze()

        return self.generator

    def get_room_grid(self):
        if self.generator is None:
            raise RuntimeError(
                "Maze belum dibuat. Panggil generate() terlebih dahulu."
            )

        return self.generator.room_grid

    def get_start_room(self):
        if self.generator is None:
            raise RuntimeError(
                "Maze belum dibuat. Panggil generate() terlebih dahulu."
            )

        return self.generator.path_end_rooms[0]

    def get_finish_room(self):
        if self.generator is None:
            raise RuntimeError(
                "Maze belum dibuat. Panggil generate() terlebih dahulu."
            )

        return self.generator.path_end_rooms[1]
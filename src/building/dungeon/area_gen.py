from gdpc import Editor
from gdpc import WorldSlice
from gdpc.vector_tools import Rect
import time

lobby_x = 50
lobby_y = 0
lobby_z = 50
lobby_width_1 = 120
lobby_width_2 = 120
lobby_height = 12


def wall_generate(editor: Editor, x_corner, y_height, z_corner, width_1, width_2, height):
    cube_generate(editor, x_corner, y_height, z_corner, width_1, width_2, height)
    cube_generate(editor, x_corner + 1, y_height + 1, z_corner + 1, width_1 - 2, width_2 - 2, height - 1)
    no_border_cube_generate(editor, x_corner, y_height + height, z_corner, width_1, width_2, height, "air")
    for i in range(0, width_1 + 1):
        if i % 2 == 0:
            editor.runCommand(f"setblock {x_corner + i} {y_height + height} {z_corner} stone_bricks")
            editor.runCommand(f"setblock {x_corner} {y_height + height} {z_corner + i} stone_bricks")
            editor.runCommand(f"setblock {x_corner + width_1} {y_height + height} {z_corner + i} stone_bricks")
            editor.runCommand(f"setblock {x_corner + i} {y_height + height} {z_corner + width_1} stone_bricks")
            print(f"setblock {x_corner + i} {y_height + height} {z_corner} stone_bricks")


def cube_generate(editor: Editor, x_corner, y_height, z_corner, width_1, width_2, height):
    for i in range(0, height):
        editor.runCommand(
            f"fill {x_corner} {y_height + i} {z_corner} {x_corner + width_1} {y_height + i + 1} {z_corner + width_2} stone_bricks")
        editor.flushBuffer()
    for i in range(1, height - 1):
        editor.runCommand(
            f"fill {x_corner + 1} {y_height + i} {z_corner + 1} {x_corner + width_1 - 1} {y_height + i + 1} {z_corner + width_2 - 1} air")
        editor.flushBuffer()


def no_border_cube_generate(editor: Editor, x_corner, y_height, z_corner, width_1, width_2, height,
                            material="stone_bricks"):
    for i in range(0, height):
        editor.runCommand(
            f"fill {x_corner} {y_height + i} {z_corner} {x_corner + width_1} {y_height + i + 1} {z_corner + width_2} {material}")
        editor.flushBuffer()


def lobby_generate(editor: Editor, x_corner, y_height, z_corner, width_1, width_2, height):
    cube_generate(editor, x_corner - 3, y_height, z_corner - 3, width_1 + 6, width_2 + 6, height * 2 + 1)
    wall_generate(editor, lobby_x, lobby_y, lobby_z, lobby_width_1, lobby_width_2, lobby_height)


def get_height(worldSlice: WorldSlice, x, z):
    """
    Get the height of the worldSlice at the given x and z coordinates.
    """
    buildArea = editor.getBuildArea()
    print("Loading world slice...")
    worldSlice = editor.loadWorldSlice(buildArea.toRect(), cache=True)
    print("World slice loaded")

    area = Rect(size=worldSlice.rect.size)
    shape = area.size.to_tuple()
    heightMaps = worldSlice.heightmaps["MOTION_BLOCKING_NO_LEAVES"]
    for x, z in area.inner:
        y = heightMaps[x, z]
        print(f"({x}, {y}, {z})")
    return heightMaps


if __name__ == "__main__":
    editor = Editor()
    # height1 = get_height(editor.worldSlice, -87, 102)
    # print(height1)
    lobby_generate(editor, lobby_x, lobby_y, lobby_z, lobby_width_1, lobby_width_2, lobby_height)

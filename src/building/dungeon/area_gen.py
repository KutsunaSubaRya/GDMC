from gdpc import Editor
from gdpc import WorldSlice
from gdpc.vector_tools import Rect
from src.config.config import config

# import time
#
# lobby_x = config.lobby_x
# lobby_y = config.lobby_y
# lobby_z = config.lobby_z
# local_lobby_offset_x = config.local_lobby_offset_x
# local_lobby_offset_z = config.local_lobby_offset_z
# lobby_width_1 = config.lobby_width_1
# lobby_width_2 = config.lobby_width_2
# lobby_height = config.lobby_height
# build_area_start_x = config.build_area_start_x
# build_area_start_y = config.build_area_start_y
# build_area_start_z = config.build_area_start_z
# build_area_end_x = config.build_area_end_x
# build_area_end_y = config.build_area_end_y
# build_area_end_z = config.build_area_end_z


def wall_generate(editor: Editor, x_corner, y_height, z_corner, width_1, width_2, height):
    cube_generate(editor, x_corner, y_height, z_corner, width_1, width_2, height)
    cube_generate(editor, x_corner + 1, y_height + 1, z_corner + 1, width_1 - 2, width_2 - 2, height - 1)
    no_border_cube_generate(editor, x_corner, y_height + height, z_corner, width_1, width_2, height, "air")
    surface_generate(editor, x_corner + 2, y_height + 1, z_corner + 2, width_1 - 4, width_2 - 4)
    for i in range(0, width_1 + 1):
        if i % 2 == 0:
            editor.runCommand(f"setblock {x_corner + i} {y_height + height} {z_corner} stone_bricks")
            editor.runCommand(f"setblock {x_corner} {y_height + height} {z_corner + i} stone_bricks")
            editor.runCommand(f"setblock {x_corner + width_1} {y_height + height} {z_corner + i} stone_bricks")
            editor.runCommand(f"setblock {x_corner + i} {y_height + height} {z_corner + width_1} stone_bricks")
            print(f"setblock {x_corner + i} {y_height + height} {z_corner} stone_bricks")
            editor.runCommand(f"setblock {x_corner + i} {y_height + height + 1} {z_corner} lantern")
            editor.runCommand(f"setblock {x_corner} {y_height + height + 1} {z_corner + i} lantern")
            editor.runCommand(f"setblock {x_corner + width_1} {y_height + height + 1} {z_corner + i} lantern")
            editor.runCommand(f"setblock {x_corner + i} {y_height + height + 1} {z_corner + width_1} lantern")
            print(f"setblock {x_corner + i} {y_height + height + 1} {z_corner} lantern")
            for j in range(0, 2):
                editor.runCommand(f"setblock {x_corner + i} {y_height + height - 9 - j} {z_corner} air")
                editor.runCommand(f"setblock {x_corner} {y_height + height - 9 - j} {z_corner + i} air")
                editor.runCommand(f"setblock {x_corner + width_1} {y_height + height - 9 - j} {z_corner + i} air")
                editor.runCommand(f"setblock {x_corner + i} {y_height + height - 9 - j} {z_corner + width_1} air")
    for i in range(1, width_1):
        if i % 2 == 1:
            for j in range(0, 2):
                print("i", i)
                print("x_corner", x_corner)
                print("z_corner", z_corner)
                print("width_1", width_1)
                print("width_2", width_2)
                editor.runCommand(f"setblock {x_corner + i + 1} {y_height + height - 9 - j} {z_corner + 1} air")
                editor.runCommand(f"setblock {x_corner + 1} {y_height + height - 9 - j} {z_corner + i + 1} air")
                editor.runCommand(f"setblock {x_corner + width_1 - 1} {y_height + height - 9 - j} {z_corner + i + 1} air")
                editor.runCommand(f"setblock {x_corner + i + 1} {y_height + height - 9 - j} {z_corner + width_1 - 1} air")


def cube_generate(editor: Editor, x_corner, y_height, z_corner, width_1, width_2, height):
    for i in range(0, height):
        editor.runCommand(
            f"fill {x_corner} {y_height + i} {z_corner} {x_corner + width_1} {y_height + i + 1} {z_corner + width_2} stone_bricks")
        editor.flushBuffer()
    for i in range(1, height - 1):
        editor.runCommand(
            f"fill {x_corner + 1} {y_height + i} {z_corner + 1} {x_corner + width_1 - 1} {y_height + i + 1} {z_corner + width_2 - 1} air")
        editor.flushBuffer()


def cube_generate_from_middle(editor: Editor, x_corner, y_height, z_corner, width_1, width_2, height, size: int = 7, border_material="stone_bricks", inner_material="air"):
    sz = size//2

    for i in range(0, height):
        editor.runCommand(
            f"fill {x_corner - sz} {y_height + i} {z_corner - sz} {x_corner + width_1} {y_height + i + 1} {z_corner + width_2} {border_material}")
        editor.flushBuffer()
    for i in range(1, height - 1):
        editor.runCommand(
            f"fill {x_corner + 1 - sz} {y_height + i} {z_corner + 1 - sz} {x_corner + width_1 - 1} {y_height + i + 1} {z_corner + width_2 - 1} {inner_material}")
        editor.flushBuffer()


def no_border_cube_generate(editor: Editor, x_corner, y_height, z_corner, width_1, width_2, height,
                            material="stone_bricks"):
    for i in range(0, height):
        editor.runCommand(
            f"fill {x_corner} {y_height + i} {z_corner} {x_corner + width_1} {y_height + i + 1} {z_corner + width_2} {material}")
        editor.flushBuffer()


def surface_generate(editor: Editor, x_corner, y_height, z_corner, width_1, width_2, material="grass_block"):
    editor.runCommand(
        f"fill {x_corner} {y_height} {z_corner} {x_corner + width_1} {y_height} {z_corner + width_2} {material}")
    editor.flushBuffer()


def lobby_generate(editor: Editor, x_corner, y_height, z_corner, width_1, width_2, height):
    cube_generate(editor, x_corner - 3, y_height, z_corner - 3, width_1 + 6, width_2 + 6, height * 2 + 1)
    wall_generate(editor, x_corner, y_height, z_corner, width_1, width_2, height)

def get_block_height_and_info(worldSlice: WorldSlice, x, z):
    buildArea = editor.getBuildArea()
    print("Loading world slice...")
    worldSlice = editor.loadWorldSlice(buildArea.toRect(), cache=True)
    print("World slice loaded")

    area = Rect(size=worldSlice.rect.size)
    heightMaps = worldSlice.heightmaps["MOTION_BLOCKING_NO_LEAVES"]
    globalBound = buildArea.toRect()
    globalOffset = globalBound.offset

    height = heightMaps[x - globalOffset.x, z - globalOffset.y]
    print("height", height)

    block = worldSlice.getBlock((x - globalOffset.x, height - 1, z - globalOffset.y))
    print("block", block)


def surface_material_scattering(editor: Editor, x_corner, y_height, z_corner, width_1, width_2, material="sea_lantern"):
    # mod 4 to make sure the material is not too dense
    for i in range(0, width_1, 4):
        for j in range(0, width_2, 4):
            editor.runCommand(f"setblock {x_corner + i} {y_height} {z_corner + j} {material}")
        editor.flushBuffer()

if __name__ == "__main__":
    editor = Editor()
    get_block_height_and_info(editor.worldSlice, 5918, 5880)
    # lobby_generate(editor, lobby_x, lobby_y, lobby_z, lobby_width_1, lobby_width_2, lobby_height)

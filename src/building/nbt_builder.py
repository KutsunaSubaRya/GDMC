"""
1. absPath = getNBTAbsPath(name, type, level)
    - get the absolute path of the nbt file.
        - name, level can be found in src/building_util/building.py
        - type can be found in src/building_util/building_info.py
2. nbt_struct = nbt.NBTFile(absPath)
    - get the nbt structure.
3. buildFromStructureNBT(nbt_struct, baseX, baseY, baseZ, biome)
    - build the structure
    - biome default is "".
"""

from nbt import nbt as nbt
from gdpc import Editor, Block, Box, Rect
from gdpc.vector_tools import ivec3, dropY
from gdpc.geometry import placeCuboid
from ..resource.biome_substitute import changeBlock


def NBT2Str(struct: nbt.TAG):
    match struct:
        case nbt.TAG_Compound():
            return '{{{}}}'.format(
                ','.join(['{}:{}'.format(str(k), NBT2Str(v)) for k, v in struct.iteritems()]))
        case nbt.TAG_List():
            return '[{}]'.format(','.join([NBT2Str(x) for x in struct]))
        case nbt.TAG_String():
            return '"{}"'.format(str(struct))
        case nbt.TAG_Byte():
            return '{}b'.format(str(struct))
        case nbt.TAG_Float():
            return '{}f'.format(str(struct))
        case nbt.TAG_Double():
            return '{}d'.format(str(struct))
        case nbt.TAG_Int():
            return '{}'.format(str(struct))
        case nbt.TAG_Long():
            return '{}'.format(str(struct))


def NBT2Blocks(struct: nbt.NBTFile, offset: ivec3 = ivec3(0, 0, 0)):
    palatte = struct["palette"]
    for blk in struct["blocks"]:
        pos = ivec3(*map(lambda p: int(p.value), blk["pos"]))
        stateTag = palatte[blk["state"].value]
        if 'nbt' in blk:
            nbt = blk["nbt"]
        else:
            nbt = None
        block = Block.fromBlockStateTag(stateTag, nbt)
        yield pos + offset, block


def buildFromNBT(editor: Editor, struct: nbt.NBTFile, globalOffset: ivec3, localOffset: ivec3, material: str = "oak", keep=False):
    if editor.worldSlice is None:
        raise Exception("Error while building structure: worldSlice is None")

    globalCoordinate = globalOffset + localOffset

    size = getStructureSizeNBT(struct)
    bound = Box(globalCoordinate, size)

    if not keep:
        begin = bound.begin
        last = bound.last
        placeCuboid(editor, begin, last, Block("barrier"))

    # Fill basement
    rect = bound.toRect()
    worldSlice = editor.worldSlice
    height = worldSlice.heightmaps["MOTION_BLOCKING_NO_LEAVES"]
    for x, z in rect.inner:
        floory = height[x - globalOffset.x, z - globalOffset.z]
        placeCuboid(editor, ivec3(x, floory, z), ivec3(
            x, globalCoordinate.y, z), Block("cobblestone"))
    for pos, block in NBT2Blocks(struct, globalCoordinate):
        # FIXME: isChangeBlock and changeBlock function - SubaRya
        if material != "oak":
            blkString = changeBlock(material, block.id)
            block = Block(blkString, block.states, block.data)

        editor.placeBlock(pos, block)


def getStructureSizeNBT(struct: nbt.NBTFile) -> ivec3:
    size = struct["size"]
    return ivec3(*map(lambda x: int(x.value), size))

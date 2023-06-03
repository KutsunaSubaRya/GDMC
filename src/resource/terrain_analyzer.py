# for stone, log, food, iron "no amount of human"
# fix: add human transform - SubaRya
import numpy as np
from dataclasses import dataclass
from gdpc import WorldSlice
from gdpc.vector_tools import Rect, addY, ivec2

stoneSet = {"minecraft:andesite", "minecraft:basalt", "minecraft:cobblestone", "minecraft:mossy_cobblestone", "minecraft:mossy_stone_bricks", "minecraft:cracked_stone_bricks", "minecraft:diorite",
            "minecraft:dripstone_block", "minecraft:stone", "minecraft:stone_bricks", "minecraft:granite", "minecraft:deepslate", "minecraft:deepslate_bricks", "minecraft:cobbled_deepslate", "minecraft:tuff"}
logSet = {"minecraft:oak_log", "minecraft:dark_oak_log", "minecraft:birch_log", "minecraft:spruce_log", "minecraft:jungle_log", "minecraft:acacia_log", "minecraft:stripped_oak_log",
          "minecraft:stripped_birch_log", "minecraft:stripped_spruce_log", "minecraft:stripped_jungle_log", "minecraft:stripped_acacia_log", "minecraft:stripped_dark_oak_log", "minecraft:mangrove_log"}
ironSet = {"minecraft:iron_ore", "minecraft:raw_iron_block",
           "minecraft:deepslate_iron_ore"}

grassSet = {"minecraft:grass_block", "minecraft:grass"}


@dataclass
class Resource():
    human: int = 0
    wood: int = 0
    stone: int = 0
    food: int = 0
    ironOre: int = 0
    iron: int = 0
    grass: int = 0

    @staticmethod
    def fromDict(d: dict[str, int]) -> "Resource":
        return Resource(d["human"], d["wood"], d["stone"], d["food"], d["ironOre"], d["iron"], d["grass"])

    def __lt__(self, other):
        return (
            self.wood < other.wood or
            self.stone < other.stone or
            self.food < other.food or
            self.ironOre < other.ironOre or
            self.iron < other.iron
        )

    def __sub__(self, other):
        return Resource(
            self.human - other.human,
            self.wood - other.wood,
            self.stone - other.stone,
            self.food - other.food,
            self.ironOre - other.ironOre,
            self.iron - other.iron,
            self.grass - other.grass
        )

    def __add__(self, other):
        return Resource(
            self.human + other.human,
            self.wood + other.wood,
            self.stone + other.stone,
            self.food + other.food,
            self.ironOre + other.ironOre,
            self.iron + other.iron,
            self.grass + other.grass
        )

    def __getitem__(self, key: str):
        return getattr(self, key)

    def __setitem__(self, key: str, value: int):
        setattr(self, key, value)


@dataclass
class ResourceMap():
    area: Rect
    human: np.ndarray
    wood: np.ndarray
    stone: np.ndarray
    food: np.ndarray
    ironOre: np.ndarray
    iron: np.ndarray
    grass: np.ndarray

    def __init__(self, worldSlice: WorldSlice):
        self.area = worldSlice.rect
        shape = self.area.size.to_tuple()
        self.human = np.zeros(shape)
        self.wood = np.zeros(shape)
        self.stone = np.zeros(shape)
        self.food = np.zeros(shape)
        self.ironOre = np.zeros(shape)
        self.iron = np.zeros(shape)
        self.grass = np.zeros(shape)

        def addBlock(blockName: str, pos: ivec2):
            if blockName in logSet:
                self.wood[pos.x, pos.y] += 1
            elif blockName in stoneSet:
                self.stone[pos.x, pos.y] += 1
            elif blockName in ironSet:
                self.ironOre[pos.x, pos.y] += 1
            elif blockName in grassSet:
                self.grass[pos.x, pos.y] += 1

        sizeX, sizeZ = self.area.size
        for x in range(sizeX):
            for z in range(sizeZ):
                pos = ivec2(x,z)
                heights = worldSlice.heightmaps["MOTION_BLOCKING"]
                height = heights[pos.x, pos.y]-1

                for y in range(height-1, height-17, -1):
                    blockName = worldSlice.getBlock(addY(pos, y)).id
                    if blockName is None:
                        break

                    addBlock(blockName, pos)

                    if not blockName.count("leaves"):
                        break

    def analyzeResource(self, area: Rect | None = None) -> Resource:
        if area is None:
            area = self.area
        begin, end = area.begin, area.end
        wood: int = self.wood[begin.x:end.x, begin.y:end.y].sum()
        stone: int = self.stone[begin.x:end.x, begin.y:end.y].sum()
        ironOre: int = self.ironOre[begin.x:end.x, begin.y:end.y].sum()
        grass: int = self.grass[begin.x:end.x, begin.y:end.y].sum()
        wood *= 4
        food = wood // 40
        resource = Resource(human=2, wood=wood, stone=stone,
                            food=food, ironOre=ironOre, grass=grass)
        return resource

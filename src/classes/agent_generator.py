from typing import Callable
from gdpc.vector_tools import Rect
from ..classes.core import Core
from ..classes.agent import BuildAgent
from ..analyze_util.basic import isFlat, hasEnoughWood, closeEnoughToRoad, isLiquid, isDesert, nearBound, requiredBasement, nearBuilding
from ..config.config import config
from ..building.building_info import BuildingInfo


# basic buildings

CHALET = "chalet"
DESERT_BUILDING = "desert_building"

BASIC_BUILDINGS = {
    CHALET,
    DESERT_BUILDING
}

# Special buildings

SAWMILL = "sawmill"
FARM = "farm"
QUARRY = "quarry"
FORGE = "forge"
CHURCH = "church"

SPECIAL_BUILDINGS = {
    SAWMILL,
    FARM,
    QUARRY,
    FORGE,
    CHURCH
}

# Building tags

TAG_LAND = "land"
TAG_DESERT = "desert"
TAG_CITY = "city"
TAG_FOREST = "forest"

BUILDING_TAGS = {
    CHALET: [TAG_LAND],
    DESERT_BUILDING: [TAG_LAND, TAG_DESERT],
    SAWMILL: [TAG_LAND, TAG_FOREST],
    FARM: [TAG_LAND],
    QUARRY: [TAG_LAND],
    FORGE: [TAG_LAND],
    CHURCH: [TAG_LAND, TAG_CITY]
}


def newAgent(core: Core, name: str):
    tags = BUILDING_TAGS[name]

    def analyzeFunction(core: Core, area: Rect, buildingInfo: BuildingInfo):
        realArea = Rect(area.offset + core.buildArea.offset, area.size)
        total = 0

        if nearBound(core, realArea):
            return 0

        reqBaseBlock = requiredBasement(core, realArea)
        # TODO: make this flexible config
        if reqBaseBlock > realArea.area * 3:
            return 0

        flatness = isFlat(core, realArea)
        if flatness < config.flatnessThreshold:
            return 0
        total += flatness

        if name in SPECIAL_BUILDINGS:
            if nearBuilding(core, realArea, buildingInfo, config.minimumBuildingMargin):
                return 0

        if TAG_LAND in tags and isLiquid(core, realArea):
            return 0

        if TAG_FOREST in tags:
            buildArea = core.buildArea.toRect()
            queryArea = realArea.dilated(config.forestQueryMargin)
            begin, end = queryArea.begin, queryArea.end
            begin.x = max(begin.x, buildArea.begin.x)
            begin.y = max(begin.y, buildArea.begin.y)
            end.x = min(end.x, buildArea.end.x)
            end.y = min(end.y, buildArea.end.y)
            queryArea = Rect(begin, end-begin)
            forestness = hasEnoughWood(core, queryArea)
            if forestness < config.forestThreshold:
                return 0
            total += forestness*10

        desertness = isDesert(core, realArea)
        if TAG_DESERT in tags:
            if desertness <= config.desertnessThreshold:
                return 0
            total += desertness
        if TAG_DESERT not in tags:
            if desertness >= config.desertnessThreshold:
                return 0
            total += 1-desertness

        return total

    return BuildAgent(core, analyzeFunction, name)

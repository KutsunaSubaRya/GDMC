"""
In main.py, use levelManager = LevelManager() to create a LevelManager object
    LevelManager path is src/level/level_manager.py

Use islevelup = levelManager.isLevelUp(core.level, core.resources, len(core.blueprintData))
    to ask levelManager whether core can level up or not
    if islevelup == True, it means that:
        1. level is not reach the maxlevel
        2. all resources items reach the goal in this level
        3. number of building reach the goal in this level

Call core to level up:
    core.levelUp(levelManager.getLimitResource(core.level+1), levelManager.getLimitBuilding(core.level+1))
    use the code above can make core level to level up and update resourceLimit and buildingLimit simultaneously
    
Use levelManager.getMostLackResource(...), (return value type is str)
    to get the resource name(str) that is MOST SHORTAGE
    this function CAN/MAYBE used to decide which resource should be gathered by agents who have nothing to do

Use levelManager.isLackBuilding(...), (return value type is bool)
    to check if building is lack, namely, existBuilding < limitBuilding(in this level)
    this function CAN/MAYBE used to decide if agent should build building in this level or not

Use core.conformToResourceLimit
    to make the resource conform to the resource limit
    namely, if current resource is more than resource limit, then set current resource to resource limit

Use levelManager.getUnlockAgent(...), (return value type is str) (please see the name(str) in agent_limit.json)
    to get the SPECIAL agent name(str) that can be unlocked after this level
    if the return value is "none", it means that there is NO SPECIAL agent can be generate after this level
    NOTICE 1: this agent can only generate ONCE, for example, you can ONLY generate one sawmill agent in whole game. 
              (Because it is special agent, not wood/sand house agent)
    NOTICE 2: if you want to add new action like "some SPECIFIC building can only be upgraded after ? level", 
              you can add new name(str) in agent_limit.json, 
              and use this function to get the name(str) while you reach the level,
              then write YOUR OWN LOGIC to distinguish the name(str)
"""

# ! /usr/bin/python3
from datetime import datetime
from time import time
from random import sample
from src.classes.core import Core
from src.classes.agent import RoadAgent
from src.classes.agent_pool import AgentPool
from src.level.level_manager import LevelManager
from src.level.limit import getUnlockAgents
from src.visual.blueprint import plotBlueprint
from src.config.config import config
from pathlib import Path
from json import load
from gdpc.vector_tools import ivec3, Box
from gdpc import Editor
from time import sleep
from src.building.dungeon.area_gen import lobby_generate, surface_generate, surface_material_scattering
from src.building.dungeon.utils import local_lobby_dynamic_offset

AREA_JSON_PATH = Path("area.json")

if __name__ == '__main__':
    startTime = time()

    ROUND = config.gameRound
    NUM_BASIC_AGENTS = config.numBasicAgents
    NUM_SPECIAL_AGENTS = config.numSpecialAgents

    # LOG_PATH = Path("log")

    print("Initing core...")
    core = Core()
    print("Done initing core")
    print("save original building area...")
    original_area = core.editor.getBuildArea()
    print("Done save original building area")

    # FIXME: lobby_x, lobby_z needs to be changed dynamically

    # levelManager = LevelManager()
    # agentPool = AgentPool(core, NUM_BASIC_AGENTS, NUM_SPECIAL_AGENTS)
    # RoadAgent(core)
    #
    # for agent in agentPool.agents:
    #     print(agent)
    #
    # # iterate rounds for surface
    # for i in range(ROUND):
    #     numbersOfBuildings = [
    #         core.numberOfBuildings(level) for level in (1, 2, 3)
    #     ]
    #     limitsOfBuildings = [
    #         core.getBuildingLimit(level) for level in (1, 2, 3)
    #     ]
    #
    #     print(f"Round: {i}")
    #     print(f"Level: {core.level}")
    #     print(f"Buildings: {numbersOfBuildings}")
    #     print(f"Max Buildings:  {limitsOfBuildings}")
    #     print(f"Resources: {core.resources}")
    #
    #     core.updateResource()
    #
    #     unlockedAgents = getUnlockAgents(core.level, "surface")
    #     print("Unlocked agents: ", unlockedAgents)
    #
    #     for unlockedAgent in unlockedAgents:
    #         agentPool.unlockSpecial(unlockedAgent)
    #
    #     print("Start running agents")
    #
    #     restingAgents = 0
    #
    #     agents = list(agentPool.agents)
    #     for agent in sample(agents, len(agents)):
    #         # run agent
    #         success = agent.run()
    #
    #         if not success:
    #             # gather resource if the agent cannot do their job
    #             restingAgents += 1
    #             agent.rest()
    #
    #     core.increaseGrass()
    #
    #     print(f"Resting agents: {restingAgents}")
    #
    #     if levelManager.canLevelUp(core.level, core.resources,
    #                                core.numberOfBuildings()):
    #         core.levelUp()
    #
    #     # clamp resource to limit
    #     core.conformToResourceLimit()
    #
    #     print("Round Done")
    #     print("=====")
    #
    #     # Time limiter
    #     if time() - startTime > 465:
    #         print("Round had run over 7min 30sec. Force enter minecraft building phase.")
    #         break
    #
    # print("Start building in minecraft")
    #
    # core.startBuildingInMinecraft()
    #
    # print("Done building in minecraft")


    from src.building.dungeon.lobby_extension import lobby_extension, roadConnection
    ne, se, ee, we = lobby_extension(core.editor, original_area)

    # iterate rounds for underground
    # FIXME: hardcode here
    editor = Editor()
    globalBound = editor.getBuildArea().toRect()
    globalOffset = globalBound.offset
    lobby_offset_x, lobby_offset_z = local_lobby_dynamic_offset(original_area)
    lobby_x = lobby_offset_x + globalOffset.x
    lobby_y = config.lobby_y
    lobby_z = lobby_offset_z + globalOffset.y
    lobby_width_1 = config.lobby_width_1
    lobby_width_2 = config.lobby_width_2
    lobby_height = config.lobby_height
    build_area_start_x = lobby_x + 2
    build_area_start_y = lobby_y + 2
    build_area_start_z = lobby_z + 2
    build_area_end_x = lobby_x + lobby_width_1 - 2
    build_area_end_y = lobby_y + lobby_height * 2
    build_area_end_z = lobby_z + lobby_width_2 - 2
    surface_generate(editor, lobby_x + 2, 200, lobby_z + 2, lobby_width_1 - 4, lobby_width_2 - 4)
    # setbuildarea
    editor.runCommand(
        f"setbuildarea {build_area_start_x} {build_area_start_y} {build_area_start_z} {build_area_end_x} {build_area_end_y} {build_area_end_z}")
    editor.flushBuffer()

    print(
        f"setbuildarea {build_area_start_x} {build_area_start_y} {build_area_start_z} {build_area_end_x} {build_area_end_y} {build_area_end_z}")
    # build lobby and wall
    lobby_generate(editor, lobby_x, lobby_y, lobby_z, lobby_width_1, lobby_width_2, lobby_height)

    print("Initing core...")
    core = Core()
    print("Done initing core")

    levelManager = LevelManager()
    agentPool = AgentPool(core, NUM_BASIC_AGENTS, NUM_SPECIAL_AGENTS)
    RoadAgent(core)

    for agent in agentPool.agents:
        print(agent)

    for i in range(ROUND):
        numbersOfBuildings = [
            core.numberOfBuildings(level) for level in (1, 2, 3)
        ]
        limitsOfBuildings = [
            core.getBuildingLimit(level) for level in (1, 2, 3)
        ]

        print(f"Round: {i}")
        print(f"Level: {core.level}")
        print(f"Buildings: {numbersOfBuildings}")
        print(f"Max Buildings:  {limitsOfBuildings}")
        print(f"Resources: {core.resources}")

        core.updateResource()

        unlockedAgents = getUnlockAgents(core.level, "underground")
        print("Unlocked agents: ", unlockedAgents)

        for unlockedAgent in unlockedAgents:
            agentPool.unlockSpecial(unlockedAgent)

        print("Start running agents")

        restingAgents = 0

        agents = list(agentPool.agents)
        for agent in sample(agents, len(agents)):
            # run agent
            success = agent.run()

            if not success:
                # gather resource if the agent cannot do their job
                restingAgents += 1
                agent.rest()

        core.increaseGrass()

        print(f"Resting agents: {restingAgents}")

        if levelManager.canLevelUp(core.level, core.resources,
                                   core.numberOfBuildings()):
            core.levelUp()

        # clamp resource to limit
        core.conformToResourceLimit()

        print("Round Done")
        print("=====")

    # Change back surface to air
    surface_generate(editor, lobby_x + 2, 200, lobby_z + 2, lobby_width_1 - 4, lobby_width_2 - 4, "air")
    surface_generate(editor, lobby_x - 2, build_area_end_y + 1, lobby_z - 2, lobby_width_1 + 4, lobby_width_2 + 4,
                     "sea_lantern")
    surface_generate(editor, lobby_x - 3, build_area_end_y + 2, lobby_z - 3, lobby_width_1 + 6, lobby_width_2 + 6,
                     "stone_bricks")
    surface_material_scattering(editor, lobby_x + 2, lobby_y, lobby_z + 2, lobby_width_1 - 4,
                                lobby_width_2 - 4, "sea_lantern")
    surface_material_scattering(editor, lobby_x + 2, lobby_y + 1, lobby_z + 2, lobby_width_1 - 4,
                                lobby_width_2 - 4, "glass")
    surface_generate(editor, lobby_x - 2, lobby_y, lobby_z - 2, lobby_width_1 + 4, lobby_width_2 + 4,
                     "sea_lantern")
    surface_generate(editor, lobby_x - 3, lobby_y - 1, lobby_z - 3, lobby_width_1 + 6, lobby_width_2 + 6,
                     "stone_bricks")

    # build lobby entry
    end_x, end_y, end_z = original_area.end
    offset_x, offset_z = local_lobby_dynamic_offset(original_area)
    for i in range(1, 3):
        editor.runCommand(f"setblock {(offset_x + 60) + globalOffset.x} {i} {120 + offset_z + 3 + globalOffset.y} air")
        editor.runCommand(f"setblock {(offset_x + 60) + globalOffset.x} {i} {0 + offset_z - 3 + globalOffset.y} air")
        editor.runCommand(f"setblock {0 + offset_x - 3 + globalOffset.x} {i} {(offset_z + 60) + globalOffset.y} air")
        editor.runCommand(f"setblock {120 + offset_x + 3 + globalOffset.x} {i} {(offset_z + 60) + globalOffset.y} air")

    print("globalOffset", globalOffset)
    print("original_area", original_area)
    print("end_x", end_x)
    print("end_z", end_z)
    print("offset_x", offset_x)
    print("offset_z", offset_z)
    print("Start building in minecraft")

    core.startBuildingInMinecraft(is_underground=True, y_height=lobby_y + 2)

    print("Done building in minecraft")

    print(f"Time: {time() - startTime}")
    plotBlueprint(core)

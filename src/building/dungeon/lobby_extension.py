from src.poisson_disk_sampling import poissonDiskSample
from src.config.config import config
from glm import ivec2
from gdpc.vector_tools import Rect, Box, addY
from src.building.dungeon.utils import local_lobby_dynamic_offset
import matplotlib.pyplot as plt
from src.road.road_network import RoadNetwork, RoadEdge
from src.road.road_network import RoadNode
from gdpc import Editor
from src.building.dungeon.area_gen import cube_generate_from_middle
import matplotlib.patches as mpatch
import numpy as np

lobby_x = config.lobby_x
lobby_y = config.lobby_y
lobby_z = config.lobby_z
local_lobby_offset_x = config.local_lobby_offset_x
local_lobby_offset_z = config.local_lobby_offset_z
lobby_width_1 = config.lobby_width_1
lobby_width_2 = config.lobby_width_2
# fig, ax = plt.subplots()


class Graph:
    mst_result = []

    def __init__(self, vertices):
        self.V = vertices
        self.graph = []

    def addEdge(self, u, v, w):
        self.graph.append([u, v, w])

    def find(self, parent, i):
        if parent[i] != i:
            parent[i] = self.find(parent, parent[i])
        return parent[i]

    def union(self, parent, rank, x, y):

        if rank[x] < rank[y]:
            parent[x] = y
        elif rank[x] > rank[y]:
            parent[y] = x
        else:
            parent[y] = x
            rank[x] += 1

    def KruskalMST(self):

        result = []
        idx = 0
        e = 0
        self.graph = sorted(self.graph,
                            key=lambda item: item[2])
        parent = []
        rank = []
        for node in range(self.V):
            parent.append(node)
            rank.append(0)
        while e < self.V - 1:
            u, v, w = self.graph[idx]
            idx += 1
            x = self.find(parent, u)
            y = self.find(parent, v)
            if x != y:
                e = e + 1
                result.append([u, v, w])
                self.union(parent, rank, x, y)
        minimumCost = 0
        # print("Edges in the constructed MST")
        for u, v, weight in result:
            minimumCost += weight
            # print("%d -- %d == %d" % (u, v, weight))
        # print("Minimum Spanning Tree", minimumCost)
        self.mst_result = result


class sideNode:
    idx: int
    pos: ivec2

    def __init__(self, idx: int, pos: ivec2):
        self.idx = idx
        self.pos = pos


def display_plt(samples, end_x, end_z, offset_x, offset_z):
    print(*samples, sep='\n')
    for sample in samples:
        if 0 <= sample[0] <= end_x and 120 + offset_z <= sample[1] <= end_z:
            if sample[0] + 10 >= end_x or sample[1] + 10 >= end_z or sample[0] - 10 <= 0 or sample[
                1] - 10 <= 120 + offset_z:
                continue
            else:
                plt.scatter(sample[0], sample[1], c='g')
        elif 0 <= sample[0] <= end_x and 0 <= sample[1] <= offset_z:
            if sample[0] + 10 >= end_x or sample[1] + 10 >= offset_z or sample[0] - 10 <= 0 or sample[1] - 10 <= 0:
                continue
            else:
                plt.scatter(sample[0], sample[1], c='b')
        elif 0 <= sample[0] <= offset_x <= sample[1] <= 120 + offset_z:
            if sample[0] + 10 >= offset_x or sample[1] + 10 >= 120 + offset_z or sample[0] - 10 <= 0 or sample[
                1] - 10 <= offset_z:
                continue
            else:
                plt.scatter(sample[0], sample[1], c='orange')
        elif end_x >= sample[0] >= 120 + offset_x and offset_z + 120 >= sample[1] >= offset_z:
            if sample[0] + 10 >= end_x or sample[1] + 10 >= 120 + offset_z or sample[0] - 10 <= 120 + offset_x or \
                    sample[1] - 10 <= offset_z:
                continue
            else:
                plt.scatter(sample[0], sample[1], c='grey')

    plt.xlim(0, end_x)
    plt.ylim(0, end_z)
    plt.xticks(range(0, end_x, 20))
    plt.yticks(range(0, end_z, 20))
    plt.grid()
    plt.show()


def lobby_extension(editor: Editor, original_area: Box):
    print(original_area)
    start_x, start_y, start_z = original_area.begin
    end_x, end_y, end_z = original_area.end
    offset_x, offset_z = local_lobby_dynamic_offset(original_area)

    bound = Rect(ivec2(0, 0), ivec2(end_x, end_z))
    samples = poissonDiskSample(bound, 1000, 22)
    display_plt(samples, end_x, end_z, offset_x, offset_z)
    # sideNode list
    north_samples = []
    south_samples = []
    east_samples = []
    west_samples = []

    north_idx: int = 0
    south_idx: int = 0
    east_idx: int = 0
    west_idx: int = 0

    # determine the border

    for sample in samples:
        if 0 <= sample[0] <= end_x and 120 + offset_z <= sample[1] <= end_z:
            if sample[0] + 10 >= end_x or sample[1] + 10 >= end_z or sample[0] - 10 <= 0 or sample[
                1] - 10 <= 120 + offset_z:
                continue
            else:
                north_samples.append(sideNode(north_idx, sample))
                north_idx += 1
        elif 0 <= sample[0] <= end_x and 0 <= sample[1] <= offset_z:
            if sample[0] + 10 >= end_x or sample[1] + 10 >= offset_z or sample[0] - 10 <= 0 or sample[1] - 10 <= 0:
                continue
            else:
                south_samples.append(sideNode(south_idx, sample))
                south_idx += 1
        elif 0 <= sample[0] <= offset_x <= sample[1] <= 120 + offset_z:
            if sample[0] + 10 >= offset_x or sample[1] + 10 >= 120 + offset_z or sample[0] - 10 <= 0 or sample[
                1] - 10 <= offset_z:
                continue
            else:
                east_samples.append(sideNode(east_idx, sample))
                east_idx += 1
        elif end_x >= sample[0] >= 120 + offset_x and offset_z + 120 >= sample[1] >= offset_z:
            if sample[0] + 10 >= end_x or sample[1] + 10 >= 120 + offset_z or sample[0] - 10 <= 120 + offset_x or \
                    sample[1] - 10 <= offset_z:
                continue
            else:
                west_samples.append(sideNode(west_idx, sample))
                west_idx += 1

    # for sample in north_samples:
    #     print("North samples: ", sample.idx, sample.pos)
    # for sample in south_samples:
    #     print("South samples: ", sample.idx, sample.pos)
    # for sample in east_samples:
    #     print("East samples: ", sample.idx, sample.pos)
    # for sample in west_samples:
    #     print("West samples: ", sample.idx, sample.pos)

    # print size of north_samples, south_samples, east_samples, west_samples
    # print("Size of north_samples: ", len(north_samples))
    # print("Size of south_samples: ", len(south_samples))
    # print("Size of east_samples: ", len(east_samples))
    # print("Size of west_samples: ", len(west_samples))

    # generate road network for north samples
    north_g = Graph(len(north_samples))
    for i in range(len(north_samples)):
        for j in range(i + 1, len(north_samples)):
            # distance between two points
            distance = int(np.sqrt((north_samples[i].pos[0] - north_samples[j].pos[0]) ** 2 + (
                    north_samples[i].pos[1] - north_samples[j].pos[1]) ** 2))
            # print("Distance between ", north_samples[i].idx, " and ", north_samples[j].idx, " is: ", distance)
            # print("g.addEdge(", north_samples[i].idx, ", ", north_samples[j].idx, ", ", distance, ")" )
            north_g.addEdge(north_samples[i].idx, north_samples[j].idx, distance)
    north_g.KruskalMST()
    print("north MST pair", north_g.mst_result)
    for i in range(len(north_g.mst_result)):
        print(north_g.mst_result[i][0], north_g.mst_result[i][1], north_g.mst_result[i][2])

    # generate road network for south samples
    south_g = Graph(len(south_samples))
    for i in range(len(south_samples)):
        for j in range(i + 1, len(south_samples)):
            # distance between two points
            distance = int(np.sqrt((south_samples[i].pos[0] - south_samples[j].pos[0]) ** 2 + (
                    south_samples[i].pos[1] - south_samples[j].pos[1]) ** 2))
            # print("Distance between ", south_samples[i].idx, " and ", south_samples[j].idx, " is: ", distance)
            # print("g.addEdge(", south_samples[i].idx, ", ", south_samples[j].idx, ", ", distance, ")" )
            south_g.addEdge(south_samples[i].idx, south_samples[j].idx, distance)
    south_g.KruskalMST()
    print("south MST pair", south_g.mst_result)

    # generate road network for east samples
    east_g = Graph(len(east_samples))
    for i in range(len(east_samples)):
        for j in range(i + 1, len(east_samples)):
            # distance between two points
            distance = int(np.sqrt((east_samples[i].pos[0] - east_samples[j].pos[0]) ** 2 + (
                    east_samples[i].pos[1] - east_samples[j].pos[1]) ** 2))
            # print("Distance between ", east_samples[i].idx, " and ", east_samples[j].idx, " is: ", distance)
            # print("g.addEdge(", east_samples[i].idx, ", ", east_samples[j].idx, ", ", distance, ")" )
            east_g.addEdge(east_samples[i].idx, east_samples[j].idx, distance)
    east_g.KruskalMST()
    print("east MST pair", east_g.mst_result)

    # generate road network for west samples
    west_g = Graph(len(west_samples))
    for i in range(len(west_samples)):
        for j in range(i + 1, len(west_samples)):
            # distance between two points
            distance = int(np.sqrt((west_samples[i].pos[0] - west_samples[j].pos[0]) ** 2 + (
                    west_samples[i].pos[1] - west_samples[j].pos[1]) ** 2))
            # print("Distance between ", west_samples[i].idx, " and ", west_samples[j].idx, " is: ", distance)
            # print("g.addEdge(", west_samples[i].idx, ", ", west_samples[j].idx, ", ", distance, ")" )
            west_g.addEdge(west_samples[i].idx, west_samples[j].idx, distance)
    west_g.KruskalMST()
    print("west MST pair", west_g.mst_result)

    roadConnection(editor, original_area, north_samples, north_g.mst_result)
    print("Road connection for north samples done")
    roadConnection(editor, original_area, south_samples, south_g.mst_result)
    print("Road connection for south samples done")
    roadConnection(editor, original_area, east_samples, east_g.mst_result)
    print("Road connection for east samples done")
    roadConnection(editor, original_area, west_samples, west_g.mst_result)
    print("Road connection for west samples done")

    # ax.set_xlim(original_area.begin.x, original_area.end.x)
    # ax.set_ylim(original_area.begin.z, original_area.end.z)
    # ax.set_aspect("equal")
    # plt.show()


def roadConnection(editor: Editor, original_area, samples: list[sideNode], mst_samples: list[list[int]]):
    globalBound = original_area.toRect()
    globalOffset = globalBound.offset
    UNIT = config.unit
    fig, ax = plt.subplots()
    # ====== Add road to Minecraft ======

    # Fix the road height
    # roadNetwork
    roadNetwork = RoadNetwork[ivec2](
        hashfunc=lambda o: o.to_tuple().__hash__() if isinstance(o, ivec2) else o.__hash__())

    # init sureRoadHeights and roadNetwork
    y_height = 1

    roadNodes = set(roadNetwork.subnodes)

    # generate road
    for i in range(len(mst_samples)):
        node_idx_from = samples[mst_samples[i][0]]
        node_idx_to = samples[mst_samples[i][1]]
        pos_from_x = node_idx_from.pos[0] + globalOffset.x
        pos_from_z = node_idx_from.pos[1] + globalOffset.y
        pos_to_x = node_idx_to.pos[0] + globalOffset.x
        pos_to_z = node_idx_to.pos[1] + globalOffset.y
        # print("From: ", pos_from_x, pos_from_z)
        # print("To: ", pos_to_x, pos_to_z)

        print("=======================================================")
        print("id", i)
        # print("pos_from_x, pos_from_z", pos_from_x, pos_from_z)
        # print("pos_to_x, pos_to_z", pos_to_x, pos_to_z)
        # left bottom to right top
        if (pos_from_x < pos_to_x and pos_from_z < pos_to_z) or (pos_from_x > pos_to_x and pos_from_z > pos_to_z):
            if pos_from_x > pos_to_x and pos_from_z > pos_to_z:
                tmp = pos_from_x
                pos_from_x = pos_to_x
                pos_to_x = tmp
                tmp = pos_from_z
                pos_from_z = pos_to_z
                pos_to_z = tmp
            print("left bottom to right top")
            print("pos_from_x, pos_from_z", pos_from_x, pos_from_z)
            print("pos_to_x, pos_to_z", pos_to_x, pos_to_z)
            idx_x = pos_from_x
            z = pos_from_z
            while True:
                if idx_x + 1 >= pos_to_x and z + 1 > pos_to_z:
                    break
                elif idx_x + 1 >= pos_to_x and z + 1 <= pos_to_z:
                    z += 1
                    roadNodes.add(roadNetwork.newNode(ivec2(idx_x, z)))
                    print("add point", ivec2(idx_x, z))
                    p = mpatch.Rectangle(ivec2(idx_x, z) + globalOffset, UNIT, UNIT, fill=True, color="red")
                    ax.add_artist(p)
                elif z + 1 > pos_to_z and idx_x + 1 < pos_to_x:
                    idx_x += 1
                    roadNodes.add(roadNetwork.newNode(ivec2(idx_x, z)))
                    print("add point", ivec2(idx_x, z))
                    p = mpatch.Rectangle(ivec2(idx_x, z) + globalOffset, UNIT, UNIT, fill=True, color="red")
                    ax.add_artist(p)
                else:
                    idx_x += 1
                    z += 1
                    roadNodes.add(roadNetwork.newNode(ivec2(idx_x, z)))
                    print("add point", ivec2(idx_x, z))
                    p = mpatch.Rectangle(ivec2(idx_x, z) + globalOffset, UNIT, UNIT, fill=True, color="red")
                    ax.add_artist(p)
        # right bottom to left top
        else:
            if (pos_from_x < pos_to_x) and (pos_from_z > pos_to_z):
                tmp = pos_from_x
                pos_from_x = pos_to_x
                pos_to_x = tmp
                tmp = pos_from_z
                pos_from_z = pos_to_z
                pos_to_z = tmp
            idx_x = pos_from_x
            z = pos_from_z
            print("right bottom to left top")
            print("pos_from_x, pos_from_z", pos_from_x, pos_from_z)
            print("pos_to_x, pos_to_z", pos_to_x, pos_to_z)
            while True:
                if idx_x - 1 < pos_to_x and z + 1 >= pos_to_z:
                    break
                elif idx_x - 1 >= pos_to_x and z + 1 >= pos_to_z:
                    idx_x -= 1
                    roadNodes.add(roadNetwork.newNode(ivec2(idx_x, z)))
                    print("add point", ivec2(idx_x, z))
                    p = mpatch.Rectangle(ivec2(idx_x, z) + globalOffset, UNIT, UNIT, fill=True, color="red")
                    ax.add_artist(p)
                elif z + 1 < pos_to_z and idx_x - 1 < pos_to_x:
                    z += 1
                    roadNodes.add(roadNetwork.newNode(ivec2(idx_x, z)))
                    print("add point", ivec2(idx_x, z))
                    p = mpatch.Rectangle(ivec2(idx_x, z) + globalOffset, UNIT, UNIT, fill=True, color="red")
                    ax.add_artist(p)
                else:
                    idx_x -= 1
                    z += 1
                    roadNodes.add(roadNetwork.newNode(ivec2(idx_x, z)))
                    print("add point", ivec2(idx_x, z))
                    p = mpatch.Rectangle(ivec2(idx_x, z) + globalOffset, UNIT, UNIT, fill=True, color="red")
                    ax.add_artist(p)

    for node in roadNodes:
        area = Rect(node.val, (UNIT, UNIT))

        y = y_height

        pos = addY(node.val + globalOffset, y)

        clearBox = area.toBox(y, 3)
        for x, y, z in clearBox.inner:
            begin, last = clearBox.begin + \
                          addY(globalOffset, 0), clearBox.last + \
                          addY(globalOffset, 0)
            editor.runCommand(
                f"fill {begin.x} {begin.y} {begin.z} {last.x} {last.y} {last.z} minecraft:air",
                syncWithBuffer=True)
            break
        a = "minecraft:gold_block"
        editor.runCommand(
            f"fill {pos.x} {pos.y - 1} {pos.z} {pos.x + 1} {pos.y - 1} {pos.z + 1} {a}",
            syncWithBuffer=True)

    editor.flushBuffer()

    for sample in samples:
        cube_generate_from_middle(editor, sample.pos[0], 0, sample.pos[1], 7, 7, 7)
    editor.flushBuffer()

import queue as Q
import indoors
import math
import random
import numpy as np
from PIL import Image, ImageDraw, ImageColor
import os

building_map = {}
foot_traffic = {}
extrema = {}

VERBS = ["Head", "Walk", "Travel", "Go",  "Move", "Grapevine"]  # to reduce redundancy

OUTSIDE = "0"
ILLEGAL = "-2"
STREET = "-10"
rows, cols = -1, -1
INF = 1e9  # very large
TO_MIN = 1 / (6000 * 2)  # from pure units to minutes
SWITCH_PENALTY = 2000  # don't switch between inside and outside
CHANGE_DIRECTION_STEP = 15  # the number of steps to check if overall path direction changed (to get around curvy paths)
CROSS_STREET_PENALTY = int(1 / (2*TO_MIN))  # about half a minute of wait

STAIR_LIM = INF

# directional displacements (N, W, S, E, NW, SW, SE, NE)
root2 = math.sqrt(2)/2
dx = [-1, 0, 1, 0, -root2, root2, root2, -root2]
dy = [0, -1, 0, 1, -root2, -root2, root2, root2]


def get_direction(c1, c2):
    """
    Gets the closest cardinal direction between two points
    :param c1: starting coordinates
    :param c2: ending coordinates
    :return: North, West, South, or East
    """
    xd, yd = c2[0]-c1[0], c2[1]-c1[1]
    mx_val, mx_ind = -INF, -1
    for k in range(8):
        cand = dx[k] * xd + dy[k] * yd
        if cand > mx_val:
            mx_val, mx_ind = cand, k
    return ["North", "West", "South", "East", "Northwest", "Southwest", "Southeast", "Northeast"][mx_ind]


def generate_instructions(coords, s_meth_d=None, e_floor=1, e_meth_d=None):
    """
    Gets an English set of directions given a coordinate path and distance
    :param coords: the output from shortest_path
    :param s_meth_d: starting descending method
    :param e_floor: ending floor
    :param e_meth_d: ending ascending method
    :return: an English string
    """
    def get_building_name(bid):
        """Helper function."""
        if bid == OUTSIDE:
            return "the outdoors"
        elif bid == STREET:
            return "the street"
        return "building {}".format(bid)

    i, n = 0, len(coords)
    ret = "This path should take you at most {0:.3f} minutes.\nStart at building {1}".format(coords[-1][2] * TO_MIN,
                                                                                             building_map[coords[i][0]][coords[i][1]])
    if s_meth_d is not None:
        ret += "\nDescend to floor 1 using the {}".format(s_meth_d)
    while i < n-1:  # shouldn't do directions for last building
        j = i+1
        building_i = building_map[coords[i][0]][coords[i][1]]
        building_j = building_map[coords[j][0]][coords[j][1]]
        cds = CHANGE_DIRECTION_STEP
        while j < n and building_i == building_j and (
                building_i != OUTSIDE or
                j - i < 2 * cds or
                get_direction(coords[j - 2 * cds], coords[j - cds]) == get_direction(coords[j - cds], coords[j])):
            j += 1
            building_j = building_map[coords[j][0]][coords[j][1]]
        # j is next building change
        word = random.choice(VERBS)
        direction = get_direction(coords[i], coords[j])
        from_building = get_building_name(building_i)
        to_building = get_building_name(building_j)
        prefix = ("\n{word} {direction}, staying in {from_building}" if from_building == to_building else
                  "\n{word} {direction} to leave {from_building} and enter {to_building}")
        ret += (prefix + " (~{time:.3f} minutes)").format(word=word,
                                                          direction=direction,
                                                          from_building=from_building,
                                                          to_building=to_building,
                                                          time=(coords[j][2]-coords[j][1]) * TO_MIN)
        i = j  # update current position
    if e_meth_d is not None:
        ret += "\nAscend to floor {} using the {}".format(e_floor, e_meth_d)
    ret += "\nYou have arrived at floor {} of building {}!".format(e_floor, building_map[coords[-1][0]][coords[-1][1]])
    return ret


def find_center(building_id):
    """
    Finds center
    :param building_id: building
    :return: (x, y)
    """
    x, y, max_dist = -1, -1, 0
    min_x, max_x, min_y, max_y = extrema[building_id]
    for cx in range(min_x, max_x + 1):
        for cy in range(min_y, max_y + 1):
            if building_map[cx][cy] == building_id:
                man_d = min(abs(cx - min_x), abs(cx - max_x)) + min(abs(cy - min_y), abs(cy - max_y))
                if man_d > max_dist:
                    max_dist = man_d
                    x, y = cx, cy
    return x, y


def get_building_extrema():
    """
    Builds building extrema
    """
    global extrema
    for i in range(rows):
        for j in range(cols):
            min_x, max_x, min_y, max_y = extrema.get(building_map[i][j], (INF, 0, INF, 0))
            if i < min_x:
                min_x = i
            if i > max_x:
                max_x = i
            if j < min_y:
                min_y = j
            if j > max_y:
                max_y = j
            extrema[building_map[i][j]] = (min_x, max_x, min_y, max_y)


def get_size(building_id):
    """
    Building size
    :param building_id: id
    :return: size
    """
    min_x, max_x, min_y, max_y = extrema[building_id]
    range_x, range_y = max_x - min_x, max_y - min_y
    return math.sqrt((range_x * range_x + range_y * range_y)/2)


def get_closest_door(cur_x, cur_y, building_id, floor):
    """
    Finds closest door to building by testing proportions
    :param cur_x: loc x
    :param cur_y: loc y
    :param building_id: id of building
    :param floor: floor number
    :return: closest door's coordinates as a tuple (approximately)
    """
    min_x, max_x, min_y, max_y = extrema[building_id]
    cur_x -= min_x
    cur_y -= min_y
    cd = indoors.closest_door(building_id, floor, cur_x / (max_x - min_x), cur_y / (max_y - min_y))[0:1]
    prop_x, prop_y = cd[0:1]
    return int(prop_x * (max_x - min_x) + min_x), int(prop_y * (max_y - min_y) + min_y), cd[2]


def shortest_path(start_building, end_building, start_floor=1, end_floor=1, stair_limit=INF):
    """
    Finds detailed shortest path between two buildings and draws an image locally to reflect this path
    :param start_building: building the user starts at
    :param end_building: building the user ends at
    :param start_floor: floor you start on
    :param end_floor: floor you end on
    :param stair_limit: max amount of stairs user wants to climb in a row
    :return: an English direction based on a list of coordinates generated
    """
    if end_building in ["E23", "E25"]:
        end_building = "E23/E25"
    # initialize useful globals/variables
    global building_map, foot_traffic, rows, cols, STAIR_LIM
    start_floor = int(start_floor)
    end_floor = int(end_floor)
    with open('building_map.txt', 'r') as f:
        string_v = f.readline()

    building_map = eval(string_v)  # the building map, 2D array of labels (strings/ints) floodfilled to building number
    foot_traffic = list(100 * np.ones([len(building_map),len(building_map[0])]))  # the foot traffic, for distance purposes (based on time). Default is 100
    rows, cols = len(building_map), len(building_map[0])
    STAIR_LIM = stair_limit
    get_building_extrema()
    im = Image.open("bigmap.png").convert("RGB")
    draw = ImageDraw.Draw(im)

    # shortest paths
    startx, starty = find_center(start_building)
    if start_building not in extrema:
        return "Invalid starting building"
    if end_building not in extrema:
        return "Invalid ending building"
    #startx, starty, startd = get_closest_door(startx, starty, start_building, start_floor)
    dist = [[INF] * cols for _ in range(rows)]
    prev = [[None] * cols for _ in range(rows)]
    #starting_doors = indoors.get_scaled_door_locs(start_building, start_floor, get_building_extrema(start_building))
    #door_dists = indoors.traverse(start_building, startd, start_floor, stair_limit=STAIR_LIM)
    start_dist, s_meth_d = indoors.traverse(get_size(start_building), start_floor=start_floor, stair_limit=STAIR_LIM)
    dist[startx][starty] = start_dist
    q = Q.PriorityQueue()
    q.put((start_dist, startx, starty))
    # for ind, (door_x, door_y) in enumerate(starting_doors):
    #     dist[door_x][door_y] = door_dists[ind]
    #     q.put((dist[door_x][door_y], door_x, door_y))
    while not q.empty():
        cdist, cx, cy = q.get()
        if cdist > dist[cx][cy]:  # lol we don't do decrease-key in these parts
            continue
        if building_map[cx][cy] == end_building:
            endx, endy = cx, cy
            break  # we found it!
        for k in range(4):
            nx, ny = cx + dx[k], cy + dy[k]
            if nx < 0 or ny < 0 or nx >= rows or ny >= cols or building_map[nx][ny] == ILLEGAL:  # no illegal steps
                continue
            ndist = cdist
            if (building_map[cx][cy] not in [OUTSIDE, STREET] and building_map[nx][ny] in [OUTSIDE, STREET] or
                    building_map[cx][cy] in [OUTSIDE, STREET] and building_map[nx][ny] not in [OUTSIDE, STREET]):
                ndist += SWITCH_PENALTY
            if building_map[cx][cy] == OUTSIDE and building_map[nx][ny] == STREET:
                ndist += CROSS_STREET_PENALTY
            elif building_map[nx][ny] in [OUTSIDE, STREET]:
                ndist += foot_traffic[nx][ny]
            elif building_map[nx][ny] != building_map[cx][cy]:
                # starting_door = get_closest_door(nx, ny, building_map[nx][ny], 1)[2]
                # door_dists = indoors.traverse(building_map[nx][ny], door_index=starting_door, stair_limit=STAIR_LIM)
                ndist += indoors.traverse(get_size(building_map[nx][ny]))[0]
            if ndist < dist[nx][ny]:
                dist[nx][ny] = ndist
                prev[nx][ny] = (cx, cy)
                q.put((ndist, nx, ny))
    ret = []
    end_dist, e_meth_d = indoors.traverse(get_size(end_building), end_floor=end_floor, stair_limit=STAIR_LIM)
    dist[endx][endy] += end_dist
    cur = (endx, endy)
    while cur:
        ret.append((cur[0], cur[1], dist[cur[0]][cur[1]]))
        cur = prev[cur[0]][cur[1]]
    coords = list(reversed(ret))
    for i in range(len(coords)-1):
        draw.line((coords[i][1], coords[i][0], coords[i+1][1], coords[i+1][0]), fill=(0, 0, 255), width=3)
    del draw
    im.save("{}/static/sp_out.png".format(os.getcwd()), "PNG")
    return generate_instructions(coords, s_meth_d=s_meth_d, e_floor=end_floor, e_meth_d=e_meth_d)


# debugging
if __name__ == '__main__':
    x = 'N4'
    y = '26'
    sp = shortest_path(x, y, 1, 1)
    print(sp)
    # x = 'N52'
    # y = 54
    # building_map = [[x, x, -1, -1, -1, -2, -2, -2],
    #                 [-1, x, -1, 10, 10, 10, -1, -1],
    #                 [-2, -1, -2, -2, -2, 10, -1, -1],
    #                 [-2, -1, -1, -1, -2, 10, 16, -1],
    #                 [-2, -1, -2, -1, -1, -1, -1, -1],
    #                 [y, y, -2, -2, -2, -2, -2, -2],
    #                 [y, y, y, y, y, y, y, y]]
    # foot_traffic = [[100, 100, 100, 100, 100, 100, 100, 100],
    #                 [100, 100, 100, 100, 100, 100, 100, 100],
    #                 [100, 8000, 100, 100, 100, 100, 100, 100],
    #                 [100, 150, 100, 100, 100, 100, 100, 100],
    #                 [100, 100, 100, 2000, 100, 100, 100, 100],
    #                 [100, 100, 100, 100, 100, 100, 100, 100],
    #                 [100, 100, 100, 100, 100, 100, 100, 100]]
    # rows, cols = 7, 8
    # sp = shortest_path(x, y)
    # print(sp)
    # print(generate_instructions(sp))

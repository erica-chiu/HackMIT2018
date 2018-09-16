import queue as Q
import indoors
import math
import random
import numpy as np

with open('building_map.txt', 'r') as f:
    string_v = f.readline()

building_map = eval(string_v)  # the building map, 2D array of labels (strings/ints) floodfilled to building number
foot_traffic = 100*list(np.ones([len(building_map),len(building_map[0])]))  # the foot traffic, for distance purposes (based on time). Default is 100
extrema = {}

VERBS = ["Head", "Walk", "Travel", "Go",  "Move", "Grapevine"]  # to reduce redundancy

OUTSIDE = "0"
ILLEGAL = "-2"
rows, cols = -1, -1
INF = 1e9  # very large
TO_MIN = 1 / (6000 * 4)  # from pure units to minutes  TODO: fix this scaling
CHANGE_DIRECTION_STEP = 15  # the number of steps to check if overall path direction changed (to get around curvy paths)  TODO: fix this scaling

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
        return "the outdoors" if bid == OUTSIDE else "building {}".format(bid)

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
    ret += "\nYou have arrived at building {}!".format(building_map[coords[-1][0]][coords[-1][1]])
    return ret


def find_xy_cluster(building_id):
    """
    Floodfill finder
    :param building_id: building id to search
    :return: (x, y) coordinates of first matching ID or (-1, -1) if not found
    """
    assert(building_id != OUTSIDE), "This should not be done on the outdoors"
    for i in range(rows):
        for j in range(cols):
            if building_map[i][j] == building_id:
                return i, j
    return -1, -1


def get_building_extrema(building_id):
    """
    Gets building extrema
    :param building_id: the building
    :return: tuple of 4 (minx, maxx, miny, maxy)
    """
    if building_id in extrema:
        return extrema[building_id]
    min_x, min_y, max_x, max_y = INF, INF, 0, 0
    for i in range(rows):
        for j in range(cols):
            if building_map[i][j] == building_id:
                if i < min_x:
                    min_x = i
                if i > max_x:
                    max_x = i
                if j < min_y:
                    min_y = j
                if j > max_y:
                    max_y = j
    extrema[building_id] = (min_x, max_x, min_y, max_y)
    return extrema[building_id]


def get_size(building_id):
    """
    Building size
    :param building_id: id
    :return: size
    """
    min_x, max_x, min_y, max_y = get_building_extrema(building_id)
    range_x, range_y = max_x - min_x, max_y - min_y
    return math.sqrt(range_x * range_x + range_y * range_y)


def get_closest_door(cur_x, cur_y, building_id, floor):
    """
    Finds closest door to building by testing proportions
    :param cur_x: loc x
    :param cur_y: loc y
    :param building_id: id of building
    :param floor: floor number
    :return: closest door's coordinates as a tuple (approximately)
    """
    min_x, max_x, min_y, max_y = get_building_extrema(building_id)
    cur_x -= min_x
    cur_y -= min_y
    cd = indoors.closest_door(building_id, floor, cur_x / (max_x - min_x), cur_y / (max_y - min_y))[0:1]
    prop_x, prop_y = cd[0:1]
    return int(prop_x * (max_x - min_x) + min_x), int(prop_y * (max_y - min_y) + min_y), cd[2]


def shortest_path(start_building, end_building, start_floor=1, end_floor=1):
    """
    Finds detailed shortest path between two buildings.
    :param start_building: building the user starts at
    :param end_building: building the user ends at
    :param start_floor: floor you start on
    :param end_floor: floor you end on
    :return: a list of coordinates for the user to go with times
    """
    startx, starty = find_xy_cluster(start_building)
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
            if building_map[nx][ny] == OUTSIDE:
                ndist += foot_traffic[nx][ny]
            elif building_map[nx][ny] != building_map[cx][cy]:
                # starting_door = get_closest_door(nx, ny, building_map[nx][ny], 1)[2]
                # door_dists = indoors.traverse(building_map[nx][ny], door_index=starting_door, stair_limit=STAIR_LIM)
                add, meth_d = indoors.traverse(get_size(building_map[nx][ny]))
                ndist += add
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
    return generate_instructions(list(reversed(ret)), s_meth_d=s_meth_d, e_meth_d=e_meth_d)


def build_vals(traffic=None, stair_lim=None):
    """
    Builds globals
    :param buildings: map of buildings
    :param traffic: map of foot traffic
    :return: None
    """
    global foot_traffic, STAIR_LIM, rows, cols
    rows, cols = len(building_map), len(building_map[0])
    if traffic is None:
        foot_traffic = [[100] * cols for _ in range(rows)]
    else:
        foot_traffic = traffic
    if stair_lim is not None:
        STAIR_LIM = stair_lim


# debugging
if __name__ == '__main__':

    x = 'NE43'
    y = '26'
    build_vals()
    sp = shortest_path(x, y)
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

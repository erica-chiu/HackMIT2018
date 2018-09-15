import queue as Q
from . import indoors

building_map = []  # the building map, 2D array of strings floodfilled to building number
foot_traffic = []  # the foot traffic, for distance purposes (based on time). Default is 100

OUTSIDE = -1
ILLEGAL = -2
rows, cols = -1, -1
INF = 1e9  # very large

# directional displacements
dx = [0, 1, 0, -1]
dy = [1, 0, -1, 0]


def find_xy_cluster(building_id):
    """
    Floodfill finder
    :param building_id: building id to search
    :return: (x, y) coordinates of first matching ID or (-1, -1) if not found
    """
    assert(building_id != OUTSIDE), "This should not be done on the outdoors"
    for i in range(len(building_map)):
        for j in range(len(building_map[i])):
            if building_map[i][j] == building_id:
                return i, j
    return -1, -1


def shortest_path(start_building, end_building, start_floor = 1, end_floor = 1):
    """
    Finds detailed shortest path between two buildings.
    :param start_building: building the user starts at
    :param end_building: building the user ends at
    :param start_floor: floor you start on
    :param end_floor: floor you end on
    :return: a list of coordinates for the user to go
    """
    startx, starty = find_xy_cluster(start_building)
    endx, endy = find_xy_cluster(end_building)
    dist = [[INF] * cols for _ in range(rows)]
    prev = [[None] * cols for _ in range(rows)]
    dist[startx][starty] = indoors.traverse(building_map[startx][starty])
    q = Q.priority_queue
    q.put((dist[startx][starty], startx, starty))
    while not q.empty():
        cdist, cx, cy = q.get()
        if cdist > dist[cx][cy]:  # lol we don't do decrease-key in these parts
            continue
        if endx == cx and endy == cy:
            break  # we found it!
        for k in range(4):
            nx, ny = cx + dx[k], cy + dy[k]
            if nx < 0 or ny < 0 or nx >= rows or ny >= cols or building_map[nx][ny] == ILLEGAL:  # no illegal steps
                continue
            ndist = cdist
            if building_map[nx][ny] == OUTSIDE:
                ndist += foot_traffic[nx][ny]
            elif building_map[nx][ny] != building_map[cx][cy]:
                # this probably has to be more rigorous (implement doors)
                ndist += indoors.traverse(building_map[nx][ny])
            if ndist < dist[nx][ny]:
                dist[nx][ny] = ndist
                prev[nx][ny] = (cx, cy)
                q.put((ndist, nx, ny))
    ret = []
    cur = (endx, endy)
    while cur:
        ret.append((cur[0], cur[1]))
        cur = prev[cur[0]][cur[1]]
    return reversed(ret)


def build_vals(buildings, traffic=None):
    """
    Builds globals
    :param buildings: map of buildings
    :param traffic: map of foot traffic
    :return: None
    """
    global building_map, foot_traffic, rows, cols
    building_map = buildings
    rows, cols = len(buildings), len(buildings[0])
    if traffic is None:
        foot_traffic = [[100] * cols for _ in range(rows)]
    else:
        foot_traffic = traffic

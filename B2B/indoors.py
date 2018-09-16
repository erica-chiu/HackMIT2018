import queue as Q

building_map = {}  # dictionary from buildings to 3D interior arrays (these arrays are separated by floor)
foot_traffic = {}  # dictionary from building to array, where each array is floor -> number (default 100)
door_locs = {}  # dictionary from buildings to list representing location of doors on each floor

# anything nonnegative is a door index
FLOOR = -1
WALL = -2
STAIRCASE = -3
ELEVATOR = -4

CLIMBING_TIME = 1000  # about this many units for one flight of stairs
ELEVATOR_WAIT = 10  # this is multiplied by foot traffic to estimate wait time
ELEVATOR_TIME = 200  # time to ascend floors (also increased by foot traffic because of floor waiting)

dx = [-1, 0, 1, 0]
dy = [0, -1, 0, 1]

INF = 1e9  # very large


def get_scaled_door_locs(building_id, floor, extrema):
    """
    Returns door locations in terms of outdoor coordinates
    :param building_id: the building
    :param floor: the floor of the building
    :param extrema: the building extrema in outdoor coordinates
    :return: a list of tuples
    """
    floor_map = building_map[building_id][floor]
    x_range, y_range = len(floor_map), len(floor_map[0])
    min_x, max_x, min_y, max_y = extrema
    locs = []
    for d_x, d_y in enumerate(door_locs[building_id][floor]):
        locs.append(int(d_x / x_range * (max_x - min_x) + min_x), int(d_y / y_range * (max_y - min_y) + min_y))
    return locs


def closest_door(building_id, floor, prop_x, prop_y):
    """
    Returns closest door matching the proportions (Manhattan distance)
    :param building_id: the building id
    :param floor: floor of the building
    :param prop_x: how far down the point is as a fraction
    :param prop_y: how far right the point is as a fraction
    :return: tuple of proportions
    """
    best_dx, best_dy, best_ind, best_error = None, None, None, INF
    floor_map = building_map[building_id][floor]
    x_range, y_range = len(floor_map), len(floor_map[0])
    for ind, (d_x, d_y) in enumerate(door_locs[building_id][floor]):
        cur_error = abs(d_x / x_range - prop_x) + abs(d_y / y_range - prop_y)
        if cur_error < best_error:
            best_error = cur_error
            best_dx = d_x / x_range
            best_dy = d_y / y_range
    return best_dx, best_dy, best_ind


def door_ff(building_id, floor, start_x, start_y, can_stair=False):
    """
    Given a building id, returns distances to all doors on a floor
    :param building_id: 2D map of the floor
    :param floor: the floor
    :param start_x: coord to start from
    :param start_y: coord to start from
    :param can_stair: is the user willing to take so many stairs
    :return: tuple(list of distances to doors, minimum distance to a stair/elev, stair/elev's location)
    """
    floor_map = building_map[building_id][floor]
    rows, cols = len(floor_map), len(floor_map[0])
    dist = [[-1] * cols for _ in range(rows)]
    q = Q.Queue()
    q.put((0, start_x, start_y))
    dist[start_x][start_y] = 0
    min_floor_t_dist = INF  # minimum "floor transfer" distance
    floor_t_loc = None
    while not q.empty():
        cdist, cx, cy = q.get()
        if (floor_map[cx][cy] == ELEVATOR or floor_map[cx][cy] == STAIRCASE and can_stair) and min_floor_t_dist == INF:
            min_floor_t_dist = cdist
            floor_t_loc = (cx, cy)
        for k in range(4):
            nx, ny = cx + dx[k], cy + dy[k]
            if nx < 0 or ny < 0 or nx >= rows or ny >= cols or dist[nx][ny] > -1 or floor_map[nx][ny] == WALL:
                continue
            dist[nx][ny] = cdist + 1
            q.put((dist[nx][ny], nx, ny))
    return [dist[d[0]][d[1]] for d in door_locs[building_id][floor]], min_floor_t_dist, floor_t_loc


def traverse(building_id, door_index=0, start_floor=1, end_floor=1, stair_limit=INF):
    """
    Finds time to traverse through a building
    :param building_id: building to start
    :param door_index: door the user entered from
    :param start_floor: floor to start
    :param end_floor: floor to end
    :param stair_limit: max amount of floors the user wants to climb in a row
    :return: tuple(travel time for each door, method of de/ascension)
    """
    total_times, meth_d = [], None  # method of descent
    door_x, door_y = door_locs[building_id][start_floor][door_index]
    if start_floor != end_floor:
        floor_plan = building_map[building_id][start_floor]
        # start floor door -> stairs/elevators
        floor_diff = abs(start_floor - end_floor)
        can_stair = floor_diff <= stair_limit
        ff_info = door_ff(building_id, start_floor, door_x, door_y, can_stair=can_stair)
        to_floor_t_time = ff_info[1]
        floor_t_x, floor_t_y = ff_info[2]
        meth_d = "elevator" if floor_plan[floor_t_x][floor_t_y] == ELEVATOR else "stairs"
        if meth_d == "elevator":
            elevator_wait = ELEVATOR_WAIT * foot_traffic[building_id][start_floor]
            elevator_time = ELEVATOR_TIME * foot_traffic[building_id][start_floor] / 100 * floor_diff
            floor_t_time = elevator_time + elevator_wait
        else:
            floor_t_time = CLIMBING_TIME * floor_diff
        # stairs/elevators -> end floor door
        door_times = door_ff(building_id, end_floor, floor_t_x, floor_t_y)[0]
        total_times = [t + to_floor_t_time + floor_t_time for t in door_times]
    else:
        # wow this is so much simpler
        total_times = door_ff(building_id, start_floor, door_x, door_y)[0]
    return total_times, meth_d


def build_vals(buildings, traffic):
    """
    See globals for defs
    :param buildings: The buildings
    :param traffic: The traffic
    :return: None
    """
    global building_map, foot_traffic
    building_map = buildings
    foot_traffic = traffic
    for b, v in buildings.items():
        floor_doors = []
        for f in range(len(v)):
            doors = []
            for i in range(len(f)):
                for j in range(len(f[i])):
                    if f[i][j] >= 0:
                        doors.append((i, j))
            floor_doors.append(doors)
        door_locs[b] = floor_doors

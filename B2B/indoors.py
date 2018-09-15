building_map = {}  # dictionary from buildings to 3D interior arrays (these arrays are separated by floor)
foot_traffic = {}  # dictionary from building to array, where each array is floor -> number (default 100)

FLOOR = 1
WALL = -1
STAIRCASE = 2
ELEVATOR = 3

CLIMBING_TIME = 1000  # about this many units for one flight of stairs
ELEVATOR_WAIT = 10  # this is multiplied by foot traffic to estimate wait time
ELEVATOR_TIME = 200  # time to ascend floors (also increased by foot traffic because of floor waiting)

INF = 1e9  # very large


def traverse(building_id, start_floor=1, end_floor=1, stair_limit=INF):
    """
    Finds time to traverse through a building
    :param building_id: building to start
    :param start_floor: floor to start
    :param end_floor: floor to end
    :return: tuple(travel time, method of de/ascension)
    """
    # go to a staircase or an elevator, then just sum up travel distances
    total_time, meth_d = 0, None
    floor_map = building_map[building_id][start_floor]
    # TODO: find time to travel normally based on line of travel or averaging (averaging is bad for thin buildings)
    if start_floor != end_floor:
        floor_diff = abs(start_floor - end_floor)
        if floor_diff <= stair_limit:
            # TODO: figure out time to traverse to stairs based on floor map
            total_stair_time = CLIMBING_TIME * floor_diff  # this is almost always going to be less, elevators slow
        elevator_wait = ELEVATOR_WAIT * foot_traffic[building_id][start_floor]
        elevator_time = ELEVATOR_TIME * foot_traffic[building_id][start_floor] / 100 * floor_diff
        total_elevator_time = elevator_time + elevator_wait
        meth_d = "elevator" if total_elevator_time <= total_stair_time else "stairs"
        total_time += min(total_elevator_time, total_stair_time)
    return total_time, meth_d


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

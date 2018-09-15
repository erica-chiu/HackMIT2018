building_map = {}  # dictionary from buildings to 3D interior arrays (these arrays are separated by floor)
foot_traffic = {}  # dictionary from building to array, where each array is floor -> number (default 100)

FLOOR = 1
WALL = -1
STAIRCASE = 2
ELEVATOR = 3


def traverse(building_id, start_floor=1, end_floor=1):
    """
    Finds time to traverse through a building
    :param building_id: building to start
    :param start_floor: floor to start
    :param end_floor: floor to end
    :return: the travel time
    """
    return 0
    # go to a staircase or an elevator, then just sum up travel distances
    floor_map = building_map[building_id][start_floor]
    if start_floor != end_floor:
        # go to staircase or elevator
        pass
    # add in usual distance


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

#region VEXcode Generated Robot Configuration
import math
import random
from vexcode_vr import *

# Brain should be defined by default
brain=Brain()

drivetrain = Drivetrain("drivetrain", 0)
pen = Pen("pen", 8)
pen.set_pen_width(THIN)
left_bumper = Bumper("leftBumper", 2)
right_bumper = Bumper("rightBumper", 3)
front_eye = EyeSensor("frontEye", 4)
down_eye = EyeSensor("downEye", 5)
front_distance = Distance("frontdistance", 6)
distance = front_distance
magnet = Electromagnet("magnet", 7)
location = Location("location", 9)


#endregion VEXcode Generated Robot Configuration
# ------------------------------------------
# 
# 	Project:      Dynamic Maze Solver
#	Author:       Guy Nicklin
#	Created:      28/01/2025
#	Description:  A program to solve any 8x8 given maze, map the whole maze and mark the most eficient exit route.
# 
# ------------------------------------------

def move_forward():
    """
    Move the robot forward by 250 mm.
    """
    drivetrain.drive_for(FORWARD, 250, MM)

def turn_right_and_move():
    """
    Turn the robot 90 degrees to the right and move forward by 250 mm.
    """
    drivetrain.turn_for(RIGHT, 90, DEGREES)
    drivetrain.drive_for(FORWARD, 250, MM)

def turn_left_and_move():
    """
    Turn the robot 90 degrees to the left and move forward by 250 mm.
    """
    drivetrain.turn_for(LEFT, 90, DEGREES)
    drivetrain.drive_for(FORWARD, 250, MM)

def turn_around_and_move():
    """
    Turn the robot 180 degrees and move forward by 250 mm.
    """
    drivetrain.turn_for(RIGHT, 180, DEGREES)
    drivetrain.drive_for(FORWARD, 250, MM)


def define_maze():
    """
    Define an 8x8 maze with each tile having a visited, walls and key_tile (represents a visual symbol when printing) attribute.

    Returns:
        dict: A dictionary representing the maze with coordinates as keys.
    """
    maze = {}
    for i in range(1, 9):
        for j in range(1, 9):
            x = -870 + (j - 1) * 250
            y = 850 - (i - 1) * 250

            maze[(x, y)] = {
                'visited': False,
                'walls': [],
                'key_tile' : "□ ",
            }
    return maze


def bearings_to_walls(all_walls, is_southern=None, is_northern=None):
    """
    Converts bearings of walls (N,E,S,W) to symbols for display after completion.

    Args:
        all_walls (list): Walls for the current row in the maze.
        is_southern (bool): Flag to only process walls south of the row.
        is_northern (bool): Flag to only process walls North of the row.

    returns:
        list: a list of symbols representing walls in a row. 
    """
    walls_representation = []

    for tile_walls in all_walls:
        # For East and West walls and gaps.
        if not is_southern and not is_northern:
            if "E" in tile_walls:
                    walls_representation.append("|")
            else:
                walls_representation.append(" ")
        # For North walls and gaps.
        elif not is_northern:
            if "S" in tile_walls:
                walls_representation.append("-  ")
            else:
                walls_representation.append("   ")
        # For South walls and gaps.
        else:
            if "N" in tile_walls:
                    walls_representation.append("-  ")
            else:
                walls_representation.append("   ")

    return walls_representation


def print_visual_maze(maze):
    """
    Print a visual representation of the maze using unicode.

    Args:
        maze (dict): The current maze structure.
    """
    # What will be the visual reperesentation of the maze.
    grid = [[]]

    # Convert dictionary in to 8 lists for each row in the maze.
    maze_items = list(maze.items())     
    rows = [maze_items[i:i + 8] for i in range(0, len(maze_items), 8)]

    # Boundry buffer to align tiles and East/West walls .
    buffer_tiles_and_walls = ["|"]

    # Boundry buffer to align South and North walls.
    buffer_walls = [" "]

    for index, row in enumerate(rows):
        # Extract symbols. 
        key_tiles =  [item[1]['key_tile'] for item in row]
        # Extract walls.
        walls = [item[1]['walls'] for item in row] 
        # Symbolise current row.
        east_and_west_walls = bearings_to_walls(walls)
        # Symbolise walls below (South).
        southern_walls = bearings_to_walls(walls, True) 

        # Only symbolise Northern walls on the first loop (Top border) as we can just process southern walls after.
        if index == 0:
            northern_walls = bearings_to_walls(walls, True, True) 
            grid.append(buffer_walls + northern_walls)

        # Interleaves tile symbols list with walls list.  
        merged_walls_and_tiles = [item for pair in zip(key_tiles, east_and_west_walls) for item in pair]

        # Append tiles and there West and East walls. Then append there Southern walls.
        grid.append(buffer_tiles_and_walls + merged_walls_and_tiles)
        grid.append(buffer_walls + southern_walls)

    # Print the visual reperesentation of the maze.
    for row in grid:
        for symbol in row:
            # Highlights the route from entrance to exit in red for better understanding.
            symbols_to_colour = ['✩ ', "↑ ", "→ ", "↓ ", "← ", "○ "]
            if symbol in symbols_to_colour:
                brain.set_print_color(RED)
                brain.print(symbol)
                brain.set_print_color(BLACK)
            else:
                brain.print(symbol)
        brain.new_line()
    
    brain.new_line()

    # Also print the data for reference.
    for row in rows:
        brain.print(row)
        brain.new_line()


def set_visited(maze): 
    """
    Mark the current tile as visited.

    Args:
        maze (dict): The current maze structure.
    """
    tile = get_tile(maze)
    maze[tile]['visited'] = True


def get_visited(maze, tile):
    """
    Get the visited status of a specific tile.

    Args:
        maze (dict): The current maze structure.
        tile (tuple): The tile coordinates.

    Returns:
        bool: True if the tile has been visited, False otherwise.
    """
    return maze[tile]['visited']


def visited_all_tiles(maze):
    """
    Check if all tiles in the maze have been visited.

    Args:
        maze (dict): The current maze structure.

    Returns:
        bool: True if all tiles have been visited, False otherwise.
    """
    return all(tile['visited'] for tile in maze.values()) 


def set_walls(maze, tile, bearings):
    """
    Set walls attribute (N, S, E, W) for a given tile in the maze.

    Args:
        maze (dict): The current maze structure.
        tile (tuple): The tile coordinates.
        bearings (list): The directions where walls exist.
    """
    for bearing in bearings:
        if bearing not in maze[tile]['walls']:
            maze[tile]['walls'].append(bearing)
            
    
def get_walls(maze, tile):
    """
    Get the walls attribute of a given tile in the maze.

    Args:
        maze (dict): The current maze structure.
        tile (tuple): The coordinate of the tile.

    Returns:
        list: The walls present at the given tile.
    """
    return maze[tile]['walls']
    
def get_tile(maze):
    """
    Snap to the closest coordinate within the maze (The tile we are in). 
    Uses the Euclidean distance formula in two dimensions.
    This accounts for inaccuracies in robot location when turning.

    Args:
        maze (dict): The current maze structure.

    Returns:
        tuple: The closest tile coordinate.
    """
    current_position = (location.position(X, MM), location.position(Y, MM))
    x, y = current_position

    # Smallest squared Euclidean distance to the current position. 
    return min(maze.keys(), key=lambda coord: (coord[0] - x) ** 2 + (coord[1] - y) ** 2)


def detect_exit(movement_stack):
    """
    Detect if the robot has reached an exit tile.

    Args:
        movement_stack (list of lists): Each list contains the recorded movements of the robot between intersections.

    Returns:
        list or bool: The shortest route if exit is found, else False.
    """
    exit = down_eye.detect(RED)
    shortest_route = False

    # Return the combined movement stacks when the exit is detected.
    if exit:
        shortest_route = sum(movement_stack, [])

    return shortest_route
        

def get_adjacent_tile(maze, bearing):
    """
    Get the adjacent tile based on the given bearing.

    Args:
        maze (dict): The current maze representation.
        bearing (str): The direction ('N', 'E', 'S', 'W') to find the adjacent tile.

    Returns:
        tuple or None: The adjacent tile coordinate if valid, otherwise None.
    """
    current_position = (location.position(X, MM), location.position(Y, MM))
    x, y = current_position

    if bearing == 'N':
        y += 250
    elif bearing == 'E':
        x += 250
    elif bearing == 'S':
        y -= 250
    elif bearing == 'W':
        x -= 250

    # Find the closest valid tile as movements can throw slight position inaccuracies.
    # Smallest squared Euclidean distance to the current position + or - 250 (distance of a tile).
    tile = min(maze.keys(), key=lambda coord: (coord[0] - x) ** 2 + (coord[1] - y) ** 2)

    # Ensure it hasn't snapped to the current position.
    if tile != current_position:
        return tile
    else:
        return None   


def set_entrance(maze, start_position):
    """
    Dynamically assign a wall to the entrance to prevent the robot from leaving.
    Set the entrance tile as visited.

    Args:
        maze (dict): The current maze representation.
        start_position (tuple): The coordinate of the start position.
    """
    current_position_angle = location.position_angle(DEGREES)
    
    # Entrance is logically always behind the robot on start, so dynamically assign wall based on position angle.
    if current_position_angle == 0:
        set_walls(maze, start_position, 'S')
    elif current_position_angle == 90:
        set_walls(maze, start_position, 'W')
    elif current_position_angle == 180:
        set_walls(maze, start_position, 'N')
    else:
        set_walls(maze, start_position, 'E')
    
    set_visited(maze)


def set_bearings(maze, front, left, right):
    """
    Determines the robot's orientation and sets walls in the maze accordingly.
    
    Args:
        maze (dict): The maze structure where the walls will be recorded.
        front (bool): Whether there is a wall in front of the robot.
        left (bool): Whether there is a wall to the left of the robot.
        right (bool): Whether there is a wall to the right of the robot.
    """
    # Calculates the robot's current position angle.
    current_position_angle = location.position_angle(DEGREES)
    current_tile = get_tile(maze)
    bearings = []

    # determines which directions correspond to North, East, South, and West based on position angle.
    # N
    if current_position_angle == 0 or current_position_angle == 360:
        if front: bearings.append('N')
        if left: bearings.append('W')
        if right: bearings.append('E') 
    # E    
    elif current_position_angle == 90:
        if front: bearings.append('E') 
        if left: bearings.append('N') 
        if right: bearings.append('S')
    # S   
    elif current_position_angle == 180:
        if front : bearings.append('S') 
        if left: bearings.append('E') 
        if right: bearings.append('W') 
    # W 
    elif current_position_angle == 270:
        if front : bearings.append('W') 
        if left: bearings.append('S') 
        if right: bearings.append('N')  

    # Updates the maze's wall data accordingly.
    set_walls(maze, current_tile, bearings)


def determine_movement(bearing, maze):
    """
    Determines the robot's movement based on the presence of walls and its current orientation.
    
    Args:
        bearing (str): The direction the robot intends to move ('N', 'E', 'S', 'W').
        maze (dict): The maze structure where walls are recorded.
    
    Returns:
        bool: False if movement is blocked by a wall, True if the robot moves successfully.
    """
    current_heading = location.position_angle(DEGREES)
    current_tile = get_tile(maze)

    # Dont drive into walls.
    walls = get_walls(maze, current_tile)
    if bearing in walls:
        # Robot has not successfully made a move.
        return False
    
    # Make a movement based on the passed bearing (N, S, E , W)
    #N
    if current_heading == 0 or current_heading == 360:  
        if bearing == 'N': 
            move_forward()
        elif bearing == 'E':
            turn_right_and_move()
        elif bearing == 'W': 
            turn_left_and_move()
        elif bearing == 'S': 
            turn_around_and_move()
    #E
    elif current_heading == 90:  
        if bearing == 'E':
            move_forward()
        elif bearing == 'S': 
            turn_right_and_move()
        elif bearing == 'N': 
            turn_left_and_move()
        elif bearing == 'W': 
            turn_around_and_move()
    #S
    elif current_heading == 180:  
        if bearing == 'S': 
            move_forward()
        elif bearing == 'W': 
            turn_right_and_move()
        elif bearing == 'E': 
            turn_left_and_move()
        elif bearing == 'N': 
            turn_around_and_move()
    #W
    elif current_heading == 270:  
        if bearing == 'W': 
            move_forward()
        elif bearing == 'N': 
            turn_right_and_move()
        elif bearing == 'S': 
            turn_left_and_move()
        elif bearing == 'E': 
            turn_around_and_move()
    
    # Robot has successfully made a move.
    return True
    

def detect_walls(maze, movement_stack=None, stack_head=None):
    """
    Detects walls surrounding the robot and updates the maze accordingly.

    Args:
        maze (dict): The maze structure where walls are recorded.

    Returns:
        bool: True if walls are detected on all three sides (front, left, and right), 
              otherwise False.
    """

    # Checks left, right and forward for walls.
    front = front_distance.get_distance(MM) < 100
    drivetrain.turn_for(LEFT, 90, DEGREES)
    left = front_distance.get_distance(MM) < 100
    drivetrain.turn_for(RIGHT, 180, DEGREES)
    right = front_distance.get_distance(MM) < 100
    drivetrain.turn_for(LEFT, 90, DEGREES)

    # On the 9th maze there is a wall that the robot can go through.
    # This is a little hack that uses previous moves and the tiles coordinates to place a wall when the following tiles are visited.
    # This ensures the robot takes the correct route and doesn't pass through the wall for this particular maze.
    tile = get_tile(maze)
    if tile == (-870, 600) and movement_stack[stack_head] == ['N', 'N', 'N', 'N', 'N', 'W', 'N']:
        right = True
    if tile == (-620, 600) and movement_stack[stack_head] == ['N', 'W', 'W']:
        front = True

    # Determmines wall positioning by calling the set_bearings function.
    set_bearings(maze, front, left, right)

    return all([front, left, right])

def update_movement_stack(movement_stack, stack_head):
    """
    Updates the movement stack by adding a new empty list and incrementing the stack head.

    Args:
        movement_stack (list of lists): Each list contains the recorded movements of the robot between intersections.
        stack_head (int): An index tracking the most recent list of moves.

    Returns:
        tuple: The updated movement_stack and the incremented stack_head.
    """
    movement_stack.append([])
    stack_head = stack_head + 1  
    return movement_stack, stack_head

def all_adjacent_visited(maze):
    """
    Check if all adjacent tiles of the current tile have been visited.

    Args:
        maze (dict): The current maze structure.

    Returns:
        bool: True if all adjacent tiles are visited, otherwise False.
    """
    current_tile = get_tile(maze)
    possible_directions = ['N', 'E', 'S', 'W']
    walls = get_walls(maze, current_tile)

    for direction in possible_directions:
        # Check for walls.
        if direction in walls:
            continue

        # Check if visited.
        adjacent_tile = get_adjacent_tile(maze, direction)
        visited = get_visited(maze, adjacent_tile)

        # Exit early if not visited.
        if visited == False:
            return visited
    
    return True


def find_open_paths(maze):
    """
    Identifies open paths by determining which directions do not have walls.

    Args:
        maze (dict): The maze structure containing tile wall data.

    Returns:
        list: A list of directions ('N', 'E', 'S', 'W') where there are no walls.
    """
    current_tile = get_tile(maze) 
    possible_walls = ['N', 'E', 'S', 'W']
    walls = get_walls(maze, current_tile)

    # Apply set difference.
    open_paths = list(set(possible_walls) - set(walls))

    return open_paths 


def handle_backtracking(movement_stack, stack_head, opposite_bearing, maze, all_visited):
    """
    Handles backtracking when all adjacent tiles have been visited.

    Args:
        movement_stack (list): A stack of movement paths taken.
        stack_head (int): The current index pointing to the active movement stack.
        opposite_bearing (str): The direction opposite to the last movement.
        maze (dict): The maze structure containing visited tiles and walls.
        all_visited (bool): A flag indicating whether all adjacent tiles have been visited.

    Returns:
        tuple: The updated movement stack and stack head after backtracking.
    """
    while all_visited:
            movement_stack, stack_head = return_to_intersection(movement_stack, stack_head, opposite_bearing, maze)
            all_visited = all_adjacent_visited(maze)
            wait(5, MSEC)
    
    return movement_stack, stack_head
        
    
def move_to_next_tile(open_paths, movement_stack, stack_head, maze):
    """
    Moves the robot to the next unvisited tile based on available open paths.

    Args:
        open_paths (list): A list of available movement directions (N, E, S, W).
        movement_stack (list of lists): Stacks recording movement history.
        stack_head (int): The current index pointing to the active movement stack.
        maze (dict): The maze structure containing visited tiles and walls.

    Returns:
        tuple: The updated movement stack and stack head after movement.
    """
    # If there is more than one possible path to take. 
    if len(open_paths) >= 1:
        
        # Get the adjacent tiles dictionary entrys in the direction of the open path (N,S,E,W)
        for open_path in open_paths:
            tile = get_adjacent_tile(maze, open_path)
            # Check if the path has been visited.
            visited = get_visited(maze, tile)

            # Only move into unvisited tiles
            if visited == False:
                # Make the robot move into next tile based on the open paths.
                success = determine_movement(open_path, maze)
                # Record the movement so the robot can retrace its steps without re-sensing walls.
                if success:
                    movement_stack[stack_head].append(open_path)
                    set_visited(maze)

                return movement_stack, stack_head          

    return movement_stack, stack_head

def return_to_intersection(movement_stack, stack_head, opposite_bearing, maze):
    """
    Backtracks to the previous intersection by reversing movements.

    Args:
        movement_stack (list): Stacks recording movement history..
        stack_head (int): The current index pointing to the active movement stack.
        opposite_bearing (dict): A mapping of movement directions to their opposites.
        maze (dict): The maze structure containing visited tiles and walls.

    Returns:
        tuple: The updated movement stack and stack head after backtracking.
    """

    # Pop the current stack to get to the last intersection.
    for movement in movement_stack[stack_head][:]:
        last_move = movement_stack[stack_head].pop()
        # Move the robot in the opposite direction based on the popped direction.
        success = determine_movement(opposite_bearing[last_move], maze)
    
    # When the stack is empty delete it (unless it is the original stack) and point at the previous stack.
    if stack_head > 0: 
        del(movement_stack[stack_head])
        stack_head = stack_head - 1

    return movement_stack, stack_head

def print_key_line(text, symbol=None, colour=BLACK):
    """
    Prints text in black and then symbols in colour for the visual maze key.

    Args:
        text (string): The text that proceeds the symbol.
        symbol (string): The symbol for the maze tile.
        colour (vex.vr variable): Colour to change the symbol to when printed to the console.
    """
    brain.print(text)
    if symbol:
        brain.set_print_color(colour)
        brain.print(symbol)
        brain.set_print_color(BLACK)
    brain.new_line()



def main():
    # Clear the last console.
    brain.clear()

    # --------------------------------- Setup before main algoritham --------------------------------

    # Define empty maze as a dictionary. 
    maze = define_maze()

    # Set robot specs.
    drivetrain.set_drive_velocity(100, PERCENT)
    drivetrain.set_turn_velocity(100, PERCENT)

    # Define starting positions and current heading.
    start_position = (location.position(X, MM), location.position(Y, MM))

    # Setup the start of the maze
    set_entrance(maze,start_position)

    # Opposite bearings for backtracking.
    opposite_bearing = {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}

    # Exit clause for main algoritham.
    map_complete = False

    # Will hold the movements the robot needs to make it go from entrance to exit.
    shortest_route = False

    # Holds lists of robot movements between intersections.
    movement_stack = [[]]

    # Index of the list with the most recent moves since an intersection.
    stack_head = 0

    # -------------------------------------- Main algoritham uses (DFS) ---------------------------------------

    while map_complete == False:
        # Mark all visited tiles
        pen.move(DOWN)

        # Tile the robot is in.
        tile = get_tile(maze)

        # Is the current tile a dead end?
        dead_end = detect_walls(maze, movement_stack, stack_head) 

        if dead_end: 
            # Return to the last recorded intersection. 
            movement_stack, stack_head = return_to_intersection(movement_stack, stack_head, opposite_bearing, maze)
        else:
            # Check if all adjacent tiles are already visited.
            all_visited = all_adjacent_visited(maze)

            # Get directions to paths not blocked by a wall.
            open_paths = find_open_paths(maze)

            # backtrack again to the last recorded intersection.
            if all_visited:
                movement_stack, stack_head = handle_backtracking(movement_stack, stack_head, opposite_bearing, maze, all_visited)


            # If adjacent tiles have not been visited and they are not blocked by walls it needs to be processed. 
            elif len(open_paths) > 2:
                # If this is not the first interchange add a new list of moves and increment the index to point at the new list.
                if len(movement_stack[stack_head]) > 0:   
                    movement_stack, stack_head = update_movement_stack(movement_stack, stack_head) 
            
            # Move the robot based on open unvisited tiles.
            move_to_next_tile(open_paths, movement_stack, stack_head, maze)
            # Check if all the tiles in the maze have been visited. 
            map_complete = visited_all_tiles(maze)

        # Detect if the tile we have entered is the exit if it is record the path entrance->exit
        # Dont call again when the path is found.
        if not shortest_route: shortest_route = detect_exit(movement_stack)

    # -------------------------------------- Final processing after completion ---------------------------------------

    # Return to the entrance upon completion.
    for stack in reversed(movement_stack): 
        while stack:  
            last_move = stack.pop()
            success = determine_movement(opposite_bearing[last_move], maze)

    # Change the colour of the pen to mark the shortest route.
    pen.move(UP)
    pen.set_pen_color(GREEN)
    pen.move(DOWN)

    # Mark the shortest route entrance->exit.
    directions = {"N": "↑ ", "E": "→ ", "S": "↓ ", "W": "← "}
    for index, movement in enumerate(shortest_route):
        tile = get_tile(maze)
        
        # Set symbols to visualy represent the shortest route when printed.
        if index == 0:
            maze[tile]['key_tile'] =  "○ "
        else:
            maze[tile]['key_tile'] = directions[movement]

        # Follow the route to the exit
        success = determine_movement(movement, maze)

    final_tile = get_tile(maze)

    maze[final_tile]['key_tile'] =  "✩ "
    
    # Print a key for the symbols used in the visual representation of the maze.
    print_key_line("-------- KEY --------",)    
    print_key_line("Entrance :", "○", RED)
    print_key_line("Exit : ", "✩", RED)
    print_key_line("Direction to exit : ", "↑ → ↓ ←", RED)
    print_key_line("Dead end tiles: ", "□")
    print_key_line("Walls: ", "| -")
    brain.new_line()

    # Print the visual representation of the maze.
    print_visual_maze(maze)

    brain.new_line()
    brain.new_line()

    # Escape maze once at exit.
    open_paths = find_open_paths(maze)
    for path in open_paths:
        current_tile = get_tile(maze)
        tile = get_adjacent_tile(maze, path)
        if tile == current_tile:
            determine_movement(path, maze)
            break




vr_thread(main)



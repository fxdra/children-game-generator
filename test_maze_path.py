from collections import deque

from app.services.maze_generator import MazeGenerator


maze = MazeGenerator()
maze.generate()

grid = maze.get_room_grid()
start = maze.get_start_room()
finish = maze.get_finish_room()

queue = deque([start])
visited = {start}

while queue:
    room = queue.popleft()

    for connection in room.connections:
        if connection.is_closed:
            continue

        next_room = connection.remote(room).room

        if next_room in visited:
            continue

        visited.add(next_room)
        queue.append(next_room)

print("START:", start.location)
print("FINISH:", finish.location)
print("TOTAL ROOMS:", len(grid.get_all_rooms()))
print("REACHABLE FROM START:", len(visited))
print("FINISH REACHABLE:", finish in visited)
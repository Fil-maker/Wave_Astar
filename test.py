import pygame
import random
from enum import Enum


class Marker(Enum):
    path = 0
    wall = 1
    start = 2
    goal = 3

    def __str__(self):
        return str(self.name)


class Point:
    def __init__(self, row, col, markers: list[Marker] = []):
        self.row, self.col = row, col
        self.markers = markers

    def get_manh_distance(self, goal):
        return abs(goal.row - self.row) + abs(goal.col - self.col)

    def __eq__(self, other):
        return self.row == other.row and self.col == other.col

    def __str__(self):
        return f"{self.row},{self.col}({'.'.join([str(m) for m in self.markers])})"

    def get_neighbors(self) -> list:
        neighbors: list[Point] = []
        for d_row in range(-1, 2):
            for d_col in range(-1, 2):
                if (d_row != 0 or d_col != 0) and (abs(d_row) != 1 or abs(d_col) != 1):
                    neighbors.append(Point(self.row + d_row, self.col + d_col))
        return neighbors


def get_closest(points: list[Point], goal: Point) -> Point:
    min_distance = None
    closest = None
    for point in points:
        cur_distance = point.get_manh_distance(goal)
        if min_distance is None or cur_distance < min_distance:
            closest = point
    return closest


class Maze:
    def __init__(self, height, width, wall_chance=0.2):
        self.last_changed = None
        self.margin = 2
        self.height, self.width, self.wall_chance = height, width, wall_chance
        self.map: list[list[Point]] = []
        self.start = None
        self.goal = None
        self.generate_field()
        self.generate_walls()
        self.set_path_coords()
        self.cell_width, self.cell_height = None, None

    def get_point(self, point: Point):
        return self.map[point.row][point.col]

    def point_inbounds(self, point: Point):
        return 0 <= point.row < self.height and 0 <= point.col < self.width

    def set_path_coords(self):
        start_row, start_col = 0, 0
        goal_row, goal_col = len(self.map) - 1, len(self.map[0]) - 1
        while Marker.wall in self.map[start_row][start_col].markers \
                or Marker.wall in self.map[goal_row][goal_col].markers \
                or (start_row == goal_row and start_col == goal_col):
            start_row, start_col = random.randint(0, len(self.map) - 1), random.randint(0, len(self.map[0]) - 1)
            goal_row, goal_col = random.randint(0, len(self.map) - 1), random.randint(0, len(self.map[0]) - 1)
        self.map[start_row][start_col].markers.append(Marker.start)
        self.map[goal_row][goal_col].markers.append(Marker.goal)
        self.start = Point(start_row, start_row)
        self.goal = Point(goal_row, goal_col)

    def generate_walls(self):
        for row in range(self.height):
            for col in range(self.width):
                res = random.random()
                if res < self.wall_chance:
                    offset = [0, 0]
                    direction = None
                    if min(col + 1, self.width - col) < min(row + 1, self.height - row):
                        direction = [0, int((col - self.width / 2) / abs(col - self.width / 2))]
                    elif min(col + 1, self.width - col) > min(row + 1, self.height - row):
                        direction = [int((row - self.height / 2) / abs(row - self.height / 2)), 0]
                    if direction is not None:
                        looking = Point(row + offset[0] + direction[0], col + offset[1] + direction[1])
                        while self.point_inbounds(looking):
                            self.map[looking.row][looking.col].markers = [Marker.wall]
                            offset[0], offset[1] = offset[0] + direction[0], offset[1] + direction[1]
                            looking = Point(row + offset[0] + direction[0], col + offset[1] + direction[1])

    def generate_field(self):
        for row in range(self.height):
            self.map.append([])
            for col in range(self.width):
                markers = [Marker.path]
                self.map[-1].append(
                    Point(row, col, markers=markers))

    def draw_on_screen(self, display: pygame.Surface, color, params):
        self.cell_width, self.cell_height = (params[2] - self.margin * (len(self.map[0]) + 1)) / (len(self.map[0])), \
                                            (params[3] - self.margin * (len(self.map) + 1)) / (len(self.map))
        for row in range(len(self.map)):
            for col in range(len(self.map[row])):
                pick = color
                if Marker.start in self.map[row][col].markers:
                    pick = (255, 0, 0)
                elif Marker.goal in self.map[row][col].markers:
                    pick = (0, 255, 0)
                elif Marker.wall in self.map[row][col].markers:
                    pick = (0, 0, 0)
                pygame.draw.rect(display, pick, (
                    params[0] + self.margin + col * (self.cell_width + self.margin),
                    params[1] + self.margin + row * (self.cell_height + self.margin),
                    self.cell_width, self.cell_height
                ))

    def is_cell_drawable(self, point: Point):
        return Marker.goal not in self.get_point(point).markers \
               and Marker.start not in self.get_point(point).markers \
               and (self.last_changed is not None and self.last_changed != point)

    def draw_cell(self, point: Point):
        if self.is_cell_drawable(point):
            self.get_point(point).markers = [Marker.wall]
        self.last_changed = point

    def clear_cell(self, point: Point):
        if self.is_cell_drawable(point):
            self.get_point(point).markers = [Marker.path]
        self.last_changed = point

    def catch_click(self, local_click, actions):
        pr_col = (local_click[0] - self.margin) / (self.cell_width + self.margin)
        pr_row = (local_click[1] - self.margin) / (self.cell_height + self.margin)
        margin_part = self.margin / (self.cell_height + self.margin)
        if int(pr_col) <= pr_col <= int(pr_col + 1) - margin_part \
                and int(pr_row) <= pr_row <= int(pr_row + 1) - margin_part:
            if actions[0] == 1:
                self.draw_cell(Point(int(pr_row), int(pr_col)))
            elif actions[2] == 1:
                self.clear_cell(Point(int(pr_row), int(pr_col)))


# print(get_closest(get_neighbors(Point(0, 0)), Point(0, -2)), sep='\n')
if __name__ == '__main__':
    f = Maze(3, 3)
    f.draw_cell(Point(0, 0))
    for r in f.map:
        for c in r:
            print(c, end='; ')
        print()

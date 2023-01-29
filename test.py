from __future__ import annotations
import pygame
import random
from enum import Enum


class Marker(Enum):
    empty = 0
    wall = 1
    start = 2
    goal = 3
    path = 4
    confirmed = 5
    wrong = 6

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


class PathPoint:
    def __init__(self, point: Point, val: int, parent: PathPoint = None):
        self.point = point
        self.length = val
        self.parent = parent

    def __eq__(self, other):
        return self.point == other.point


def get_closest(points: list[PathPoint], goal: Point) -> PathPoint:
    min_distance = None
    closest = None
    for point in points:
        cur_distance = point.point.get_manh_distance(goal)
        if min_distance is None or cur_distance + point.length < min_distance:
            closest = point
            min_distance = point.length + cur_distance
    return closest


class Maze:
    def __init__(self, height, width, wall_chance=0.2):
        self.last_changed = None
        self.margin = 1
        self.height, self.width, self.wall_chance = height, width, wall_chance
        self.map: list[list[Point]] = []
        self.start: Point
        self.goal: Point
        self.generate_field()
        self.cell_width, self.cell_height = None, None
        # self.generate_walls()
        self.set_path_coords()
        self.is_path_found = False
        self.search_area: list[PathPoint] = [PathPoint(self.start, 0)]
        self.worked_points: list[PathPoint] = []

    def get_point(self, point: Point):
        return self.map[point.row][point.col]

    def is_point_inbounds(self, point: Point):
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
                        while self.is_point_inbounds(looking):
                            self.map[looking.row][looking.col].markers = [Marker.wall]
                            offset[0], offset[1] = offset[0] + direction[0], offset[1] + direction[1]
                            looking = Point(row + offset[0] + direction[0], col + offset[1] + direction[1])

    def generate_field(self):
        for row in range(self.height):
            self.map.append([])
            for col in range(self.width):
                markers = [Marker.empty]
                self.map[-1].append(
                    Point(row, col, markers=markers))

    def draw_on_screen(self, display: pygame.Surface, color, params):
        self.cell_width, self.cell_height = (params[2] - self.margin * (len(self.map[0]) + 1)) / (len(self.map[0])), \
                                            (params[3] - self.margin * (len(self.map) + 1)) / (len(self.map))
        for row in range(len(self.map)):
            for col in range(len(self.map[row])):
                pick = color
                if Marker.wrong in self.map[row][col].markers:
                    pick = (255, 0, 255)
                elif Marker.path in self.map[row][col].markers:
                    pick = (255, 255, 0)
                elif Marker.start in self.map[row][col].markers:
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
        return self.is_point_inbounds(point) and Marker.goal not in self.get_point(point).markers \
               and Marker.start not in self.get_point(point).markers \
               and (self.last_changed is not None and self.last_changed != point)

    def draw_cell(self, point: Point):
        if self.is_cell_drawable(point):
            self.get_point(point).markers = [Marker.wall]
        self.last_changed = point

    def clear_cell(self, point: Point):
        if self.is_cell_drawable(point):
            self.get_point(point).markers = [Marker.empty]
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

    def find_path(self):
        if self.is_path_found:
            return

        closest = get_closest(self.search_area, self.goal)
        if closest is None:
            return
        neighbors = closest.point.get_neighbors()
        is_successful = False
        for n in neighbors:
            is_possible = self.is_point_inbounds(n) and PathPoint(n, closest.length) not in self.worked_points \
                          and Marker.wall not in self.get_point(n).markers \
                          and Marker.start not in self.get_point(n).markers
            for pp in self.search_area:
                if pp.point == n:
                    is_possible = False
            if is_possible:
                if n == self.goal:
                    print(closest.length + 1)
                    self.finish(PathPoint(n, closest.length + 1, closest))
                else:
                    self.search_area.append(PathPoint(n, closest.length + 1, closest))
                    self.get_point(n).markers.append(Marker.path)
                    is_successful = True
        if not is_successful:
            self.get_point(closest.point).markers.append(Marker.wrong)
        # self.get_point(closest.point).markers.append(Marker.wrong)
        self.worked_points.append(closest)
        self.search_area.remove(closest)

    def finish(self, track: PathPoint):
        while track is not None:
            print(track.point)
            track = track.parent


# print(get_closest(get_neighbors(Point(0, 0)), Point(0, -2)), sep='\n')
if __name__ == '__main__':
    f = Maze(3, 3)
    f.draw_cell(Point(0, 0))
    for r in f.map:
        for c in r:
            print(c, end='; ')
        print()

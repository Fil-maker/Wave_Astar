from __future__ import annotations
import pygame
import random
from enum import Enum
from eller_algorithm import generate_labyrinth


def add_colors(color1: tuple[int, int, int], color2: tuple[int, int, int], subtract: bool = False) -> tuple[
    int, int, int]:
    if subtract:
        color2 = (-color2[0], -color2[1], -color2[2])
    return color1[0] + color2[0], color1[1] + color2[1], color1[2] + color2[2]


class Marker(Enum):
    empty = 0
    wall = 1
    start = 2
    goal = 3
    path = 4
    confirmed = 5
    wrong = 6
    current_closest = 7
    custom = 100

    def __str__(self):
        return str(self.name)


class Point:
    def __init__(self, row, col, markers: list[Marker] = []):
        self.row, self.col = row, col
        self.markers = markers
        self.color: tuple[int, int, int] = None

    def get_manh_distance(self, goal):
        return abs(goal.row - self.row) + abs(goal.col - self.col)

    def __eq__(self, other):
        return self.row == other.row and self.col == other.col

    def __str__(self):
        return f"{self.row},{self.col}({'.'.join([str(m) for m in self.markers])})"

    def get_neighbors(self) -> list[Point]:
        neighbors: list[Point] = []
        for d_row in range(-1, 2):
            for d_col in range(-1, 2):
                if (d_row != 0 or d_col != 0) and (abs(d_row) != 1 or abs(d_col) != 1):
                    neighbors.append(Point(self.row + d_row, self.col + d_col))
        return neighbors

    def add_marker(self, marker: Marker) -> None:
        self.markers.append(marker)

    def set_color(self, color: tuple[int, int, int]) -> None:
        if Marker.custom in self.markers:
            self.color = color
        else:
            raise TypeError


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
    def __init__(self, height, width, wall_chance=0.2):  # height and width should be ONLY odd
        self.last_changed = None
        self.margin = 1
        self.start_color = (0x00, 0xF2, 0x60)
        self.end_color = (0x05, 0x75, 0xE6)
        self.working: bool = False
        self.height, self.width, self.wall_chance = height, width, wall_chance
        if self.height % 2 == 0:
            self.height += 1
        if self.width % 2 == 0:
            self.width += 1
        self.map: list[list[Point]] = []
        self.generate_field()
        self.start: Point = None
        self.goal: Point = None
        self.closest: Point = None
        self.last_track_point: PathPoint = None
        self.path: list[Point] = []
        self.cell_width, self.cell_height = None, None
        self.generate_walls()
        self.set_path_coords()
        self.is_path_found = False
        self.path_complete: bool = False  # it means that the self.path variable contains full path
        self.search_area: list[PathPoint] = [PathPoint(self.start, 0)]
        self.worked_points: list[PathPoint] = []

    def get_point(self, point: Point):
        return self.map[point.row][point.col]

    def is_point_inbounds(self, point: Point):
        return 0 <= point.row < self.height and 0 <= point.col < self.width

    def set_path_coords(self):
        start_row, start_col = self.height // 2, 0
        goal_row, goal_col = self.height // 2, len(self.map[0]) - 1
        while Marker.wall in self.map[start_row][start_col].markers \
                or Marker.wall in self.map[goal_row][goal_col].markers \
                or (start_row == goal_row and start_col == goal_col):
            start_row, start_col = random.randint(0, len(self.map) - 1), random.randint(0, len(self.map[0]) - 1)
            goal_row, goal_col = random.randint(0, len(self.map) - 1), random.randint(0, len(self.map[0]) - 1)
        self.map[start_row][start_col].markers.append(Marker.start)
        self.map[goal_row][goal_col].markers.append(Marker.goal)
        self.start = Point(start_row, start_col)
        self.goal = Point(goal_row, goal_col)

    def generate_walls(self):
        matrix_right_borders, matrix_down_borders = generate_labyrinth(self.width // 2, self.height // 2)
        for row in range(self.height):
            for col in range(self.width):
                if row == 0:
                    self.map[row][col].markers = [Marker.wall]
                    continue
                if col == 0:
                    self.map[row][col].markers = [Marker.wall]
                    continue
                if col % 2 == 0 and matrix_right_borders[(row - 1) // 2][(col - 1) // 2]:
                    self.map[row][col].markers = [Marker.wall]
                if row % 2 == 0 and matrix_down_borders[(row - 1) // 2][(col - 1) // 2]:
                    self.map[row][col].markers = [Marker.wall]

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
                if Marker.custom in self.map[row][col].markers:
                    pick = self.map[row][col].color
                elif Marker.start in self.map[row][col].markers:
                    pick = (255, 0, 0)
                elif Marker.goal in self.map[row][col].markers:
                    pick = (0, 255, 0)
                elif Marker.wrong in self.map[row][col].markers:
                    pick = (255, 0, 255)
                elif Marker.confirmed in self.map[row][col].markers:
                    pick = (0, 255, 255)
                elif Marker.current_closest in self.map[row][col].markers:
                    pick = (0x6A, 0x0D, 0xAD)
                elif Marker.path in self.map[row][col].markers:
                    pick = (255, 255, 0)
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
        if not self.working:
            pr_col = (local_click[0] - self.margin) / (self.cell_width + self.margin)
            pr_row = (local_click[1] - self.margin) / (self.cell_height + self.margin)
            margin_part = self.margin / (self.cell_height + self.margin)
            if int(pr_col) <= pr_col <= int(pr_col + 1) - margin_part \
                    and int(pr_row) <= pr_row <= int(pr_row + 1) - margin_part:
                if actions[0] == 1:
                    self.draw_cell(Point(int(pr_row), int(pr_col)))
                elif actions[2] == 1:
                    self.clear_cell(Point(int(pr_row), int(pr_col)))

    def next_step(self):
        if self.working:
            if not self.is_path_found:
                self.find_path()
            elif not self.path_complete:
                self.backtrack_path()
            else:
                self.shift_gradient()

    def find_path(self):
        if self.closest is not None:
            self.closest.markers.remove(Marker.current_closest)
            pass
        closest = get_closest(self.search_area, self.goal)
        self.closest = self.get_point(closest.point)
        self.closest.markers.append(Marker.current_closest)
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
                is_successful = True
                if n == self.goal:
                    self.is_path_found = True
                    self.last_track_point = PathPoint(n, closest.length + 1, closest)
                else:
                    self.search_area.append(PathPoint(n, closest.length + 1, closest))
                    self.get_point(n).markers.append(Marker.path)
        if not is_successful:
            self.get_point(closest.point).markers.append(Marker.wrong)
        # self.get_point(closest.point).markers.append(Marker.wrong)
        self.worked_points.append(closest)
        self.search_area.remove(closest)

    def apply_gradient_first_time(self):
        path_length = len(self.path)
        change = add_colors(self.end_color, self.start_color, True)
        change = change[0] // path_length, change[1] // path_length, change[2] // path_length
        current_color = self.start_color
        for point in self.path:
            point.markers.append(Marker.custom)
            point.set_color(current_color)
            current_color = add_colors(current_color, change)

    def backtrack_path(self):
        if self.last_track_point is not None:
            self.get_point(self.last_track_point.point).markers.append(Marker.confirmed)
            self.path.append(self.get_point(self.last_track_point.point))
            self.last_track_point = self.last_track_point.parent
        else:
            self.path_complete = True
            self.apply_gradient_first_time()

    def shift_gradient(self):
        last_color = self.path[-1].color
        for point in self.path:
            last_color, point.color = point.color, last_color

    def clear_pathpoint_list(self, cur_list: list[PathPoint]) -> None:
        for pathpoint in cur_list:
            cur_point = self.get_point(pathpoint.point)
            if Marker.goal in cur_point.markers:
                cur_point.markers = [Marker.goal]
            elif Marker.start in cur_point.markers:
                cur_point.markers = [Marker.start]
            else:
                cur_point.markers = [Marker.empty]

    def clear_point_list(self, cur_list: list[Point]) -> None:
        for point in cur_list:
            cur_point = self.get_point(point)
            if Marker.goal in cur_point.markers:
                cur_point.markers = [Marker.goal]
            elif Marker.start in cur_point.markers:
                cur_point.markers = [Marker.start]
            else:
                cur_point.markers = [Marker.empty]

    def clear_path(self):
        self.working = False
        self.closest = None
        self.is_path_found = False
        self.path_complete = False
        self.clear_pathpoint_list(self.search_area)
        self.search_area = [PathPoint(self.start, 0)]
        self.clear_pathpoint_list(self.worked_points)
        self.worked_points = []
        self.clear_point_list(self.path)
        self.path = []


# print(get_closest(get_neighbors(Point(0, 0)), Point(0, -2)), sep='\n')
if __name__ == '__main__':
    f = Maze(5, 5)
    f.draw_cell(Point(0, 0))
    for r in f.map:
        for c in r:
            print(c, end='; ')
        print()

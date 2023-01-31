import pygame
from test import Maze, Point
from pygame_utils import Button, Switch, Counter, Text

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)


class ScreenObject:
    def __init__(self, left, top, width, height, draw_object):
        self.params = self.left, self.top, self.width, self.height, = left, top, width, height
        self.draw_object = draw_object

    def is_click_in(self, click) -> bool:
        return 0 <= click[0] - self.left <= self.width and 0 <= click[1] - self.top <= self.height

    def catch_click(self, click, buttons):
        if self.is_click_in(click):
            self.draw_object.catch_click((click[0] - self.left, click[1] - self.top), buttons)

    def draw(self, display):
        self.draw_object.draw_on_screen(display, (250, 250, 250), self.params)
        self.width, self.height = self.draw_object.size


class LabyrinthDisplay:
    def __init__(self):
        WIDTH = 15
        HEIGHT = 15
        self.maze = Maze(2 * WIDTH // 2 + 1, 2 * HEIGHT // 2 + 1)

        self.maze_obj = ScreenObject(
            20, 20, 560, 560, self.maze)
        self.solve_button = ScreenObject(
            600, 20, 150, 50, Button("Решить лабиринт", lambda: self.maze.change_solving()))
        self.regenerate_button = ScreenObject(
            600, 70, 150, 50, Button("Перестроить лабиринт", lambda: self.maze.rebuild()))
        self.empty_button = ScreenObject(
            600, 120, 150, 50, Button("Пустое поле", lambda: self.maze.rebuild(walls=False)))
        self.alternate_path = ScreenObject(
            600, 150, 150, 50, Switch(
                "Режим редактирования точек пути", lambda: self.maze.change_editing(), (0, 150, 0),
                is_on=self.maze.is_alternative))

        odd_up, odd_down = lambda x: (x // 2 + 1) * 2 + 1, lambda x: (x // 2) * 2 - 1
        self.field_from_title = ScreenObject(600, 418, 0, 0, Text("Создать поле"))
        self.rows_form = ScreenObject(600, 459, 0, 0, Counter("Высота ", 11, up_method=odd_up, down_method=odd_down))
        self.columns_form = ScreenObject(600, 509, 0, 0, Counter("Ширина ", 11, up_method=odd_up, down_method=odd_down))
        self.confirm_creation = ScreenObject(600, 559, 0, 0, Button("Создать", self.recreate_maze))

        self.objects = [
            self.maze_obj, self.solve_button, self.regenerate_button, self.empty_button, self.alternate_path,
            self.field_from_title, self.rows_form, self.columns_form, self.confirm_creation]

        size = width, height = 800, 600
        self.FPS = 10

        pygame.init()
        self.clock = pygame.time.Clock()
        self.DISPLAY = pygame.display.set_mode(size, 0)
        pygame.display.set_caption("Лабиринты")

    def recreate_maze(self):
        self.maze = Maze(self.rows_form.draw_object.value, self.columns_form.draw_object.value)
        self.maze_obj.draw_object = self.maze
        self.alternate_path.draw_object.is_on = self.maze.is_alternative

    def paint(self):
        pygame.draw.rect(self.DISPLAY, (135, 196, 250), (0, 0, *self.DISPLAY.get_size()))
        pygame.draw.rect(self.DISPLAY, (185, 160, 5), (590, 0, 560, 223))
        pygame.draw.rect(self.DISPLAY, (185, 160, 5), (590, 408, 560, 560))
        pygame.draw.rect(self.DISPLAY, (0, 0, 0), (20, 20, 560, 560))
        for obj in self.objects:
            obj.draw(self.DISPLAY)
        # pygame.draw.rect(screen, BLUE, (200, 150, 100, 50))

    def main(self):
        running = True
        hold = False
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    hold = True
                    self.maze.last_changed = Point(-1, -1)
                    if event.button == 1:
                        for obj in self.objects:
                            obj.catch_click(event.pos, (1, 0, 0))
                    elif event.button == 3:
                        for obj in self.objects:
                            obj.catch_click(event.pos, (0, 0, 1))
                if hold and event.type == pygame.MOUSEMOTION:
                    self.maze_obj.catch_click(event.pos, event.buttons)
                if event.type == pygame.MOUSEBUTTONUP:
                    hold = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    self.maze.change_solving()
            self.paint()
            self.maze.next_step()
            pygame.display.flip()
            self.clock.tick(self.FPS)


if __name__ == '__main__':
    LabyrinthDisplay().main()

import pygame

from test import Maze, Point

WHITE = (255, 255, 255)
BLUE = (0, 0, 255)


class ScreenObject:
    def __init__(self, left, top, width, height, draw_object):
        self.left, self.top, self.width, self.height, = left, top, width, height
        self.draw_object = draw_object

    def is_click_in(self, click) -> bool:
        return 0 <= click[0] - self.left <= self.width and 0 <= click[1] - self.top <= self.height

    def catch_click(self, click, buttons):
        if self.is_click_in(click):
            self.draw_object.catch_click((click[0] - self.left, click[1] - self.top), buttons)

    def draw(self, display, params):
        self.draw_object.draw_on_screen(display, (250, 250, 250), params)


def paint(screen: pygame.Surface, objects):
    pygame.draw.rect(screen, (135, 206, 250), (0, 0, 800, 600))
    # pygame.draw.rect(screen, BLUE, (200, 150, 100, 50))


def main():
    maze = Maze(20, 20)
    obj = ScreenObject(20, 20, 560, 560, maze)
    size = width, height = 800, 600
    FPS = 60
    time_to_frame = 1000 / FPS
    running = True
    pygame.init()
    clock = pygame.time.Clock()
    DISPLAY = pygame.display.set_mode(size, 0)
    hold = False
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                hold = True
                maze.last_changed = Point(-1, -1)
                if event.button == 1:
                    obj.catch_click(event.pos, (1, 0, 0))
                if event.button == 3:
                    obj.catch_click(event.pos, (0, 0, 1))
            if hold and event.type == pygame.MOUSEMOTION:
                obj.catch_click(event.pos, event.buttons)
            if event.type == pygame.MOUSEBUTTONUP:
                hold = False
        paint(DISPLAY, size)
        pygame.draw.rect(DISPLAY, (0, 0, 0), (20, 20, 560, 560))
        obj.draw(DISPLAY, (20, 20, 560, 560))
        maze.draw_on_screen(DISPLAY, (235, 235, 235), (20, 20, 560, 560))
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == '__main__':
    main()

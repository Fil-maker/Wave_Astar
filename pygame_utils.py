import pygame


class Text:
    def __init__(self, text):
        self.text = text
        pygame.font.init()
        self.myfont = pygame.font.SysFont("monospace", 18)
        self.size = 0, 0

    def blit_text(self, surface, pos, color=pygame.Color('black')):
        words = [word.split(' ') for word in self.text.splitlines()]  # 2D array where each row is a list of words.
        space = self.myfont.size(' ')[0]  # The width of a space.
        max_width, max_height = surface.get_size()
        x, y = pos
        width = 0
        for line in words:
            for word in line:
                word_surface = self.myfont.render(word, 1, color)
                word_width, word_height = word_surface.get_size()
                if x + word_width >= max_width:
                    width = max(x - pos[0], width)
                    x = pos[0]  # Reset the x.
                    y += word_height  # Start on new row.
                surface.blit(word_surface, (x, y))
                x += word_width + space
                width = max(x - pos[0], width)
            x = pos[0]  # Reset the x.
            y += word_height  # Start on new row.
        return width, y - pos[1]

    def draw_on_screen(self, display: pygame.Surface, color, params):
        self.size = self.blit_text(display, (params[0], params[1]))

    def catch_click(self, local_click, buttons):
        pass


class Button(Text):
    def __init__(self, text, func):
        super().__init__(text)
        self.func = func

    def draw_on_screen(self, display: pygame.Surface, color, params):
        pygame.draw.rect(display, color, (params[0], params[1], *self.size))
        pygame.draw.rect(
            display, (0, 0, 0), (params[0], params[1], *self.size), width=1)
        self.size = self.blit_text(display, (params[0], params[1]))

    def catch_click(self, local_click, buttons):
        if buttons[0] == 1:
            self.func()


class Switch(Button):
    def __init__(self, text, func, alt_color, is_on=False):
        super().__init__(text, func)
        self.alt_color = alt_color
        self.is_on = is_on

    def draw_on_screen(self, display: pygame.Surface, color, params):
        if self.is_on is False:
            pygame.draw.rect(display, (150, 0, 0), (params[0], params[1], *self.size))
        else:
            pygame.draw.rect(display, self.alt_color, (params[0], params[1], *self.size))
        pygame.draw.rect(
            display, (0, 0, 0), (params[0], params[1], *self.size), width=1)
        self.size = self.blit_text(display, (params[0], params[1]))

    def catch_click(self, local_click, buttons):
        self.is_on = not self.is_on
        super(Switch, self).catch_click(local_click, buttons)


class Counter(Text):
    def __init__(self, question, value=0, up_method=None, down_method=None):
        super().__init__(value)
        self.small_size = None
        self.up_size = None
        self.down_size = None
        self.question = question
        self.value = value
        self.up_method = up_method
        self.down_method = down_method
        self.up_button = Button('▲', self.increase)
        self.down_button = Button('▼', self.decrease)

    def increase(self):
        if self.up_method is None:
            self.value += 1
        else:
            self.value = self.up_method(self.value)

    def decrease(self):
        if self.value > 1:
            if self.down_method is None:
                self.value -= 1
            else:
                self.value = self.down_method(self.value)

    def draw_on_screen(self, display: pygame.Surface, color, params):
        self.text = self.question + str(self.value)
        self.small_size = self.blit_text(display, (params[0], params[1]))
        self.up_button.draw_on_screen(
            display, (255, 255, 255), (params[0] + self.small_size[0], params[1]))
        self.up_size = self.up_button.size
        self.down_button.draw_on_screen(
            display, (255, 255, 255), (params[0] + self.small_size[0], params[1] + 5 + self.up_size[1]))
        self.down_size = self.down_button.size
        self.size = self.small_size[0] + self.up_size[0], self.small_size[1] + self.down_size[1] + 5

    def catch_click(self, local_click, buttons):
        self.calc_click(local_click, buttons)

    def calc_click(self, local_click, buttons):
        if self.small_size[0] <= local_click[0] <= self.size[0] and 0 <= local_click[1] <= self.up_size[1]:
            self.up_button.catch_click(
                (local_click[0] - self.small_size[0], local_click[1]), buttons)
        if self.small_size[0] <= local_click[0] <= self.size[0] \
                and self.up_size[1] + 5 <= local_click[1] <= self.up_size[1] + 5 + self.up_size[1]:
            self.down_button.catch_click(
                (local_click[0] - self.small_size[0], local_click[1] - 5 - self.up_size[1]), buttons)

import pygame

pygame.init()

POPUP_WINDOW_SIZE = (300, 100)
MAIN_WINDOW_SIZE = (1350, 580)

FONT = pygame.font.SysFont('Arial', 20)

colors = {
    "white": (255,255,255),
    "black": (  0,  0,  0),
    "green": ( 44,186,  0),
    "red":   (255,  0,  0),
    "blue":  ( 57,158,235),
    "gray":  ( 69, 69, 69),
}

class Window:
    def __init__(self, name, size, bg_color):
        self.size = size
        self.bg_color = bg_color
        self.window = pygame.display.set_mode(size)
        self.window.fill(colors[bg_color])
        pygame.display.set_caption(name)
    
    def warning(self, text):
        self.window.fill(self.bg_color)
        text = FONT.render(text, True, colors["black"])
        text_container = text.get_rect()
        text_container.center = (self.size[0]//2,self.size[1]//2)
        self.window.blit(text, text_container)
        pygame.display.flip()


class Widget:

    active_widget = False

    def __init__(self, parent, x, y, width, height):
        self.parent = parent
        self.x=x
        self.y=y
        self.width = width
        self.height = height

    def coursor_on_widget(self, coursor_position):
        coursor_x, coursor_y = coursor_position

        if (coursor_x >= self.x and 
            coursor_x <= self.x + self.width and
            coursor_y >= self.y and 
            coursor_y <= self.y + self.height):
            return True
        else:
            return False
    

class Button(Widget):
    def __init__(self, parent, x, y, width, height, text, command):
        super().__init__(parent, x, y, width, height)
        self.bg_color = colors["blue"]
        self.ct_color = colors["black"]
        self.text = text
        self.command = command
        self.display()

    def display(self):
        pygame.draw.rect(self.parent, self.ct_color, pygame.Rect(self.x-3,self.y-3,self.width+6,self.height+6))
        pygame.draw.rect(self.parent, self.bg_color, pygame.Rect(self.x,self.y,self.width,self.height))
        text = FONT.render(self.text, True, colors["black"])
        text_container = text.get_rect()
        text_container.center = (self.x+self.width//2,self.y+self.height//2)
        self.parent.blit(text, text_container)
        
    def click(self, coursor_position):
        if self.coursor_on_widget(coursor_position) and not Widget.active_widget:
            Widget.active_widget = self
            self.command()


class Slider(Widget):
    def __init__(self, parent, x, y, width, height):
        super().__init__(parent, x, y, width, height)
        self.bg_color = colors["blue"]
        self.ct_color = colors["black"]
        self.sa_color = colors["white"]
        self.display()

    def display(self, coursor_position=(None,None)):
        if coursor_position==(None,None):
            coursor_position = (None, self.y+self.height//2)

        outer_radius = self.width//2
        inner_radius = outer_radius-1
        upper_circle_center = (self.x+outer_radius, self.y+outer_radius)
        lower_circle_center = (self.x+outer_radius, self.y+self.height-outer_radius)
        sliding_circle_center = (self.x+outer_radius, min(lower_circle_center[1],max(coursor_position[1],upper_circle_center[1])))

        pygame.draw.circle(self.parent, self.ct_color, upper_circle_center, outer_radius+2)
        pygame.draw.circle(self.parent, self.ct_color, lower_circle_center, outer_radius+2)
        pygame.draw.rect(self.parent, self.ct_color, (self.x-3,self.y+outer_radius-3,self.width+6,self.height-self.width+6))

        pygame.draw.circle(self.parent, self.sa_color, upper_circle_center, inner_radius)
        pygame.draw.circle(self.parent, self.sa_color, lower_circle_center, inner_radius)
        pygame.draw.rect(self.parent, self.sa_color, (self.x,self.y+outer_radius,self.width,self.height-self.width))

        pygame.draw.circle(self.parent, self.ct_color, sliding_circle_center, outer_radius+2)
        pygame.draw.circle(self.parent, self.bg_color, sliding_circle_center, inner_radius)
        
        self.z = 10*((lower_circle_center[1]-sliding_circle_center[1])/(lower_circle_center[1]-upper_circle_center[1]))-5
        slider_text = FONT.render(str(round(self.z, 1)), True, colors["black"])
        slider_text_rect = slider_text.get_rect()
        slider_text_rect.center = sliding_circle_center
        self.parent.blit(slider_text, slider_text_rect)

    def click(self, coursor_position):
        if self.coursor_on_widget(coursor_position) and (not Widget.active_widget or Widget.active_widget == self):
            Widget.active_widget = self
            self.display(coursor_position)


class Canvas(Widget):
    def __init__(self, parent, x, y, width, height):
        super().__init__(parent, x, y, width, height)

        self.busy = False
        self.color = colors["black"]
        self.points = []
        self.lines = []

        pygame.draw.rect(self.parent, colors["black"], (self.x-3,self.y-3,self.width+6,self.height+6))
        pygame.draw.rect(self.parent, colors["white"], (self.x,self.y,self.width,self.height))

    def add_point(self, coursor_position, prev_coursor_position):
        self.points.append(coursor_position)
        self.lines.append([prev_coursor_position, coursor_position])

    def draw(self, coursor_position):
        if self.coursor_on_widget(coursor_position) and (not Widget.active_widget or Widget.active_widget == self):

            Widget.active_widget = self

            if not self.busy:
                self.busy = True
                self.prev = coursor_position
                self.points.append(coursor_position)
                pygame.draw.circle(self.parent, colors["black"], self.points[-1], 2)
                return [0, coursor_position]

            elif coursor_position != self.prev:
                self.add_point(coursor_position, self.prev)
                pygame.draw.circle(self.parent, colors["black"], coursor_position, 2)
                pygame.draw.line(self.parent, colors["black"], self.prev, coursor_position, 5)
                self.prev = coursor_position
                return [1, coursor_position]


    def end_draw(self, coursor_position):
        self.busy = False
        return [2, coursor_position]

    def update_drawings(self, progress):
        for done_point in progress:
            if len(self.points)!=0:
                if self.points[0] == (done_point[0],done_point[1]):
                    pygame.draw.circle(self.parent, colors["green"], self.points[0], 2)
                    del self.points[0]
            if len(self.lines)!=0:
                if self.lines[0][1] == (done_point[0],done_point[1]):
                    pygame.draw.line(self.parent, colors["green"], self.lines[0][0], self.lines[0][1], 5)
                    del self.lines[0]

    def clear(self):
        self.points = []
        self.lines = []
        pygame.draw.rect(self.parent, colors["black"], (self.x-3,self.y-3,self.width+6,self.height+6))
        pygame.draw.rect(self.parent, colors["white"], (self.x,self.y,self.width,self.height))
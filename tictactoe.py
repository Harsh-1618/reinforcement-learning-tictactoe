from os import environ
environ["PYGAME_HIDE_SUPPORT_PROMPT"] = '1'
import time
import random
import pygame
import numpy as np
from button import Button


class TictactoeConstants:
    __slots__ = ()
    HEIGHT_PADDING = 15
    WIDTH_PADDING = 15
    GRID_LINE_WIDTH = 5


class TicTacToe:
    ttt_constants = TictactoeConstants()
    height_padding = ttt_constants.HEIGHT_PADDING
    width_padding = ttt_constants.WIDTH_PADDING
    grid_line_width = ttt_constants.GRID_LINE_WIDTH

    def __init__(self,
                screen,
                clock,
                ttt_dim,
                screen_height,
                screen_width,
                window_name="TicTacToe",
                window_icon="./images/grid_icon.png",
                img_x_path="./images/x_transparent_edited.png",
                img_o_path="./images/o_transparent_edited.png"):
        self.screen = screen
        self.clock = clock
        self.ttt_dim = ttt_dim
        self.screen_height = screen_height
        self.screen_width = screen_width
        
        pygame.display.set_caption(window_name)
        pygame.display.set_icon(pygame.image.load(window_icon))

        self.row_grid_color = "#101010"
        self.col_grid_color = "#101010"
        self.logic_grid = np.zeros((self.ttt_dim, self.ttt_dim), dtype=np.int8) # 1 for 'X', -1 for 'O' and 0 if position is available
        self.player = 1
        self.angles = np.zeros((self.ttt_dim, self.ttt_dim), dtype=np.int16)

        # size reduction factor to compensate for grid line width and image rotation
        self.reduction_factor_x = 25 - 3*(self.ttt_dim-3) # 'X' is big and has sharp corners which interfere with other 'X', so bigger reduction
        self.reduction_factor_o = 1 # 'O' does not interfere that much
        self.img_x_resize_value = (self.screen_height//self.ttt_dim) - 2*((TicTacToe.grid_line_width+self.reduction_factor_x)//2)
        self.img_o_resize_value = (self.screen_height//self.ttt_dim) - 2*((TicTacToe.grid_line_width+self.reduction_factor_o)//2)

        self.img_x = pygame.image.load(img_x_path)
        self.img_o = pygame.image.load(img_o_path)
        self.img_x = pygame.transform.scale(self.img_x, (self.img_x_resize_value, self.img_x_resize_value))
        self.img_o = pygame.transform.scale(self.img_o, (self.img_o_resize_value, self.img_o_resize_value))

    @staticmethod
    def get_color(color):
        rgb = [int(color[1:3], 16), int(color[3:5], 16), int(color[5:], 16)]
        index = random.randint(0,2)
        # rgb[index] = (rgb[index] + 1) if rgb[index] < 255 else 16
        # rgb[index] = (rgb[index] + 5) if rgb[index] < 251 else 16
        rgb[index] = (rgb[index] + (index+1)) if rgb[index] < 253 else 16 # gives better visuals
        result = f"#{hex(rgb[0])}{hex(rgb[1])}{hex(rgb[2])}"

        return result.replace("0x", "")

    def calculate_grid(self):
        self.rows = []
        self.cols = []
    
        row_start = self.screen_height//self.ttt_dim
        width_blank_space_start = self.screen_width-self.screen_height

        for i in range(self.ttt_dim-1):
            self.rows.append(
                ((TicTacToe.width_padding, row_start*(i+1)),
                (self.screen_width-width_blank_space_start-TicTacToe.width_padding, row_start*(i+1))))
            self.cols.append(
                ((row_start*(i+1), TicTacToe.height_padding),
                (row_start*(i+1), self.screen_height-TicTacToe.height_padding)))

        self.height_intervals = [0] + [row[0][1] for row in self.rows] + [self.screen_height]
        self.width_intervals = [0] + [col[0][0] for col in self.cols] + [self.screen_width-width_blank_space_start]

    def render_grid(self):
        self.row_grid_color = TicTacToe.get_color(self.row_grid_color)
        self.col_grid_color = TicTacToe.get_color(self.col_grid_color)

        for row in self.rows:
            pygame.draw.line(self.screen, self.row_grid_color, start_pos=row[0], end_pos=row[1], width=TicTacToe.grid_line_width)
        for col in self.cols:
            pygame.draw.line(self.screen, self.col_grid_color, start_pos=col[0], end_pos=col[1], width=TicTacToe.grid_line_width)

    def add_xo_to_grid(self, mouse_down_pos):
        row_val = None
        col_val = None

        for i in range(len(self.height_intervals)-1):
            if (mouse_down_pos[1] > self.height_intervals[i]) and (mouse_down_pos[1] < self.height_intervals[i+1]):
                row_val = i
        for i in range(len(self.width_intervals)-1):
            if (mouse_down_pos[0] > self.width_intervals[i]) and (mouse_down_pos[0] < self.width_intervals[i+1]):
                col_val = i

        if (row_val is not None) and (col_val is not None):
            if self.logic_grid[row_val][col_val] == 0:
                self.logic_grid[row_val][col_val] = self.player
                self.player = -self.player

    def render_xo(self):
        x_pos = np.where(self.logic_grid==1)
        o_pos = np.where(self.logic_grid==-1)

        for i in range(len(x_pos[0])):
            loc = (self.width_intervals[x_pos[1][i]]+((TicTacToe.grid_line_width+self.reduction_factor_x)//2), self.height_intervals[x_pos[0][i]]+((TicTacToe.grid_line_width+self.reduction_factor_x)//2))
            img_x = pygame.transform.rotate(self.img_x, self.angles[x_pos[0][i], x_pos[1][i]]) # counter-clockwise rotation
            img_x_rect = img_x.get_rect(center=(loc[0]+self.img_x_resize_value//2, loc[1]+self.img_x_resize_value//2))
            self.screen.blit(img_x, img_x_rect)
            self.angles[x_pos[0][i], x_pos[1][i]] = (self.angles[x_pos[0][i], x_pos[1][i]] + 1)%360

        for i in range(len(o_pos[0])):
            loc = (self.width_intervals[o_pos[1][i]]+((TicTacToe.grid_line_width+self.reduction_factor_o)//2), self.height_intervals[o_pos[0][i]]+((TicTacToe.grid_line_width+self.reduction_factor_o)//2))
            img_o = pygame.transform.rotate(self.img_o, -self.angles[o_pos[0][i], o_pos[1][i]]) # clockwise rotation
            img_o_rect = img_o.get_rect(center=(loc[0]+self.img_o_resize_value//2, loc[1]+self.img_o_resize_value//2))
            self.screen.blit(img_o, img_o_rect)
            self.angles[o_pos[0][i], o_pos[1][i]] = (self.angles[o_pos[0][i], o_pos[1][i]] + 1)%360

    def run(self):
        self.calculate_grid()
        
        while True:
            mouse_down_pos = None

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 0
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: # 1 is for left mouse click
                        mouse_down_pos = event.pos

            self.screen.fill("black")

            if mouse_down_pos:
                self.add_xo_to_grid(mouse_down_pos)

            self.render_xo()
            self.render_grid()

            pygame.display.flip()

            self.clock.tick(60) # limits FPS to 60


class MainScreen:
    def __init__(self, screen=None, clock=None, ttt_dim=None, screen_height=None, screen_width=None, window_icon="./images/main_icon.png",):
        self.ttt_dim = 9 if ttt_dim is None else ttt_dim
        self.screen_height = 480 if screen_height is None else screen_height
        self.screen_width = 640 if screen_width is None else screen_width

        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height)) if screen is None else screen
        self.clock = pygame.time.Clock() if clock is None else clock

        pygame.display.set_icon(pygame.image.load(window_icon))

        self.play_button = Button(self.screen, "./images/dormant.png", "./images/play.png", (201,101), self.screen_width//2, self.screen_height//4, "Play")
        self.options_button = Button(self.screen, "./images/dormant.png", "./images/options.png", (201,101), self.screen_width//2, 2*self.screen_height//4, "Options")
        self.exit_button = Button(self.screen, "./images/dormant.png", "./images/exit.png", (201,101), self.screen_width//2, 3*self.screen_height//4, "Exit")

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return (0,)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.play_button.check_for_click(event.pos):
                        return 1, self.screen, self.clock, self.ttt_dim, self.screen_height, self.screen_width
                    elif self.options_button.check_for_click(event.pos):
                        return (2,)
                    elif self.exit_button.check_for_click(event.pos):
                        return (3,)

            self.screen.fill("black")
            self.play_button.render_button()
            self.options_button.render_button()
            self.exit_button.render_button()

            self.play_button.hover_detection(pygame.mouse.get_pos())
            self.options_button.hover_detection(pygame.mouse.get_pos())
            self.exit_button.hover_detection(pygame.mouse.get_pos())

            pygame.display.flip()
            self.clock.tick(60)


if __name__ == "__main__":
    pygame.init()
    running = True

    while running:
        ms = MainScreen()
        button_value, *ttt_blueprint = ms.run()
        
        if button_value == 0:
            running = False
        elif button_value == 1:
            ttt = TicTacToe(*ttt_blueprint)
            ttt_value = ttt.run()
            if ttt_value == 0:
                running = False
            elif ttt_value == 1:
                pass
        elif button_value == 2:
            pass
        elif button_value == 3:
            tq = pygame.mixer.Sound("./sounds/thank_you.wav")
            tq.play()
            time.sleep(tq.get_length()-0.7)
            running = False
    # SCREEN_HEIGHT = 480
    # SCREEN_WIDTH = 640
    # # SCREEN_HEIGHT = 640
    # # SCREEN_WIDTH = 1280
    # TICTACTOE_DIM = 3
    pygame.quit()

from os import environ
environ["PYGAME_HIDE_SUPPORT_PROMPT"] = '1'
import time
import random
import pygame
import numpy as np
from utils import Button, Label


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

    sounds = (pygame.mixer.Sound("./sounds/click_x.wav"),
            pygame.mixer.Sound("./sounds/click_o.wav"),
            pygame.mixer.Sound("./sounds/win_x.wav"),
            pygame.mixer.Sound("./sounds/win_o.wav"),
            pygame.mixer.Sound("./sounds/tie.wav"),
            pygame.mixer.Sound("./sounds/click_forward.wav"),
            pygame.mixer.Sound("./sounds/click_backward.wav"),
            pygame.mixer.Sound("./sounds/button_hover.wav"))

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
        self.is_game_terminated = False
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
        
        self.wins_x = 0
        self.wins_o = 0
        self.ties = 0
        self.label_x_color = "white"
        self.label_o_color = "white"
        self.label_x = Label(self.screen, self.screen_width-(self.screen_width-self.screen_height)//2, self.screen_height//6, self.label_x_color, (int(150*self.screen_width/640), int(50*self.screen_height/480)), f"X wins: {self.wins_x}")
        self.label_o = Label(self.screen, self.screen_width-(self.screen_width-self.screen_height)//2, 2*self.screen_height//6, self.label_o_color, (int(150*self.screen_width/640), int(50*self.screen_height/480)), f"O wins: {self.wins_o}")
        self.label_ties = Label(self.screen, self.screen_width-(self.screen_width-self.screen_height)//2, 3*self.screen_height//6, "white", (int(120*self.screen_width/640), int(50*self.screen_height/480)), f"Ties: {self.ties}")

        self.reset_button = Button(self.screen, self.screen_width-(self.screen_width-self.screen_height)//2, 4*self.screen_height//6, "./images/dormant.png", "./images/play.png", (int(100*self.screen_width/640), int(50*self.screen_height/480)), "Reset")
        self.back_button = Button(self.screen, self.screen_width-(self.screen_width-self.screen_height)//2, 5*self.screen_height//6, "./images/dormant.png", "./images/exit.png", (int(100*self.screen_width/640), int(50*self.screen_height/480)), "Back")

        self.reset_hover_detection = [0,0] # used to detect the moment mouse hovers on reset button to play hover sound
        self.back_hover_detection = [0,0]

    @staticmethod
    def get_color(color):
        rgb = [int(color[1:3], 16), int(color[3:5], 16), int(color[5:], 16)]
        index = random.randint(0,2)
        # rgb[index] = (rgb[index] + 1) if rgb[index] < 255 else 16
        # rgb[index] = (rgb[index] + 5) if rgb[index] < 251 else 16
        rgb[index] = (rgb[index] + (index+1)) if rgb[index] < 253 else 16 # gives better visuals
        result = f"#{hex(rgb[0])}{hex(rgb[1])}{hex(rgb[2])}"

        return result.replace("0x", "")

    def set_label_xo_color(self):
        if self.wins_x == self.wins_o:
            self.label_x_color = "white"
            self.label_o_color = "white"
        elif self.wins_x > self.wins_o:
            self.label_x_color = "green"
            self.label_o_color = "red"
        else:
            self.label_x_color = "red"
            self.label_o_color = "green"

    def check_win(self, row_val, col_val):
        self.is_game_terminated = np.sum(self.logic_grid[row_val,:]) == self.player * self.ttt_dim or \
            np.sum(self.logic_grid[:,col_val]) == self.player * self.ttt_dim or \
            np.sum(np.diag(np.flip(self.logic_grid, axis=0))) == self.player * self.ttt_dim or \
            np.sum(np.diag(self.logic_grid)) == self.player * self.ttt_dim

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
            if (self.logic_grid[row_val][col_val] == 0) and (not self.is_game_terminated):
                self.logic_grid[row_val][col_val] = self.player
                if self.player == 1:
                    TicTacToe.sounds[0].play()
                else:
                    TicTacToe.sounds[1].play()

                self.check_win(row_val, col_val)
                if self.is_game_terminated:
                    if self.player == 1:
                        TicTacToe.sounds[2].play().fadeout(3000)
                        self.wins_x += 1
                    else:
                        TicTacToe.sounds[3].play().fadeout(3000)
                        self.wins_o += 1
                    self.set_label_xo_color()
                    self.label_x = Label(self.screen, self.screen_width-(self.screen_width-self.screen_height)//2, self.screen_height//6, self.label_x_color, (int(150*self.screen_width/640), int(50*self.screen_height/480)), f"X wins: {self.wins_x}")
                    self.label_o = Label(self.screen, self.screen_width-(self.screen_width-self.screen_height)//2, 2*self.screen_height//6, self.label_o_color, (int(150*self.screen_width/640), int(50*self.screen_height/480)), f"O wins: {self.wins_o}")
                elif len(np.where(self.logic_grid==0)[0]) == 0:
                    TicTacToe.sounds[4].play()
                    self.ties += 1
                    self.label_ties = Label(self.screen, self.screen_width-(self.screen_width-self.screen_height)//2, 3*self.screen_height//6, "white", (int(120*self.screen_width/640), int(50*self.screen_height/480)), f"Ties: {self.ties}")
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
                    return (0,)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: # 1 is for left mouse click
                        mouse_down_pos = event.pos

                    if self.reset_button.check_for_click(event.pos):
                        TicTacToe.sounds[5].play()
                        self.logic_grid[:] = 0
                        self.is_game_terminated = False
                        self.player = 1
                    elif self.back_button.check_for_click(event.pos):
                        TicTacToe.sounds[6].play()
                        return (1,)

            self.screen.fill("black")

            if mouse_down_pos:
                self.add_xo_to_grid(mouse_down_pos)

            self.render_xo()
            self.render_grid()

            self.reset_button.render_button()
            self.back_button.render_button()
            self.label_x.render_text()
            self.label_o.render_text()
            self.label_ties.render_text()
            
            self.reset_hover_detection[0] = self.reset_hover_detection[1]
            self.reset_hover_detection[1] = self.reset_button.hover_detection(pygame.mouse.get_pos())
            if self.reset_hover_detection == [0,1]:
                TicTacToe.sounds[7].play()
            self.back_hover_detection[0] = self.back_hover_detection[1]
            self.back_hover_detection[1] = self.back_button.hover_detection(pygame.mouse.get_pos())
            if self.back_hover_detection == [0,1]:
                TicTacToe.sounds[7].play()

            pygame.display.flip()

            self.clock.tick(60) # limits FPS to 60


class MenuMaker:
    sounds = (pygame.mixer.Sound("./sounds/click_forward.wav"),
            pygame.mixer.Sound("./sounds/click_backward.wav"),
            pygame.mixer.Sound("./sounds/button_hover.wav"))

    def __init__(self, screen, clock, ttt_dim, screen_height, screen_width, btn_args, rtn_values):
        self.screen = screen
        self.clock = clock
        self.screen_height = screen_height
        self.screen_width = screen_width
        self.rtn_values = rtn_values

        self.button_res_resize_height = self.screen_height/480 # 640x480 standard resolution
        self.button_res_resize_width = self.screen_width/640

        self.buttons = [Button(self.screen, self.screen_width//2, (i+1)*self.screen_height//(len(btn_args)+1), "./images/dormant.png", btn_args[i][0], (int(btn_args[i][1][0]*self.button_res_resize_width), int(btn_args[i][1][1]*self.button_res_resize_height)), btn_args[i][2]) for i in (range(len(btn_args)))]
        self.return_stuff = [(rtn_values[i], self.screen, self.clock, ttt_dim, self.screen_height, self.screen_width) for i in (range(len(rtn_values)))]

        self.hover_sound_list = [[0,0] for i in range(len(self.buttons))] # used to detect the moment mouse hovers on any button to play hover sound
        # if we play when mouse is on button, then it will play the sound indefinately till the mouse is on the button.

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return (0,)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for i in range(len(self.buttons)):
                        if self.buttons[i].check_for_click(event.pos):
                            if (i == len(self.buttons)-1) and (type(self)==MenuMaker):
                                MenuMaker.sounds[1].play()
                            else:
                                MenuMaker.sounds[0].play()
                            return self.return_stuff[i]

            self.screen.fill("black")
            for i in range(len(self.buttons)):
                self.buttons[i].render_button()
                self.hover_sound_list[i][0] = self.hover_sound_list[i][1]
                self.hover_sound_list[i][1] = self.buttons[i].hover_detection(pygame.mouse.get_pos())
                if self.hover_sound_list[i] == [0,1]:
                    MenuMaker.sounds[2].play()

            pygame.display.flip()
            self.clock.tick(60)


class MainMenu(MenuMaker):
    def __init__(self, ttt_dim, screen_height, screen_width, btn_args, rtn_values, window_icon="./images/main_icon.png"):
        self.ttt_dim = 3 if ttt_dim is None else ttt_dim
        self.screen_height = 480 if screen_height is None else screen_height
        self.screen_width = 640 if screen_width is None else screen_width

        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.clock = pygame.time.Clock()

        pygame.display.set_icon(pygame.image.load(window_icon))

        super().__init__(self.screen, self.clock, self.ttt_dim, self.screen_height, self.screen_width, btn_args, rtn_values)


def make_btn_args(hover_img_path, resize_dim, text):
    if (diff := len(text)-len(hover_img_path)) != 0:
        hover_img_path = [hover_img_path[-2]]*(diff+1) + [hover_img_path[-1]]

    if len(resize_dim) == 1:
        resize_dim = [resize_dim[0]]*len(text)

    return tuple(zip(hover_img_path, resize_dim, text))

def get_all_menu_args():
    main_hover_img_path = ("./images/play.png", "./images/options.png", "./images/exit.png")
    main_resize_dim = ((201,101),)
    main_text = ("Play", "Options", "Exit")
    main_btn_args = make_btn_args(main_hover_img_path, main_resize_dim, main_text)
    main_rtn_values = (1, 2, -1)

    options_hover_img_path = ("./images/options.png", "./images/exit.png")
    options_resize_dim = ((301,101), (301,101), (201,101))
    options_text = ("Set Grid Dimension", "Set Game Resolution", "Back")
    options_btn_args = make_btn_args(options_hover_img_path, options_resize_dim, options_text)
    options_rtn_values = (1, 2, -1)

    grid_hover_img_path = ("./images/options.png", "./images/exit.png")
    grid_resize_dim = ((201,51),)
    grid_text = ("3 x 3", "4 x 4", "5 x 5", "6 x 6", "7 x 7", "8 x 8", "9 x 9", "Back")
    grid_btn_args = make_btn_args(grid_hover_img_path, grid_resize_dim, grid_text)
    grid_rtn_values = (3, 4, 5, 6, 7, 8, 9, -1)

    res_hover_img_path = ("./images/options.png", "./images/exit.png")
    res_resize_dim = ((201,51),)
    res_text = ("640 x 480", "720 x 540", "800 x 600", "1280 x 640", "1280 x 720", "1920 x 1080", "Back")
    res_btn_args = make_btn_args(res_hover_img_path, res_resize_dim, res_text)
    res_rtn_values = ((640,480), (720,540), (800,600), (1280,640), (1280,720), (1920,1080), -1)

    return (main_btn_args, main_rtn_values), (options_btn_args, options_rtn_values), (grid_btn_args, grid_rtn_values), (res_btn_args, res_rtn_values)


if __name__ == "__main__":
    pygame.init()
    main_args, options_args, grid_args, res_args = get_all_menu_args()
    bgm = pygame.mixer.Sound("./sounds/bgm.mp3")
    bgm.play(loops=-1)
    
    ttt_dim = None
    screen_height = None
    screen_width = None

    running = True
    while running:
        mm = MainMenu(ttt_dim, screen_height, screen_width, *main_args)
        mm_bv, *ttt_blueprint = mm.run() # mm_bv -> main menu button value
        if mm_bv == 0:
            running = False
        elif mm_bv == -1:
            tq = pygame.mixer.Sound("./sounds/thank_you.wav") # tq -> thank you
            tq.play()
            time.sleep(tq.get_length()-0.7)
            running = False
        elif mm_bv == 1:
            bgm.set_volume(0.05)
            ttt = TicTacToe(*ttt_blueprint)
            ttt_bv, *ttt_blueprint = ttt.run()
            bgm.set_volume(1)
            if ttt_bv == 0:
                running = False
            elif ttt_bv == 1:
                continue
        elif mm_bv == 2:
            while True:
                om = MenuMaker(*ttt_blueprint, *options_args)
                om_bv, *ttt_blueprint = om.run()
                if om_bv == 0:
                    running = False
                    break
                elif om_bv == -1:
                    break
                elif om_bv == 1:
                    gm = MenuMaker(*ttt_blueprint, *grid_args)
                    gm_bv, *ttt_blueprint = gm.run()
                    if gm_bv == 0:
                        running = False
                        break
                    elif gm_bv == -1:
                        continue
                    else:
                        ttt_dim = gm_bv
                        break
                elif om_bv == 2:
                    rm = MenuMaker(*ttt_blueprint, *res_args)
                    rm_bv, *ttt_blueprint = rm.run()
                    if rm_bv == 0:
                        running = False
                        break
                    elif rm_bv == -1:
                        continue
                    else:
                        screen_width, screen_height = rm_bv
                        break

    pygame.quit()

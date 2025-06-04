from os import environ
environ["PYGAME_HIDE_SUPPORT_PROMPT"] = '1'
import copy
import pygame
import numpy as np
from utils import Button, Label, Label_with_bg
from pygame.surfarray import make_surface
from cube.cube_cython import build_cube, render_cube

pygame.init()


class TicTacToe_3d:
    sounds = (pygame.mixer.Sound("./sounds/click_x.wav"),
            pygame.mixer.Sound("./sounds/click_o.wav"),
            pygame.mixer.Sound("./sounds/win_x.wav"),
            pygame.mixer.Sound("./sounds/win_o.wav"),
            pygame.mixer.Sound("./sounds/tie.wav"),
            pygame.mixer.Sound("./sounds/click_forward.wav"),
            pygame.mixer.Sound("./sounds/click_backward.wav"),
            pygame.mixer.Sound("./sounds/button_hover.wav"))

    sub_cubes = ["0_0_0","1_0_0","2_0_0","0_1_0","1_1_0","2_1_0","0_2_0","1_2_0","2_2_0",
            "0_0_1","1_0_1","2_0_1","0_1_1","1_1_1","2_1_1","0_2_1","1_2_1","2_2_1",
            "0_0_2","1_0_2","2_0_2","0_1_2","1_1_2","2_1_2","0_2_2","1_2_2","2_2_2"]
    
    neutral_color = (51,46,44) # RGB
    x_color = 204,85,0
    o_color = (8,143,143)

    def __init__(self,
            screen,
            clock,
            ttt_dim,
            screen_height,
            screen_width,
            window_name="3D TicTacToe",
            window_icon="./images/grid_icon.png"):
        self.screen = screen
        self.clock = clock
        self.ttt_dim = 3 if ttt_dim != 3 else ttt_dim # only using 3 cause 3x3x3 already has 27 subcubes, 4x4x4 will have 64! which is too much!
        self.screen_height = screen_height
        self.screen_width = screen_width
        
        pygame.display.set_caption(window_name)
        pygame.display.set_icon(pygame.image.load(window_icon))

        self.A = 0
        self.prev_A = None
        self.B = 0
        self.prev_B = None
        self.cube_screen = None
        self.prev_cube_screen = None
        self.cube_info = build_cube(screen_height=self.screen_height,
                                    screen_width=self.screen_height,
                                    linear_spacing=0.5,
                                    sub_cube_spacing=2,
                                    pixel_scaling=20,
                                    r1_unit=1.0,
                                    k2_unit=20.0)

        self.sub_cube_colors = {cube:TicTacToe_3d.neutral_color for cube in TicTacToe_3d.sub_cubes}
        self.show_points = None

        self.logic_grid = np.zeros((self.ttt_dim, self.ttt_dim, self.ttt_dim), dtype=np.int8) # 1 for 'X', -1 for 'O' and 0 if position is available
        self.prev_logic_grid = None
        self.is_game_terminated = False
        self.player = 1

        self.wins_x = 0
        self.wins_o = 0
        self.ties = 0
        self.label_x_color = (255,255,255)
        self.label_o_color = (255,255,255)
        self.instruction1 = Label(self.screen, self.screen_width-(self.screen_width-self.screen_height)//2, (self.screen_height//7)-15, (164,63,79), "Click cube to play")
        self.instruction2 = Label(self.screen, self.screen_width-(self.screen_width-self.screen_height)//2, self.screen_height//7, (164,63,79), "Use arrow keys")
        self.instruction3 = Label(self.screen, self.screen_width-(self.screen_width-self.screen_height)//2, (self.screen_height//7)+15, (164,63,79), "to rotate cube")
        self.label_x = Label_with_bg(self.screen, self.screen_width-(self.screen_width-self.screen_height)//2, 2*self.screen_height//7, self.label_x_color, (int(150*self.screen_width/640), int(50*self.screen_height/480)), f"X wins: {self.wins_x}")
        self.label_o = Label_with_bg(self.screen, self.screen_width-(self.screen_width-self.screen_height)//2, 3*self.screen_height//7, self.label_o_color, (int(150*self.screen_width/640), int(50*self.screen_height/480)), f"O wins: {self.wins_o}")
        self.label_ties = Label_with_bg(self.screen, self.screen_width-(self.screen_width-self.screen_height)//2, 4*self.screen_height//7, (255,255,255), (int(120*self.screen_width/640), int(50*self.screen_height/480)), f"Ties: {self.ties}")

        self.reset_button = Button(self.screen, self.screen_width-(self.screen_width-self.screen_height)//2, 5*self.screen_height//7, "./images/dormant.png", "./images/play.png", (int(100*self.screen_width/640), int(50*self.screen_height/480)), "Reset")
        self.back_button = Button(self.screen, self.screen_width-(self.screen_width-self.screen_height)//2, 6*self.screen_height//7, "./images/dormant.png", "./images/exit.png", (int(100*self.screen_width/640), int(50*self.screen_height/480)), "Back")

        self.reset_hover_detection = [0,0] # used to detect the moment mouse hovers on reset button to play hover sound
        self.back_hover_detection = [0,0]

    def set_label_xo_color(self):
        if self.wins_x == self.wins_o:
            self.label_x_color = (255,255,255)
            self.label_o_color = (255,255,255)
        elif self.wins_x > self.wins_o:
            self.label_x_color = (0,255,0)
            self.label_o_color = (255,0,0)
        else:
            self.label_x_color = (255,0,0)
            self.label_o_color = (0,255,0)

    def check_win(self, row_val, col_val, channel_val):
        win_requirement = self.player * self.ttt_dim

        # checking along row, column and channel (total 9x3 = 27 possibilities, checking only 3 since we know the position player played)
        row_col_channel = np.sum(self.logic_grid[row_val,col_val,:]) == win_requirement or \
                        np.sum(self.logic_grid[row_val,:,channel_val]) == win_requirement or \
                        np.sum(self.logic_grid[:,col_val,channel_val]) == win_requirement

        # checking along face diagonals (total 3x3x2 = 18 possibilities, 2 diagonals across 9 faces. checking only 3 faces)
        def planner_diag_win(planner_grid):
            return np.sum(np.diag(planner_grid)) == win_requirement or \
            np.sum(np.diag(np.flip(planner_grid, axis=0))) == win_requirement
            
        planner_diagonals = planner_diag_win(self.logic_grid[row_val,:,:]) or \
                            planner_diag_win(self.logic_grid[:,col_val,:]) or \
                            planner_diag_win(self.logic_grid[:,:,channel_val])

        # checking along long 3d diagonals passing through center of the cube. (total 4 possibilities, checking all)
        cross_square1 = np.zeros((self.ttt_dim, self.ttt_dim))
        cross_square2 = np.zeros((self.ttt_dim, self.ttt_dim))

        cross_square1[:,0] = self.logic_grid[:, 0, 0]
        cross_square1[:,1] = self.logic_grid[:, 1, 1]
        cross_square1[:,2] = self.logic_grid[:, 2, 2]

        cross_square2[:,0] = self.logic_grid[:, 0, 2]
        cross_square2[:,1] = self.logic_grid[:, 1, 1]
        cross_square2[:,2] = self.logic_grid[:, 2, 0]

        long_diagonals = planner_diag_win(cross_square1) or planner_diag_win(cross_square2)

        self.is_game_terminated = row_col_channel or planner_diagonals or long_diagonals

    def inf_ttt_3d_extension(self, row_val, col_val, channel_val, sub_cube):
        pass

    def add_xo_to_grid(self, mouse_down_pos):
        for key in self.show_points.keys():
            if key == mouse_down_pos:
                x_val, y_val, z_val = [int(c) for c in (self.show_points[key][1]).split("_")]
                y_val = self.ttt_dim-1-y_val # need to flip y since logic_grid starts from top left but our cube's starting point is bottom left! (as it follows co-ordinates system)
                row_val, col_val, channel_val = y_val, x_val, z_val # since x axis or x_val is actually corresponding to columns and y axis to rows

                if (self.logic_grid[row_val, col_val, channel_val] == 0) and (not self.is_game_terminated): # once game is terminated, you can't put xo to empty places
                    self.logic_grid[row_val, col_val, channel_val] = self.player

                    # for infinite ttt
                    self.inf_ttt_3d_extension(row_val, col_val, channel_val, self.show_points[key][1])

                    if self.player == 1:
                        TicTacToe_3d.sounds[0].play()
                        self.sub_cube_colors[self.show_points[key][1]] = TicTacToe_3d.x_color
                    else:
                        TicTacToe_3d.sounds[1].play()
                        self.sub_cube_colors[self.show_points[key][1]] = TicTacToe_3d.o_color

                    self.check_win(row_val, col_val, channel_val)
                    if self.is_game_terminated:
                        if self.player == 1:
                            TicTacToe_3d.sounds[2].play().fadeout(3000)
                            self.wins_x += 1
                        else:
                            TicTacToe_3d.sounds[3].play().fadeout(3000)
                            self.wins_o += 1
                        self.set_label_xo_color()
                        self.label_x = Label_with_bg(self.screen, self.screen_width-(self.screen_width-self.screen_height)//2, 2*self.screen_height//7, self.label_x_color, (int(150*self.screen_width/640), int(50*self.screen_height/480)), f"X wins: {self.wins_x}")
                        self.label_o = Label_with_bg(self.screen, self.screen_width-(self.screen_width-self.screen_height)//2, 3*self.screen_height//7, self.label_o_color, (int(150*self.screen_width/640), int(50*self.screen_height/480)), f"O wins: {self.wins_o}")
                    elif len(np.where(self.logic_grid==0)[0]) == 0:
                        TicTacToe_3d.sounds[4].play()
                        self.ties += 1
                        self.label_ties = Label_with_bg(self.screen, self.screen_width-(self.screen_width-self.screen_height)//2, 4*self.screen_height//7, (255,255,255), (int(120*self.screen_width/640), int(50*self.screen_height/480)), f"Ties: {self.ties}")
                    self.player = -self.player

                break # will match only once, so no need to continue loop

    def render_xo(self):
        if (self.A == self.prev_A) and (self.B == self.prev_B) and (np.all(self.logic_grid == self.prev_logic_grid)): # A, B check is for rotation, logic_grid check is for changing color of subcube
            pass
        else:
            self.cube_screen, self.show_points = render_cube(*self.cube_info, self.A, self.B, self.sub_cube_colors)
            self.cube_screen = np.transpose(self.cube_screen, (1, 0, 2)) # HxW -> WxH, cause pygame is WxH
            self.prev_A = self.A # it's fine to do this since A and B are floats
            self.prev_B = self.B
            self.prev_cube_screen = self.cube_screen # it's fine since the function call overwrites cube_screen and it's allocated at new address
            self.prev_logic_grid = copy.deepcopy(self.logic_grid) # need to have copy since logic_grid is changed inplace
        cube_surface = make_surface(self.cube_screen)
        self.screen.blit(cube_surface, (0, 0))

    def reset_parameters(self):
        self.logic_grid[:] = 0
        self.is_game_terminated = False
        self.player = 1
        self.A = 0
        self.B = 0
        self.sub_cube_colors = {cube:TicTacToe_3d.neutral_color for cube in TicTacToe_3d.sub_cubes}

    def run(self):
        while True:
            mouse_down_pos = None

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return (0,)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.B += 0.2
                    elif event.key == pygame.K_RIGHT:
                        self.B -= 0.2
                    elif event.key == pygame.K_UP:
                        self.A += 0.2
                    elif event.key == pygame.K_DOWN:
                        self.A -= 0.2
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: # 1 is for left mouse click
                        mouse_down_pos = event.pos

                    if self.reset_button.check_for_click(event.pos):
                        TicTacToe_3d.sounds[5].play()
                        self.reset_parameters()
                    elif self.back_button.check_for_click(event.pos):
                        TicTacToe_3d.sounds[6].play()
                        return (1,)

            self.screen.fill("black")

            if mouse_down_pos:
                self.add_xo_to_grid(mouse_down_pos)

            self.render_xo()

            self.reset_button.render_button()
            self.back_button.render_button()
            self.instruction1.render_text()
            self.instruction2.render_text()
            self.instruction3.render_text()
            self.label_x.render_text()
            self.label_o.render_text()
            self.label_ties.render_text()

            self.reset_hover_detection[0] = self.reset_hover_detection[1]
            self.reset_hover_detection[1] = self.reset_button.hover_detection(pygame.mouse.get_pos())
            if self.reset_hover_detection == [0,1]:
                TicTacToe_3d.sounds[7].play()
            self.back_hover_detection[0] = self.back_hover_detection[1]
            self.back_hover_detection[1] = self.back_button.hover_detection(pygame.mouse.get_pos())
            if self.back_hover_detection == [0,1]:
                TicTacToe_3d.sounds[7].play()

            pygame.display.flip()

            self.clock.tick(60) # limits FPS to 60


class InfiniteTicTacToe_3d(TicTacToe_3d):
    def __init__(self, *args):
        super().__init__(*args)
        self.memory_length = 12 # for 3x3x3 = 27, ig 12 is fine.
        self.memory = {i:None for i in range(self.memory_length)}
        self.current_number = 0
    
    def inf_ttt_3d_extension(self, row_val, col_val, channel_val, sub_cube):
        if (pos:=self.memory[self.current_number]) is not None:
            self.logic_grid[pos[0], pos[1], pos[2]] = 0
            self.sub_cube_colors[pos[3]] = InfiniteTicTacToe_3d.neutral_color

        self.memory[self.current_number] = (row_val, col_val, channel_val, sub_cube)
        self.current_number = (self.current_number + 1) % self.memory_length

    def reset_parameters(self):
        super().reset_parameters()
        self.memory = {i:None for i in range(self.memory_length)}
        self.current_number = 0
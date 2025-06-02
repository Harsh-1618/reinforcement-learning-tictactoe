from os import environ
environ["PYGAME_HIDE_SUPPORT_PROMPT"] = '1'
import pygame
import numpy as np
from utils import Button, Label
from pygame.surfarray import make_surface
from cube.cube_cython import build_cube, render_cube

pygame.init()


class TicTacToe_3d:
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
        self.ttt_dim = ttt_dim # not using it as of now cause 3x3x3 is only supported
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
        sub_cubes = ["-1_-1_-1","0_-1_-1","1_-1_-1","-1_0_-1","0_0_-1","1_0_-1","-1_1_-1","0_1_-1","1_1_-1",
                    "-1_-1_0","0_-1_0","1_-1_0","-1_0_0", "0_0_0", "1_0_0","-1_1_0","0_1_0","1_1_0",
                    "-1_-1_1","0_-1_1","1_-1_1","-1_0_1","0_0_1","1_0_1","-1_1_1","0_1_1","1_1_1"]
        self.sub_cube_colors = {cube:(61,61,61) for cube in sub_cubes}
        self.show_points = None

    def add_xo_to_grid(self, mouse_down_pos):
        for key in self.show_points.keys():
            if key == mouse_down_pos:
                self.sub_cube_colors[self.show_points[key][1]] = (0, 255, 0)
                self.render_xo(check=False)

    def render_xo(self, check=True):
        if check and (self.A == self.prev_A) and (self.B == self.prev_B):
            self.cube_screen = self.prev_cube_screen
        else:
            self.cube_screen, self.show_points = render_cube(*self.cube_info, self.A, self.B, self.sub_cube_colors)
            self.cube_screen = np.transpose(self.cube_screen, (1, 0, 2)) # HxW -> WxH, cause pygame is WxH
            self.prev_A = self.A
            self.prev_B = self.B
            self.prev_cube_screen = self.cube_screen
        cube_surface = make_surface(self.cube_screen)
        self.screen.blit(cube_surface, (0, 0))

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

            self.screen.fill("black")

            if mouse_down_pos:
                self.add_xo_to_grid(mouse_down_pos)

            self.render_xo()

            pygame.display.flip()

            self.clock.tick(60) # limits FPS to 60

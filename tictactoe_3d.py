from os import environ
environ["PYGAME_HIDE_SUPPORT_PROMPT"] = '1'
import pygame
import numpy as np
from utils import Button, Label
from pygame.surfarray import make_surface
from cube import build_cube, render_cube

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

    def render_xo(self):
        if (self.A == self.prev_A) and (self.B == self.prev_B):
            self.cube_screen = self.prev_cube_screen
        else:
            self.cube_screen = np.transpose(render_cube(*self.cube_info, self.A, self.B), (1, 0, 2)) # HxW -> WxH, cause pygame is WxH
            self.prev_A = self.A
            self.prev_B = self.B
            self.prev_cube_screen = self.cube_screen
        cube_surface = make_surface(self.cube_screen)
        self.screen.blit(cube_surface, (0, 0))

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return (0,)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.B += 0.2
                    elif event.key == pygame.K_RIGHT:
                        self.B -= 0.2
                    elif event.key == pygame.K_UP:
                        self.A += 0.2
                    elif event.key == pygame.K_DOWN:
                        self.A -= 0.2

            self.screen.fill("black")

            self.render_xo()

            pygame.display.flip()

            self.clock.tick(60) # limits FPS to 60

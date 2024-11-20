import pygame
import random
import numpy as np
import time

pygame.init()

SCREEN_HEIGHT = 480
SCREEN_WIDTH = 640
# SCREEN_HEIGHT = 640
# SCREEN_WIDTH = 1280
HEIGHT_PADDING = 15
WIDTH_PADDING = 15
TICTACTOE_DIM = 3
GRID_LINE_WIDTH = 5


def get_color(color):
    rgb = [int(color[1:3], 16), int(color[3:5], 16), int(color[5:], 16)]
    index = random.randint(0,2)
    # rgb[index] = (rgb[index] + 1) if rgb[index] < 255 else 16
    # rgb[index] = (rgb[index] + 5) if rgb[index] < 251 else 16
    rgb[index] = (rgb[index] + (index+1)) if rgb[index] < 253 else 16 # gives better visuals
    result = f"#{hex(rgb[0])}{hex(rgb[1])}{hex(rgb[2])}"
    return result.replace("0x", "")

def add_xo_to_grid(player, logic_grid, mouse_down_pos, height_intervals, width_intervals):
    row_val = None
    col_val = None

    for i in range(len(height_intervals)-1):
        if (mouse_down_pos[1] > height_intervals[i]) and (mouse_down_pos[1] < height_intervals[i+1]):
            row_val = i

    for i in range(len(width_intervals)-1):
        if (mouse_down_pos[0] > width_intervals[i]) and (mouse_down_pos[0] < width_intervals[i+1]):
            col_val = i

    # print(mouse_down_pos, row_val, col_val)

    if (row_val is not None) and (col_val is not None):
        if logic_grid[row_val][col_val] == 0:
            logic_grid[row_val][col_val] = player

def calculate_grid(height_padding, width_padding, tictactoe_dim=3):
    rows = []
    cols = []
    width, height = pygame.display.get_window_size()
    row_start = height//tictactoe_dim
    width_blank_space_start = (width-height)//2

    for i in range(tictactoe_dim-1):
        rows.append(((width_blank_space_start+width_padding, row_start*(i+1)), (width-width_blank_space_start-width_padding, row_start*(i+1))))
        cols.append(((width_blank_space_start+row_start*(i+1), height_padding), (width_blank_space_start+row_start*(i+1), height-height_padding)))

    return rows, cols

def draw_grid(screen, rows, cols, row_grid_color, col_grid_color, grid_line_width):
    for row in rows:
        pygame.draw.line(screen, row_grid_color, start_pos=row[0], end_pos=row[1], width=grid_line_width)
        # pygame.draw.circle(screen, row_grid_color, center=row[0], radius=10, draw_top_left=True, draw_bottom_left=True)
        # pygame.draw.circle(screen, row_grid_color, center=row[1], radius=10, draw_top_right=True, draw_bottom_right=True)

    for col in cols:
        pygame.draw.line(screen, col_grid_color, start_pos=col[0], end_pos=col[1], width=grid_line_width)
        # pygame.draw.circle(screen, col_grid_color, center=col[0], radius=10, draw_top_left=True, draw_top_right=True)
        # pygame.draw.circle(screen, col_grid_color, center=col[1], radius=10, draw_bottom_left=True, draw_bottom_right=True)

def render_xo(screen, logic_grid, height_intervals, width_intervals, img_x, img_o, grid_line_width, angle, img_x_resize_value, img_o_resize_value, extra_x_factor):
    img_x = pygame.transform.rotate(img_x, angle)
    img_o = pygame.transform.rotate(img_o, angle)
    x_pos = np.where(logic_grid==1)
    o_pos = np.where(logic_grid==-1)

    for i in range(len(x_pos[0])):
        c = (width_intervals[x_pos[1][i]]+((grid_line_width+extra_x_factor)//2), height_intervals[x_pos[0][i]]+((grid_line_width+extra_x_factor)//2))
        img_x_rect = img_x.get_rect(center=(c[0]+img_x_resize_value/2,c[1]+img_x_resize_value/2))
        screen.blit(img_x, img_x_rect)
        # screen.blit(img_x, (width_intervals[x_pos[1][i]]+((grid_line_width+1)//2), height_intervals[x_pos[0][i]]+((grid_line_width+1)//2)))

    for i in range(len(o_pos[0])):
        c = (width_intervals[o_pos[1][i]]+((grid_line_width+1)//2), height_intervals[o_pos[0][i]]+((grid_line_width+1)//2))
        img_o_rect = img_o.get_rect(center=(c[0]+img_o_resize_value/2,c[1]+img_o_resize_value/2))
        screen.blit(img_o, img_o_rect)
        # screen.blit(img_o, (width_intervals[o_pos[1][i]]+((grid_line_width+1)//2), height_intervals[o_pos[0][i]]+((grid_line_width+1)//2)))

pygame.display.set_caption("TicTacToe")
pygame.display.set_icon(pygame.image.load("./images/o.png"))
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
running = True
rows, cols = calculate_grid(HEIGHT_PADDING, WIDTH_PADDING, tictactoe_dim=TICTACTOE_DIM)
height_intervals = [0] + [row[0][1] for row in rows] + [SCREEN_HEIGHT]
width_intervals = [(SCREEN_WIDTH-SCREEN_HEIGHT)//2] + [col[0][0] for col in cols] + [SCREEN_WIDTH-((SCREEN_WIDTH-SCREEN_HEIGHT)//2)]
# print(height_intervals, width_intervals)
logic_grid = np.zeros((TICTACTOE_DIM, TICTACTOE_DIM)) # 1 for 'X', -1 for 'O' and 0 for position available
# print(logic_grid)
angle = 0
extra_x_factor = 25 - 3*(TICTACTOE_DIM-3)
img_o_resize_value = (SCREEN_HEIGHT//TICTACTOE_DIM) - 2*((GRID_LINE_WIDTH+1)//2)
img_x_resize_value = (SCREEN_HEIGHT//TICTACTOE_DIM) - 2*((GRID_LINE_WIDTH+extra_x_factor)//2)
img_x = pygame.image.load("./images/x_transparent_edited.png")
img_x = pygame.transform.scale(img_x, (img_x_resize_value, img_x_resize_value))
img_o = pygame.image.load("./images/o_transparent_edited.png")
img_o = pygame.transform.scale(img_o, (img_o_resize_value, img_o_resize_value))

row_grid_color = "#101010"
col_grid_color = "#101010"

while running:
    mouse_down_pos = None

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            tq = pygame.mixer.Sound("./sounds/thank_you.wav")
            tq.play()
            time.sleep(tq.get_length()-0.5)

            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # left mouse click
                mouse_down_pos = event.pos

    screen.fill("black")
    row_grid_color = get_color(row_grid_color)
    col_grid_color = get_color(col_grid_color)

    if mouse_down_pos:
        add_xo_to_grid(1, logic_grid, mouse_down_pos, height_intervals, width_intervals)

    render_xo(screen, logic_grid, height_intervals, width_intervals, img_x, img_o, GRID_LINE_WIDTH, angle, img_x_resize_value, img_o_resize_value, extra_x_factor)

    draw_grid(screen, rows, cols, row_grid_color, col_grid_color, GRID_LINE_WIDTH)
    
    # img = pygame.image.load("./images/x.png")
    # img = pygame.transform.scale(img, (100,100))
    # img = pygame.transform.rotate(img, angle)
    # img_rect = img.get_rect(center=(320,240))
    # screen.blit(img, img_rect)
    angle += 1

    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()

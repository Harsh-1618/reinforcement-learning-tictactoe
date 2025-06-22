from os import environ
environ["PYGAME_HIDE_SUPPORT_PROMPT"] = '1'
import pygame
from menus import MainMenu, MenuMaker
from tictactoe import TicTacToe, InfiniteTicTacToe
from tictactoe_3d import TicTacToe_3d, InfiniteTicTacToe_3d
import time


def make_btn_args(hover_img_path, resize_dim, text):
    if (diff := len(text)-len(hover_img_path)) != 0:
        hover_img_path = [hover_img_path[-2]]*(diff+1) + [hover_img_path[-1]]

    if len(resize_dim) == 1:
        resize_dim = [resize_dim[0]]*len(text)

    return tuple(zip(hover_img_path, resize_dim, text))

def get_all_menu_args():
    main_hover_img_path = ("./images/play.png", "./images/play.png", "./images/play.png", "./images/play.png", "./images/options.png", "./images/exit.png")
    main_resize_dim = ((201,61), (301,61), (201,61), (301,61), (201,61), (201,61))
    main_text = ("TicTacToe", "Infinite TicTacToe", "3D TicTacToe", "Infinite 3D TicTacToe", "Options", "Exit")
    main_btn_args = make_btn_args(main_hover_img_path, main_resize_dim, main_text)
    main_rtn_values = (1, 2, 3, 4, 5, -1)

    options_hover_img_path = ("./images/options.png", "./images/exit.png")
    options_resize_dim = ((301,81), (301,81), (301,81), (201,81))
    options_text = ("Set Grid Dimension", "Set Game Resolution", "Gameplay Settings", "Back")
    options_btn_args = make_btn_args(options_hover_img_path, options_resize_dim, options_text)
    options_rtn_values = (1, 2, 3, -1)

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

    you_first_hover_img_path = ("./images/options.png", "./images/options.png")
    you_first_resize_dim = ((211,71),)
    you_first_text = ("p vs MiniMax AI", "p vs MCTS")
    you_first_btn_args = make_btn_args(you_first_hover_img_path, you_first_resize_dim, you_first_text)
    you_first_rtn_values = ("p_minimax", "p_mcts")

    oneVone_hover_img_path = ("./images/options.png", "./images/exit.png")
    oneVone_resize_dim = ((101,71), (101,71))
    oneVone_text = ("p vs p", "Back")
    oneVone_btn_args = make_btn_args(oneVone_hover_img_path, oneVone_resize_dim, oneVone_text)
    oneVone_rtn_values = ("p_p", -1)

    ai_first_hover_img_path = ("./images/options.png", "./images/options.png")
    ai_first_resize_dim = ((211,71),)
    ai_first_text = ("MiniMax AI vs p", "MCTS vs p")
    ai_first_btn_args = make_btn_args(ai_first_hover_img_path, ai_first_resize_dim, ai_first_text)
    ai_first_rtn_values = ("minimax_p", "mcts_p")

    return (main_btn_args, main_rtn_values), (options_btn_args, options_rtn_values), (grid_btn_args, grid_rtn_values), (res_btn_args, res_rtn_values), \
        (you_first_btn_args, you_first_rtn_values), (oneVone_btn_args, oneVone_rtn_values), (ai_first_btn_args, ai_first_rtn_values)


if __name__ == "__main__":
    pygame.init()
    main_args, options_args, grid_args, res_args, you_first_args, oneVone_args, ai_first_args = get_all_menu_args()
    bgm = pygame.mixer.Sound("./sounds/bgm.mp3")
    bgm.play(loops=-1)
    
    ttt_dim = None
    screen_height = None
    screen_width = None
    ai = None
    player_first = None

    running = True
    while running:
        mm = MainMenu(ttt_dim, screen_height, screen_width, (main_args,))
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
            ttt = TicTacToe(*ttt_blueprint, ai, player_first)
            ttt_bv, *ttt_blueprint = ttt.run()
            bgm.set_volume(1)
            if ttt_bv == 0:
                running = False
            elif ttt_bv == 1:
                continue
        elif mm_bv == 2:
            bgm.set_volume(0.05)
            ttt = InfiniteTicTacToe(*ttt_blueprint, ai, player_first)
            ttt_bv, *ttt_blueprint = ttt.run()
            bgm.set_volume(1)
            if ttt_bv == 0:
                running = False
            elif ttt_bv == 1:
                continue
        elif mm_bv == 3:
            bgm.set_volume(0.05)
            ttt = TicTacToe_3d(*ttt_blueprint, ai, player_first)
            ttt_bv, *ttt_blueprint = ttt.run()
            bgm.set_volume(1)
            if ttt_bv == 0:
                running = False
            elif ttt_bv == 1:
                continue
        elif mm_bv == 4:
            bgm.set_volume(0.05)
            ttt = InfiniteTicTacToe_3d(*ttt_blueprint, player_first)
            ttt_bv, *ttt_blueprint = ttt.run()
            bgm.set_volume(1)
            if ttt_bv == 0:
                running = False
            elif ttt_bv == 1:
                continue
        elif mm_bv == 5:
            while True:
                om = MenuMaker(*ttt_blueprint, (options_args,))
                om_bv, *ttt_blueprint = om.run()
                if om_bv == 0:
                    running = False
                    break
                elif om_bv == -1:
                    break
                elif om_bv == 1:
                    gm = MenuMaker(*ttt_blueprint, (grid_args,))
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
                    rm = MenuMaker(*ttt_blueprint, (res_args,))
                    rm_bv, *ttt_blueprint = rm.run()
                    if rm_bv == 0:
                        running = False
                        break
                    elif rm_bv == -1:
                        continue
                    else:
                        screen_width, screen_height = rm_bv
                        break
                elif om_bv == 3:
                    gsm = MenuMaker(*ttt_blueprint, (you_first_args, oneVone_args, ai_first_args))
                    gsm_bv, *ttt_blueprint = gsm.run()
                    if gsm_bv == 0:
                        running = False
                        break
                    elif gsm_bv == -1:
                        continue
                    else:
                        l,r = gsm_bv.split("_")
                        if (l=="p") and (r=="p"):
                            ai = None
                        elif l=="p":
                            ai = r
                            player_first = True
                        else:
                            ai = l
                            player_first = False
                        break

    pygame.quit()

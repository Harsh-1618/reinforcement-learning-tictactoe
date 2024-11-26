from os import environ
environ["PYGAME_HIDE_SUPPORT_PROMPT"] = '1'
import pygame

pygame.init()

class Button():
    button_font = pygame.font.Font("./fonts/minecraft-evenings/Minecraft Evenings.otf", 25)

    def __init__(self,
                screen,
                x_pos,
                y_pos,
                image_path,
                hover_image_path,
                resize_dim,
                text):
        self.screen = screen
        self.x_pos = x_pos
        self.y_pos = y_pos

        self.text = Button.button_font.render(text, True, "black")
        self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, resize_dim)
        self.image_rect = self.image.get_rect(center=(self.x_pos, self.y_pos))

        self.hover_image = pygame.image.load(hover_image_path)
        self.hover_image = pygame.transform.scale(self.hover_image, resize_dim)

        self.rendered_image = self.image

    def render_button(self):
        self.screen.blit(self.rendered_image, self.image_rect)
        self.screen.blit(self.text, self.text_rect)

    def check_for_click(self, position):
        if position[0] in range(self.image_rect.left, self.image_rect.right) and position[1] in range(self.image_rect.top, self.image_rect.bottom):
            return True
        return None

    def hover_detection(self, position):
        if position[0] in range(self.image_rect.left, self.image_rect.right) and position[1] in range(self.image_rect.top, self.image_rect.bottom):
            self.rendered_image = self.hover_image
            return 1
        else:
            self.rendered_image = self.image
            return 0


class Label:
    text_font = pygame.font.Font("./fonts/tricky-jimmy/Tricky Jimmy.ttf", 30)

    def __init__(self, screen, x_pos, y_pos, font_color, resize_dim, text):
        self.screen = screen
        self.text = Label.text_font.render(text, True, font_color)
        self.text_rect = self.text.get_rect(center=(x_pos, y_pos))

        self.image = pygame.image.load("./images/label.png")
        self.image = pygame.transform.scale(self.image, resize_dim)
        self.image_rect = self.image.get_rect(center=(x_pos, y_pos))

    def render_text(self):
        self.screen.blit(self.image, self.image_rect)
        self.screen.blit(self.text, self.text_rect)

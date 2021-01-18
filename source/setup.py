import pygame
from . import constants as C, tools
pygame.init()
SCREEN=pygame.display.set_mode(C.SCREEN_SIZE)

GRAPHICS = tools.load_graphics('resources/graphics')

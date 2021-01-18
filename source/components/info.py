import pygame
from .. import constants as C
from .import coin
from .. import tools, setup
pygame.font.init()


class Info:
    # 不同游戏阶段要传入的文字信息
    # 1. 字体->文字->图片 速度快，相似度差
    # 2. 文字->扣图->图片 速度慢，相似度好 MVP 最小可用品 minimal viable product
    def __init__(self, state):

        self.state = state
        #某个阶段特有的文字信息
        self.create_state_labels()
        #通用的信息
        self.create_info_labels()
        self.flash_coin=coin.FlashingCoin()

    def create_state_labels(self):
        self.state_labels=[]
        if self.state =='main_menu':
            self.state_labels.append((self.create_label('1 PLAYER GAME'),(272,360)))
            self.state_labels.append((self.create_label('2 PLAYER GAME'),(272,405)))
            self.state_labels.append((self.create_label('TOP - '),(290,465)))
            self.state_labels.append((self.create_label('000000'),(400,465)))
        if self.state =='load_screen':
            self.state_labels.append((self.create_label('WORLD'),(280,200)))
            self.state_labels.append((self.create_label('1 - 1'),(430,200)))
            self.state_labels.append((self.create_label('X    3'),(380,280)))
            self.player_image=tools.get_image(setup.GRAPHICS['mario_bros'],178,32,12,16,(0,0,0),C.BG_MULTI)
    def create_info_labels(self):
        self.info_labels=[]
        self.info_labels.append((self.create_label('MARIO'),(75,30)))
        self.info_labels.append((self.create_label('WORLD'),(450,30)))
        self.info_labels.append((self.create_label('TIME'),(625,30)))
        self.info_labels.append((self.create_label('000000'),(75,55)))
        self.info_labels.append((self.create_label('x00'),(300,55)))
        self.info_labels.append((self.create_label('1 - 1'),(480,55)))


    def create_label(self, label, size=40, width_scale=1.25, height_scale=1):
        font =pygame.font.SysFont(C.FONT,size)
        #设置是否抗锯齿和颜色
        label_image=font.render(label, 1, (255,255,255))
        #渣画质操作，先缩放后放大
        rect=label_image.get_rect()
        label_image=pygame.transform.scale(label_image,(int(rect.width*width_scale),int(rect.height*height_scale)))
        return label_image
        pass

    def update(self):
        self.flash_coin.update()
        pass

    def draw(self, surface):
        for label in self.state_labels:
            surface.blit(label[0],label[1])

        for label in self.info_labels:
            surface.blit(label[0],label[1])

        surface.blit(self.flash_coin.image,self.flash_coin.rect)
        if self.state == 'load_screen':
            surface.blit(self.player_image, (300,270))

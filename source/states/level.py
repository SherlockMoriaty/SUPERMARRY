from ..components import info,player
from .. import setup
from .. import constants as C
import os,json
import pygame
class Level:
    def __init__(self):
        self.finished=False
        self.next=None
        self.info = info.Info('level')
        self.load_map_data()
        self.setup_background()
        self.setup_start_positions()
        self.setup_player()

    def load_map_data(self):
        file_name='level_1.json'
        file_path=os.path.join('source/data/maps',file_name)
        with open(file_path) as f:
            self.map_data=json.load(f)

    def setup_background(self):
        self.image_name=self.map_data['image_name']
        self.background = setup.GRAPHICS[self.image_name]
        rect=self.background.get_rect()
        self.background=pygame.transform.scale(self.background, (int(rect.width*C.BG_MULTI),int(rect.height*C.BG_MULTI)))
        self.background_rect=self.background.get_rect()

        self.game_window=setup.SCREEN.get_rect()
        self.game_ground=pygame.Surface((self.background_rect.width,self.background_rect.height))

    def setup_start_positions(self):
        self.positions=[]
        for data in self.map_data['maps']:
            self.positions.append((data['start_x'],data['end_x'],data['player_x'],data['player_y']))
        self.start_x,self.end_x,self.player_x,self.player_y=self.positions[0]


    def setup_player(self):
        self.player=player.Player('mario')
        self.player.rect.x=self.game_window.x+self.player_x
        self.player.rect.bottom=self.player_y

    def update(self,surface,keys):
        self.player.update(keys)
        self.update_player_position()
        self.update_game_window()
        self.draw(surface)

    def update_player_position(self):
        self.player.rect.x+=self.player.x_vel
        # 限制主角不会跑到屏幕外
        if self.player.rect.x<self.start_x:
            self.player.rect.x=self.start_x
        if self.player.rect.right>self.end_x:
            self.player.rect.right=self.end_x
        self.player.rect.y += self.player.y_vel

    def update_game_window(self):
        # 如果马里奥超过了窗口的1/3位置，就窗口移动
        thread = self.game_window.x+self.game_window.width/3

        if self.player.x_vel>0 and self.player.rect.centerx>thread and self.game_window.right<self.end_x:
            self.game_window.x+=self.player.x_vel
            self.start_x=self.game_window.x

    def draw(self, surface):
        #画背景
        self.game_ground.blit(self.background,self.game_window,self.game_window)
        #画主角
        self.game_ground.blit(self.player.image,self.player.rect)
        #将gameground的游戏窗口部分渲染到屏幕上
        surface.blit(self.game_ground,(0,0),self.game_window)
        self.info.draw(surface)
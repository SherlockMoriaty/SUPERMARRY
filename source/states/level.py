from ..components import info,player,stuff,brick,box,enemy
from .. import setup
from .. import constants as C
import os,json
import pygame
class Level:
    def start(self,game_info):
        self.game_info=game_info
        self.finished=False
        self.next='game_over'
        self.info = info.Info('level',game_info)
        self.load_map_data()
        self.setup_background()
        self.setup_start_positions()
        self.setup_player()
        self.setup_ground_items()
        self.setup_bricks_and_boxes()
        self.setup_enemies()


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
        # player_x, player_y是玩家重生点位置
        self.start_x,self.end_x,self.player_x,self.player_y=self.positions[0]


    def setup_player(self):
        self.player=player.Player('mario')
        self.player.rect.x=self.game_window.x+self.player_x
        self.player.rect.bottom=self.player_y

    def setup_ground_items(self):
        #精灵组，存放多个精灵，方便批量处理
        self.ground_items_group=pygame.sprite.Group()
        for name in['ground','pipe','step']:
            for item in self.map_data[name]:
                self.ground_items_group.add(stuff.Item(item['x'],item['y'],item['width'],item['height'],name))

    def setup_bricks_and_boxes(self):
        self.brick_group=pygame.sprite.Group()
        self.box_group=pygame.sprite.Group()

        if 'brick' in self.map_data:
            for brick_data in self.map_data['brick']:
                x,y =brick_data['x'],brick_data['y']
                brick_type=brick_data['type']
                if 'brick_num' in brick_data:
                    # TODO batch bricks
                    pass
                else:
                    self.brick_group.add(brick.Brick(x,y,brick_type))

        if 'box' in self.map_data:
            for box_data in self.map_data['box']:
                x,y =box_data['x'],box_data['y']
                box_type=box_data['type']
                self.box_group.add(box.Box(x,y,box_type))

    def setup_enemies(self):
        self.enemy_group_dict={}
        for enemy_group_data in self.map_data['enemy']:
            group = pygame.sprite.Group()
            for enemy_group_id, enemy_list in enemy_group_data.items():
                for enemy_data in enemy_list:
                    group.add(enemy.create_enemy(enemy_data))
                self.enemy_group_dict[enemy_group_id]=group

    def update(self,surface,keys):
        self.current_time=pygame.time.get_ticks()
        self.player.update(keys)

        if self.player.dead:
            if self.current_time-self.player.death_timer>3000:
                self.finished=True
                self.update_game_info()
        else:
            self.update_player_position()
            self.check_if_go_die()
            self.update_game_window()
            self.info.update()
            self.brick_group.update()
            self.box_group.update()

        self.draw(surface)

    def update_player_position(self):

        # x direction
        self.player.rect.x+=self.player.x_vel
        # 限制主角不会跑到屏幕外
        if self.player.rect.x<self.start_x:
            self.player.rect.x=self.start_x
        if self.player.rect.right>self.end_x:
            self.player.rect.right=self.end_x
        self.check_x_collisions()
        # y direction
        self.player.rect.y += self.player.y_vel
        self.check_y_collisions()

    def check_x_collisions(self):
        #检查一个精灵是否与精灵组里的任意一个精灵有碰撞
        check_group=pygame.sprite.Group(self.ground_items_group,self.brick_group, self.box_group)
        collided_sprite=pygame.sprite.spritecollideany(self.player, check_group)
        if collided_sprite:
            self.adjust_player_x(collided_sprite)
        pass

    def check_y_collisions(self):
        check_group = pygame.sprite.Group(self.ground_items_group, self.brick_group, self.box_group)
        collided_sprite = pygame.sprite.spritecollideany(self.player, check_group)
        if collided_sprite:
            self.adjust_player_y(collided_sprite)
        self.check_will_fall(self.player)
        pass

    def adjust_player_x(self, sprite):
        if self.player.rect.x<sprite.rect.x:
            self.player.rect.right=sprite.rect.left
        else:
            self.player.rect.left=sprite.rect.right
        self.player.x_vel=0

    def adjust_player_y(self, sprite):
        # downwards
        if self.player.rect.bottom<sprite.rect.bottom:
            self.player.y_vel=0
            self.player.rect.bottom=sprite.rect.top
            self.player.state='walk'
        #upwards
        else:
            self.player.y_vel=7
            self.player.rect.top=sprite.rect.bottom
            self.player.state='fall'
        pass

    def check_will_fall(self,sprite):
        sprite.rect.y+=1
        check_group=pygame.sprite.Group(self.ground_items_group,self.brick_group, self.box_group)
        collided_sprite=pygame.sprite.spritecollideany(sprite,check_group)
        if not collided_sprite and sprite.state!='jump':
            sprite.state='fall'
        sprite.rect.y-=1

    def update_game_window(self):
        # 如果马里奥超过了窗口的1/3位置，就窗口移动
        thread = self.game_window.x+self.game_window.width/3

        if self.player.x_vel>0 and self.player.rect.centerx>thread and self.game_window.right<self.end_x:
            self.game_window.x+=self.player.x_vel
            self.start_x=self.game_window.x

    def check_if_go_die(self):
        if self.player.rect.y>C.SCREEN_H:
            self.player.go_die()
        pass

    def update_game_info(self):
        if self.player.dead:
            self.game_info['lives']-=1
        if self.game_info['lives']==0:
            self.next='game_over'
        else:
            self.next='load_screen'

    def draw(self, surface):
        #画背景
        self.game_ground.blit(self.background,self.game_window,self.game_window)
        #画主角
        self.game_ground.blit(self.player.image,self.player.rect)
        # 画砖块
        self.brick_group.draw(self.game_ground)
        # 画宝箱
        self.box_group.draw(self.game_ground)
        # 画怪物
        for enemy_group in self.enemy_group_dict.values():
            enemy_group.draw(self.game_ground)
        #将gameground的游戏窗口部分渲染到屏幕上
        surface.blit(self.game_ground,(0,0),self.game_window)
        self.info.draw(surface)


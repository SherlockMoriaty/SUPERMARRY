import pygame
from .. import setup, tools
from .. import constants as C
from . import powerup
import os, json


class Player(pygame.sprite.Sprite):
    def __init__(self, name):
        pygame.sprite.Sprite.__init__(self)
        self.name = name
        self.load_data()
        self.setup_states()
        self.setup_velocities()
        self.setup_timers()
        self.load_images()

    def load_data(self):
        file_name = self.name + '.json'
        file_path = os.path.join('source/data/player', file_name)
        with open(file_path) as f:
            self.player_data = json.load(f)

    def setup_states(self):
        # 状态与buff
        self.state = 'stand'
        self.face_right = True
        self.dead = False
        self.big = False
        self.fire=False
        self.can_jump=True
        self.hurt_immune=False

        pass

    def setup_velocities(self):
        # 设置速度
        speed = self.player_data['speed']
        self.x_vel = 0
        self.y_vel = 0

        self.max_walk_vel = speed['max_walk_speed']
        self.max_run_vel = speed['max_run_speed']
        self.max_y_vel = speed['max_y_velocity']
        self.jump_vel = speed['jump_velocity']
        self.walk_accel = speed['walk_accel']
        self.run_accel = speed['run_accel']
        self.turn_accel = speed['turn_accel']
        self.gravity = C.GRAVITY
        self.anti_gravity=C.ANTI_GRAVITY

        self.max_x_vel = self.max_walk_vel
        self.x_accel = self.walk_accel

        pass

    def setup_timers(self):
        # 创建计时器
        self.walking_timer = 0
        self.transition_timer = 0
        self.death_timer=0
        self.hurt_immune_timer=0
        pass

    def load_images(self):
        sheet = setup.GRAPHICS['mario_bros']
        frame_rects = self.player_data['image_frames']

        self.right_small_normal_frames = []
        self.right_big_normal_frames = []
        self.right_big_fire_frames = []
        self.left_small_normal_frames = []
        self.left_big_normal_frames = []
        self.left_big_fire_frames = []

        self.small_normal_frames = [self.right_small_normal_frames, self.left_small_normal_frames]
        self.big_normal_frames = [self.right_big_normal_frames, self.left_big_normal_frames]
        self.big_fire_frames = [self.right_big_fire_frames, self.left_big_fire_frames]

        self.all_frames = [
            self.right_small_normal_frames,
            self.right_big_normal_frames,
            self.right_big_fire_frames,
            self.left_small_normal_frames,
            self.left_big_normal_frames,
            self.left_big_fire_frames,
        ]

        self.right_frames = self.right_small_normal_frames
        self.left_frames = self.left_small_normal_frames

        for group, group_frame_rects in frame_rects.items():
            for frame_rect in group_frame_rects:
                right_image = tools.get_image(sheet, frame_rect['x'], frame_rect['y'], frame_rect['width'],
                                              frame_rect['height'], (0, 0, 0), C.PLAYER_MULTI)
                left_image = pygame.transform.flip(right_image, True, False)
                if group == 'right_small_normal':
                    self.right_small_normal_frames.append(right_image)
                    self.left_small_normal_frames.append(left_image)
                if group == 'right_big_normal':
                    self.right_big_normal_frames.append(right_image)
                    self.left_big_normal_frames.append(left_image)
                if group == 'right_big_fire':
                    self.right_big_fire_frames.append(right_image)
                    self.left_big_fire_frames.append(left_image)

        self.frame_index = 0
        self.frames = self.right_frames
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        # 载入主角帧造型
        pass

    def update(self, keys,level):
        self.current_time = pygame.time.get_ticks()
        self.handle_states(keys,level)
        self.is_hurt_immune()

    def handle_states(self, keys,level):

        self.can_jump_or_not(keys)

        if self.state == 'stand':
            self.stand(keys,level)
        elif self.state == 'walk':
            self.walk(keys)
        elif self.state == 'jump':
            self.jump(keys)
        elif self.state == 'fall':
            self.fall(keys)
        elif self.state == 'die':
            self.die(keys)
        elif self.state == 'small2big':
            self.small2big(keys)
        elif self.state == 'big2small':
            self.big2small(keys)
        elif self.state=='big2fire':
            self.big2fire(keys)

        if self.face_right:
            self.image = self.right_frames[self.frame_index]
        else:
            self.image = self.left_frames[self.frame_index]
    def can_jump_or_not(self,keys):
        if not keys[pygame.K_SPACE]:
            self.can_jump=True

    def stand(self, keys, level):
        self.frame_index = 0
        self.x_vel = 0
        self.y_vel = 0
        if keys[pygame.K_RIGHT]:
            self.face_right = True
            self.state = 'walk'
        if keys[pygame.K_LEFT]:
            self.face_right = False
            self.state = 'walk'
        elif keys[pygame.K_SPACE] and self.can_jump:
            self.state='jump'
            self.y_vel=self.jump_vel
        elif keys[pygame.K_s]:
            self.shoot_fireball(level)
        pass

    def walk(self, keys):
        if keys[pygame.K_s]:
            self.max_x_vel = self.max_run_vel
            self.x_accel = self.run_accel
        else:
            self.max_x_vel = self.max_walk_vel
            self.x_accel = self.walk_accel
        if self.current_time - self.walking_timer > self.calc_frame_duration():
            if self.frame_index < 3:
                self.frame_index += 1
            else:
                self.frame_index = 1
            self.walking_timer = self.current_time
        if keys[pygame.K_RIGHT]:
            self.face_right = True
            # 向左移动
            if self.x_vel < 0:
                self.frame_index = 5  # 刹车帧
                self.x_accel = self.turn_accel
            self.x_vel = self.calc_vel(self.x_vel, self.x_accel, self.max_x_vel, True)
        elif keys[pygame.K_LEFT]:
            self.face_right = False
            if self.x_vel > 0:
                self.frame_index = 5
                self.x_accel = self.turn_accel
            self.x_vel = self.calc_vel(self.x_vel, self.x_accel, self.max_x_vel, False)
        if keys[pygame.K_SPACE] and self.can_jump:
            self.state='jump'
            self.y_vel=self.jump_vel
        elif not keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]:
            if self.face_right:
                self.x_vel -= self.x_accel
                if self.x_vel < 0:
                    self.x_vel = 0
                    self.state = 'stand'
            else:
                self.x_vel += self.x_accel
                if self.x_vel > 0:
                    self.x_vel = 0
                    self.state = 'stand'
        pass

    def jump(self, keys):
        self.frame_index=4
        self.y_vel+=self.anti_gravity
        self.can_jump=False

        if self.y_vel>=0:
            self.state='fall'

        if keys[pygame.K_RIGHT]:
            self.face_right = True
            # 向左移动
            if self.x_vel < 0:
                self.x_accel = self.turn_accel
            self.x_vel = self.calc_vel(self.x_vel, self.x_accel, self.max_x_vel, True)
        elif keys[pygame.K_LEFT]:
            self.face_right = False
            if self.x_vel > 0:
                self.x_accel = self.turn_accel
            self.x_vel = self.calc_vel(self.x_vel, self.x_accel, self.max_x_vel, False)
        else:
            if self.face_right:
                self.x_vel -= self.x_accel
                if self.x_vel < 0:
                    self.x_vel = 0
            else:
                self.x_vel += self.x_accel
                if self.x_vel > 0:
                    self.x_vel = 0
        if not keys[pygame.K_SPACE]:
            self.state='fall'
        pass

    def fall(self,keys):
        # 如果不加限制，下落速度是会无限上升的，对二次元世界不友好
        self.y_vel=self.calc_vel(self.y_vel,self.gravity,self.max_y_vel)

        if keys[pygame.K_RIGHT]:
            self.face_right = True
            # 向左移动
            if self.x_vel < 0:
                self.x_accel = self.turn_accel
            self.x_vel = self.calc_vel(self.x_vel, self.x_accel, self.max_x_vel, True)
        elif keys[pygame.K_LEFT]:
            self.face_right = False
            if self.x_vel > 0:
                self.x_accel = self.turn_accel
            self.x_vel = self.calc_vel(self.x_vel, self.x_accel, self.max_x_vel, False)
        else:
            if self.face_right:
                self.x_vel -= self.x_accel
                if self.x_vel < 0:
                    self.x_vel = 0
            else:
                self.x_vel += self.x_accel
                if self.x_vel > 0:
                    self.x_vel = 0
        pass

    def go_die(self):
        self.dead=True
        self.y_vel=self.jump_vel
        self.frame_index=6
        self.state='die'
        self.death_timer=self.current_time

    def die(self, keys):
        self.rect.y+=self.y_vel
        self.y_vel+=self.anti_gravity
        pass

    def small2big(self,keys):
        frame_dur=100
        sizes=[1,0,1,0,1,2,0,1,2,0,2] # 0 small 1 medium 2 big
        frame_and_idx=[(self.small_normal_frames,0),(self.small_normal_frames,7),(self.big_normal_frames,0)]
        if self.transition_timer==0:
            self.big=True
            self.transition_timer=self.current_time
            self.changing_idx=0
        elif self.current_time-self.transition_timer>frame_dur:
            self.transition_timer=self.current_time
            frames, idx = frame_and_idx[sizes[self.changing_idx]]
            self.change_player_image(frames, idx)
            self.changing_idx += 1
            if self.changing_idx==len(sizes):
                self.transition_timer=0
                self.state='walk'
                self.right_frames=self.right_big_normal_frames
                self.left_frames=self.left_big_normal_frames

    def big2small(self,keys):
        frame_dur=100
        sizes=[2,1,0,1,0,1,0,1,0,1,0] # 0 small 1 medium 2 big
        frame_and_idx=[(self.small_normal_frames,8),(self.big_normal_frames,8),(self.big_normal_frames,4)]
        if self.transition_timer==0:
            self.big=False
            self.transition_timer=self.current_time
            self.changing_idx=0
        elif self.current_time-self.transition_timer>frame_dur:
            self.transition_timer=self.current_time
            frames, idx = frame_and_idx[sizes[self.changing_idx]]
            self.change_player_image(frames, idx)
            self.changing_idx += 1
            if self.changing_idx==len(sizes):
                self.transition_timer=0
                self.state='walk'
                self.right_frames=self.right_small_normal_frames
                self.left_frames=self.left_small_normal_frames

    def big2fire(self,keys):
        frame_dur = 65
        sizes = [ 0, 1, 0, 1, 0, 1, 0, 1, 0,1,0]  # 0 small 1 medium 2 big
        frame_and_idx = [(self.big_fire_frames, 3), (self.big_normal_frames, 3)]
        if self.transition_timer == 0:
            self.fire = True
            self.transition_timer = self.current_time
            self.changing_idx = 0
        elif self.current_time - self.transition_timer > frame_dur:
            self.transition_timer = self.current_time
            frames, idx = frame_and_idx[sizes[self.changing_idx]]
            self.change_player_image(frames, idx)
            self.changing_idx += 1
            if self.changing_idx == len(sizes):
                self.transition_timer = 0
                self.state = 'walk'
                self.right_frames = self.right_big_fire_frames
                self.left_frames = self.left_big_fire_frames

    def change_player_image(self,frames,idx):
        self.frame_index=idx
        if self.face_right:
            self.right_frames=frames[0]
            self.image=self.right_frames[self.frame_index]
        else:
            self.left_frames = frames[1]
            self.image = self.left_frames[self.frame_index]
        last_frame_bottom=self.rect.bottom
        last_frame_centerx=self.rect.centerx
        self.rect=self.image.get_rect()
        self.rect.bottom=last_frame_bottom
        self.rect.centerx=last_frame_centerx

    def shoot_fireball(self,level):
        self.frame_index=6
        fireball=powerup.Fireball(self.rect.centerx,self.rect.centery,self.face_right)
        level.powerup_group.add(fireball)



    def calc_vel(self, vel, accel, max_vel, is_positive=True):
        if is_positive:
            return min(vel + accel, max_vel)
        else:
            return max(vel - accel, -max_vel)

    def calc_frame_duration(self):
        duration = -60 / self.max_run_vel+abs(self.x_vel)+80
        return duration

    def is_hurt_immune(self):
        if self.hurt_immune:
            if self.hurt_immune_timer==0:
                self.hurt_immune_timer=self.current_time
                self.blank_image=pygame.Surface((1,1))
            elif self.current_time-self.hurt_immune_timer<2000:
                if (self.current_time-self.hurt_immune_timer)%100<50:
                    self.image=self.blank_image
                pass
            else:
                self.hurt_immune=False
                self.hurt_immune_timer=0

import pygame
from .. import setup,tools
from .. import constants as C

# 金币类继承精灵类
# 金币不仅只展示在封面上，之后还要和mario产生联系
class FlashingCoin(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.frames=[]
        self.frame_index=0
        frame_rects=[(1,160,5,8),(9,160,5,8),(17,160,5,8),(9,160,5,8)]#忽明忽暗
        self.load_frames(frame_rects)
        self.image=self.frames[self.frame_index]
        self.rect=self.image.get_rect()
        self.rect.x=280
        self.rect.y=58
        self.timer = 0


    def load_frames(self, frame_rects):
        sheet=setup.GRAPHICS['item_objects']
        for frame_rect in frame_rects:
            # *的意思是解包，将元组解析成变量
            self.frames.append(tools.get_image(sheet, *frame_rect,(0,0,0),C.BG_MULTI))
    #重写update方法
    def update(self):
        # 当前时间
        self.current_time=pygame.time.get_ticks()
        # 帧之间停留时间
        frame_durations=[375,125,125,125]


        if self.timer==0:
            self.timer=self.current_time

        # 如果当前时间-计时器的时间>帧需要间隔的时间
        elif self.current_time-self.timer>frame_durations[self.frame_index]:
            self.frame_index+=1
            self.frame_index%=4
            self.timer=self.current_time
        self.image = self.frames[self.frame_index]

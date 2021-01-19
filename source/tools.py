import pygame
import random
import os


class Game:
    def __init__(self, state_dict, start_state):

        self.screen = pygame.display.get_surface()
        self.clock = pygame.time.Clock()
        self.keys = pygame.key.get_pressed()
        self.state_dict=state_dict
        self.state=self.state_dict[start_state]

    def update(self):
        if self.state.finished:
            game_info=self.state.game_info
            next_state=self.state.next
            self.state.finished=False
            self.state=self.state_dict[next_state]
            self.state.start(game_info)
        self.state.update(self.screen, self.keys)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.display.quit()
                    quit()
                elif event.type == pygame.KEYDOWN:
                    self.keys = pygame.key.get_pressed()
                elif event.type == pygame.KEYUP:
                    self.keys = pygame.key.get_pressed()

            self.update()

            pygame.display.update()
            # 计时+帧速率
            self.clock.tick(60)


# 对图片文件的通用处理方法
# 加载所有图片
def load_graphics(path, accept=('.jpg', '.png', '.bmp', '.gif')):
    graphics = {}
    for pic in os.listdir(path):
        name, ext = os.path.splitext(pic)
        if ext.lower() in accept:
            img = pygame.image.load(os.path.join(path, pic))
            # 如果图片带着alpha参量，就是透明底的png格式，就转换成带透明层的，这部不是必须的，但是是建议的加快渲染的操作
            if img.get_alpha():
                img = img.convert_alpha()
            else:
                img = img.convert()
            graphics[name] = img
    return graphics


# 获取图片并快速扣图
def get_image(sheet, x, y, width, height, colorkey, scale):
    image = pygame.Surface((width, height))
    image.blit(sheet, (0, 0), (x, y, width, height))  # (0,0)代表画到哪个位置，(x, y, width, height)代表sheet里哪个区域要取出来
    image.set_colorkey(colorkey)
    image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
    return image

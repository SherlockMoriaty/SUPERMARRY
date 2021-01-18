import pygame
if __name__ == '__main__':
    pygame.init()
    w,h=500,500
    pygame.display.set_mode((w,h))
    screen=pygame.display.get_surface()

    #载入背景图并且缩放至宽高
    bgpic=pygame.image.load('./bgpic.png')
    bgpic=pygame.transform.scale(bgpic,(w,h))

    #载入超级玛丽
    mario_image=pygame.image.load('./mario.png')

    #创建精灵
    mario=pygame.sprite.Sprite()
    mario.image=mario_image
    mario.rect=mario.image.get_rect() #获取坐标点
    mario.rect.x, mario.rect.y =w/2, h/2

    #玩家组（方便管理）
    player_group=pygame.sprite.Group()
    player_group.add(mario)

    #开始游戏
    #更新<=====>画图，很像单片机一直运行
    while True:
        # 更新部分
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_DOWN]:
                    mario.rect.y+=10
                if keys[pygame.K_UP]:
                    mario.rect.y-=10
        #画图部分
        screen.blit(bgpic,(0,0))
        player_group.draw(screen)
        pygame.display.update() # 更新屏幕
    os.system("pause")



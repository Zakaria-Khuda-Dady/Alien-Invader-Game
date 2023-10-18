import pygame as pg 
from pygame.locals import *
from sys import exit 
from pygame import mixer
import random, time

mixer.pre_init(44100, -16, 2, 2048)
pg.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 800
screen = pg.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
caption = pg.display.set_caption("Space Invaders")
frames = pg.time.Clock()
fps = 240
bg_music = mixer.music.load("music/bg_music.mp3")
mixer.music.play(-1)

black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)

font = pg.font.SysFont("Verdana", 30)
speed = 2

increase_speed = pg.USEREVENT + 1
pg.time.set_timer(increase_speed, 10000)

class ALIEN(pg.sprite.Sprite):
    def __init__(self) -> None:
        super().__init__()
        self.image = pg.image.load("graphics/alien.png")
        self.surf = pg.Surface((50, 30))
        self.rect = self.surf.get_rect(center=(random.randint(25, 775), (random.randint(-200, 0))))

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def update(self, score):
        self.rect.move_ip(0, speed)
        if self.rect.top > SCREEN_HEIGHT:
            self.rect.center = (random.randint(25, 775), (random.randint(-200, 0)))
            score += 1

        return score

    def reset_pos(self):
        self.rect.center = (random.randint(25, 775), (random.randint(-200, 0)))


class SHIP(pg.sprite.Sprite):
    def __init__(self) -> None:
        super().__init__()
        self.image = pg.image.load("graphics/ship.png")
        self.surf = pg.Surface((60, 30))
        self.rect = self.surf.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT - 15))

        self.lives = 3

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def update(self):
        pressed_keys = pg.key.get_pressed()
        if self.rect.left > 0:
            if pressed_keys[K_LEFT]:
                self.rect.move_ip(-2.5, 0)
        else:
            self.rect.right = SCREEN_WIDTH - 15

        if self.rect.right < SCREEN_WIDTH:
            if pressed_keys[K_RIGHT]:
                self.rect.move_ip(2.5, 0)
        else:
            self.rect.left = 15

    def create_bullet(self):
        return BULLET(self.rect.center)


class BULLET(pg.sprite.Sprite):
    def __init__(self, pos) -> None:
        super().__init__()
        self.image = pg.image.load("graphics/bullet.png")
        self.surf = pg.Surface((10, 10))
        self.rect = self.surf.get_rect(center=(pos))

    def update(self):
        self.rect.move_ip(0, -3)
        if self.rect.top < 0:
            self.kill()


class MAIN():
    def __init__(self) -> None:
        self.ship = SHIP()
        
        self.a1, self.a2, self.a3 = ALIEN(), ALIEN(), ALIEN()
        self.alien_group = pg.sprite.Group()
        self.alien_group.add(self.a1, self.a2, self.a3)

        self.bullet_group = pg.sprite.Group()

        self.score = 0

        self.bullet_shot = mixer.Sound("music/bullet_shot.wav")
        self.alien_explosion = mixer.Sound("music/alien_explosion.wav")
        self.bullet_explosion = mixer.Sound("music/bullet_explosion.wav")

    def run(self):
        self.collision_detection()
        self.draw_elements()
        self.update_elements()

    def draw_elements(self):
        self.HUD()
        self.alien_group.draw(screen)
        self.ship.draw(screen)
        self.bullet_group.draw(screen)

    def update_elements(self):
        for alien in self.alien_group:
            self.score = alien.update(self.score)

        self.ship.update()

        pressed_keys = pg.key.get_pressed()
        if pressed_keys[K_SPACE]:
            self.shoot_bullet()

        self.bullet_group.update()

        if len(self.alien_group) == 0:
            self.a1.reset_pos(), self.a2.reset_pos(), self.a3.reset_pos()
            self.alien_group.add(self.a1, self.a2, self.a3)

        if self.ship.lives == 0:
            self.end_screen()

    def shoot_bullet(self):
        if len(self.bullet_group) < 1:
            self.bullet_shot.play()
            self.bullet_group.add(self.ship.create_bullet())

    def collision_detection(self):
        self.bullet_alien_col()
        self.alien_ship_col()

    def bullet_alien_col(self):
        for alien in self.alien_group:
            for bullet in self.bullet_group:
                if pg.sprite.collide_rect(alien, bullet):
                    alien.kill()
                    bullet.kill()
                    self.bullet_explosion.play()
                    self.score += 3 

    def alien_ship_col(self):
        for alien in self.alien_group:
            if alien.rect.colliderect(self.ship):
                alien.kill()
                self.alien_explosion.play()
                self.ship.lives -= 1

    def HUD(self):
        lives_render = font.render("Lives: " + str(self.ship.lives), True, white)
        screen.blit(lives_render, (SCREEN_WIDTH/2 - 60, 0))

        score_render = font.render("Score: " + str(round(self.score, 1)), True, white)
        screen.blit(score_render, (0, 0))

        speed_render = font.render("Speed:" + str(speed), True, white)
        screen.blit(speed_render, (630, 0))

    def end_screen(self):
        time.sleep(1)
        screen.fill(red)

        score_render = font.render("Score: " + str(round(self.score, 1)), True, white)
        screen.blit(score_render, (SCREEN_WIDTH/2 - 50, SCREEN_HEIGHT/2))

        pg.display.update()

        time.sleep(2)
        end_program()


def end_program():
    pg.quit()
    exit()

main = MAIN()

while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            end_program()

        if event.type == increase_speed:
            speed += .2

    screen.fill(black)

    main.run()

    frames.tick(fps)
    pg.display.update()
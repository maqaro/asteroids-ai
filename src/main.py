import math
import pygame
import sys
import random

class Player(pygame.sprite.Sprite):
    def __init__(self, width, height):
        # Calls the parent class constructor
        pygame.sprite.Sprite.__init__(self)

        #create an image of this Sprite
        self.original_image = pygame.image.load('src/assets/ship.png').convert_alpha()
        self.original_rect = self.original_image.get_rect()
        new_size = (int(self.original_rect.width * 0.2), int(self.original_rect.height * 0.2))
        print(new_size)
        self.original_image = pygame.transform.scale(self.original_image, new_size)
        self.image = self.original_image
        self.rect = self.image.get_rect()
        
        # variables needed for movement and rotations
        self.x = 640
        self.y = 360
        self.angle = 0 

        # placing the player in the middle of the screen
        self.rect.center = (self.x, self.y)
        

    def controls(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.move(6)

        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.move(-6)

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rotate('left')
        
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rotate('right')

        if keys[pygame.K_SPACE]:
            # make it shoot bullets
            self.shoot()


    def rotate(self, direction):
        if direction == 'left':
            angle_multiplier = 4
        else:
            angle_multiplier = -4

        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.angle = (self.angle + angle_multiplier) % 360

    def move(self, move):
        self.x += move * math.cos(math.radians(self.angle + 90))
        self.y -= move * math.sin(math.radians(self.angle + 90))
        self.rect.center = (round(self.x), round(self.y))
        self.screen_wrap()

    def screen_wrap(self):
        if self.x < -20:
            self.x = 1299

        if self.x > 1300:
            self.x = -19

        if self.y < -20:
            self.y = 739

        if self.y > 740:
            self.y = -19

    def shoot():
        pass

    def update(self):
        self.controls()
        

class Object(pygame.sprite.Sprite):
    def __init__(self, width, height):
        # Calls the parent class constructor
        pygame.sprite.Sprite.__init__(self)

        #create an image of this Sprite
        self.image = pygame.Surface([width, height])
        self.image.fill("White")

        self.rect = self.image.get_rect()

    def movement(self):
        pass

    def despawn(self):
        pass

    def update(self):
        pass

pygame.init()
screen = pygame.display.set_mode((1280,720))
clock = pygame.time.Clock()
FPS = 60
running = True

player_group = pygame.sprite.GroupSingle()

player = Player(25,50)
player_group.add(player)

while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill("black")
    player_group.update()
    player_group.draw(screen)
    
    pygame.display.update()
    
pygame.quit()
import pygame
import numpy as np
import math
import random

class Player(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.original_image = pygame.image.load('src/assets/ship.png').convert_alpha()
        self.original_rect = self.original_image.get_rect()
        new_size = (int(self.original_rect.width * 0.2), int(self.original_rect.height * 0.2))
        self.original_image = pygame.transform.scale(self.original_image, new_size)
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.reset()

    def reset(self):
        self.x = 640
        self.y = 360
        self.angle = 0 
        self.rect.center = (self.x, self.y)
        self.last_shot = 300
        self.score = 0

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
        if keys[pygame.K_SPACE] and pygame.time.get_ticks() - self.last_shot >= 250:
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

    def shoot(self):
        bullet = Bullet(self.x, self.y, self.angle, self.game)
        self.game.bullets.add(bullet)
        self.last_shot = pygame.time.get_ticks()

    def increase_score(self):
        self.score += 1

    def update(self):
        self.controls()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, game):
        super().__init__()
        self.image = pygame.Surface((5, 5))
        self.image.fill('white')
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 10
        self.angle = angle
        self.game = game

    def update(self):
        dx = self.speed * math.cos(math.radians(self.angle + 90))
        dy = -self.speed * math.sin(math.radians(self.angle + 90))
        self.rect.x += dx
        self.rect.y += dy
        if not self.game.screen.get_rect().colliderect(self.rect):
            self.kill()


class Object(pygame.sprite.Sprite):
    def __init__(self, surface):
        super().__init__()
        
        self.screen_width = 1280
        self.screen_height = 720

        self.size = 60
        self.image = pygame.Surface([self.size, self.size])
        self.image.fill('black')
        pygame.draw.circle(self.image, ('white'), (30, 30), 30)
        self.rect = self.image.get_rect()

        self.angle = self.rand_angle()
        self.x, self.y = self.calculate_spawn_position()
        self.rect.center = (self.x, self.y)

    def rand_angle(self):
        return random.randint(0, 360)

    def calculate_spawn_position(self):
        angle_rad = math.radians(self.angle)
        if 0 <= self.angle <= 90:
            return -self.size, random.randint(-self.size, self.screen_height + self.size)
        elif 90 < self.angle <= 180:
            return random.randint(-self.size, self.screen_width + self.size), -self.size
        elif 180 < self.angle <= 270:
            return self.screen_width + self.size, random.randint(-self.size, self.screen_height + self.size)
        else:
            return random.randint(-self.size, self.screen_width + self.size), self.screen_height + self.size

    def movement(self):
        x_val = math.cos(math.radians(self.angle))
        y_val = math.sin(math.radians(self.angle))
        self.x += x_val * 4
        self.y += y_val * 4
        self.rect.center = (round(self.x), round(self.y))

    def despawn(self):
        if self.x < -100 or self.x > 1380:
            self.kill()
        elif self.y < -100 or self.y > 820:
            self.kill()

    def update(self):
        self.movement()
        self.despawn()

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1280, 720))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 48)
        self.FPS = 60
        self.running = True
        self.alive = True
        self.player_group = pygame.sprite.GroupSingle(Player(self))
        self.objects = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.score = 0

    def reset(self):
        self.__init__()
        self.score = 0

    def get_state(self):
        player = self.player_group.sprite
        if player:
            state = [player.x, player.y, player.angle]
            # Calculate distances to each object
            distances = []
            for obj in self.objects:
                dist = math.hypot(obj.x - player.x, obj.y - player.y)
                distances.append(dist)
            
            # Include distances of the nearest few objects (e.g., 5)
            distances = sorted(distances)[:5]  # Get the closest 5 distances

            # Pad distances with zero if fewer than 5 objects
            distances += [0] * (5 - len(distances))

            state += distances
            return np.array(state, dtype=np.float32)
        else:
            return np.array([0] * 8, dtype=np.float32)  # Adjust size to match updated state


    def play_step(self, action, fps=200):
        self.perform_action(action)
        self.update()
        reward = self.calculate_reward()
        done = not self.alive
        score = self.score
        self.draw()
        pygame.display.flip()
        self.clock.tick(fps)
        return reward, done, score

    def perform_action(self, action):
        player = self.player_group.sprite
        if player:
            if action[0] == 1:  # Move up
                player.move(6)
            if action[1] == 1:  # Move down
                player.move(-6)
            if action[2] == 1:  # Rotate left
                player.rotate('left')
            if action[3] == 1:  # Rotate right
                player.rotate('right')
            if action[4] == 1:  # Shoot
                player.shoot()

    def calculate_reward(self):
        if not self.alive:
            return -10
        if self.player_group.sprite and self.player_group.sprite.score > 0:
            return 1
        return 0

    def player_collision(self):
        if self.player_group.sprite:
            if pygame.sprite.spritecollide(self.player_group.sprite, self.objects, False):
                self.score = self.player_group.sprite.score
                self.player_group.empty()
                self.objects.empty()
                self.bullets.empty()
                return False
            else:
                return True
        else:
            return False

    def display_score(self):
        score_surface = self.font.render(f'Score: {self.score}', True, (255, 255, 255))
        score_rect = score_surface.get_rect()
        score_rect.topleft = (10, 10)
        self.screen.blit(score_surface, score_rect)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if not self.alive and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    self.alive = True

    def update(self):
        if self.alive:
            if len(self.objects) < 6:
                self.objects.add(Object(self.screen))
            if len(self.player_group) < 1:
                self.player_group.add(Player(self))
            self.player_group.update()
            self.objects.update()
            self.bullets.update()
            for bullet in self.bullets:
                if pygame.sprite.spritecollide(bullet, self.objects, True):
                    bullet.kill()
                    if self.player_group.sprite:
                        self.player_group.sprite.increase_score()
                    self.score = self.player_group.sprite.score if self.player_group.sprite else self.score
            self.alive = self.player_collision()

    def draw(self):
        self.screen.fill("black")
        if self.alive:
            self.display_score()
            self.player_group.draw(self.screen)
            self.objects.draw(self.screen)
            self.bullets.draw(self.screen)

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(self.FPS)

if __name__ == "__main__":
    game = Game()
    game.run()


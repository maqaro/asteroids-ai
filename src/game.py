import math
import os
import neat.checkpoint
import neat.population
import pygame
import random
import neat

class Player(pygame.sprite.Sprite):
    def __init__(self):
        # Calls the parent class constructor
        pygame.sprite.Sprite.__init__(self)

        #create an image of this Sprite
        self.original_image = pygame.image.load('src/assets/ship.png').convert_alpha()
        self.original_rect = self.original_image.get_rect()
        new_size = (int(self.original_rect.width * 0.2), int(self.original_rect.height * 0.2))
        self.original_image = pygame.transform.scale(self.original_image, new_size)
        self.image = self.original_image
        self.rect = self.image.get_rect()
        
        # variables needed for movement and rotations
        self.x = 640
        self.y = 360
        self.angle = 0 

        # placing the player in the middle of the screen
        self.rect.center = (self.x, self.y)

        # keeping track of time between the shots to limit bullet spam
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
        bullet = Bullet(self.x, self.y, self.angle)
        bullets.add(bullet)
        self.last_shot = pygame.time.get_ticks()

    def increase_score(self):
        self.score += 1

    def update(self):
        self.controls()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        super().__init__()
        self.image = pygame.Surface((5, 5))
        self.image.fill('white')
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 10
        self.angle = angle

    def update(self):
        dx = self.speed * math.cos(math.radians(self.angle + 90))
        dy = -self.speed * math.sin(math.radians(self.angle + 90))
        self.rect.x += dx
        self.rect.y += dy
        if not screen.get_rect().colliderect(self.rect):
            self.kill()


class Object(pygame.sprite.Sprite):
    def __init__(self, surface):
        # Calls the parent class constructor
        pygame.sprite.Sprite.__init__(self)

        # Screen dimensions
        self.screen_width = 1280
        self.screen_height = 720

        # Object size
        self.size = 60
        self.image = pygame.Surface([self.size, self.size])
        self.image.fill('black')  # Fill color white for visibility
        pygame.draw.circle(self.image, ('white'), (30, 30), 30)  # Draw circle
        self.rect = self.image.get_rect()

        # Generate a random angle from 0 to 360 degrees
        self.angle = self.rand_angle()

        # Set initial position based on angle
        self.x, self.y = self.calculate_spawn_position()
        self.rect.center = (self.x, self.y)

    def rand_angle(self):
        return random.randint(0, 360)

    def calculate_spawn_position(self):
        # Calculate spawn position off-screen based on angle
        angle_rad = math.radians(self.angle)
        if 0 <= self.angle <= 90:
            return -self.size, random.randint(-self.size, self.screen_height + self.size)
        elif 90 < self.angle <= 180:
            return random.randint(-self.size, self.screen_width + self.size), -self.size
        elif 180 < self.angle <= 270:
            return self.screen_width + self.size, random.randint(-self.size, self.screen_height + self.size)
        else:  # 270 < self.angle <= 360
            return random.randint(-self.size, self.screen_width + self.size), self.screen_height + self.size

    def movement(self):
        # Move object in the direction of its angle
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


def player_collision():
    if player_group and pygame.sprite.spritecollide(player_group.sprite, objects, False):
        player_group.empty()
        objects.empty()
        bullets.empty()
        return False
    else:
        return True

def display_score():
    score_surface = font.render(f'Score: {player_group.sprite.score}', True, (255,255,255))
    score_rect = score_surface.get_rect()
    score_rect.topleft = (10,10)
    screen.blit(score_surface, score_rect)

pygame.init()
screen = pygame.display.set_mode((1280,720))
clock = pygame.time.Clock()
font = pygame.font.Font(None, 48)

FPS = 60

player_group = pygame.sprite.GroupSingle()
objects = pygame.sprite.Group()
bullets = pygame.sprite.Group()


def eval_genome(genomes, config):
    for genome_id, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        genome.fitness = 0  # Initialize fitness to 0
        running = True
        alive = True

        while running and alive:
            clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if alive:
                    pass
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s and not alive:
                        alive = True

            if alive:
                if len(objects) < 6:
                    objects.add(Object(screen))

                if len(player_group) < 1:
                    player_group.add(Player())

                screen.fill("black")
                display_score()

                player_group.update()
                player_group.draw(screen)

                objects.update()
                objects.draw(screen)

                bullets.update()
                bullets.draw(screen)

                for bullet in bullets:
                    if pygame.sprite.spritecollide(bullet, objects, True):
                        bullet.kill()
                        player_group.sprite.increase_score()

                alive = player_collision()

            elif not alive:
                screen.fill("black")
            
            pygame.display.update()
        
    pygame.quit()



def run_neat(config_path):
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

    population = neat.Population(config)

    population.add_reporter(neat.StdOutReporter(True))
    population.add_reporter(neat.StatisticsReporter)

    population.add_reporter(neat.Checkpointer(1))

    winner = population.run(eval_genome,50)

    print('\nBest genome:\n{!s}'.format(winner))

if __name__ == "__main__":
    local_directory = os.path.dirname(__file__)
    config_path = os.path.join(local_directory, "neat_config.txt")
    run_neat(config_path)
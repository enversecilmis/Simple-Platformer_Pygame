from os import listdir
from random import random
from types import FunctionType
from typing import Tuple
import pygame
from pygame.sprite import Group, Sprite
from gamedata import COLOR, TILE_SIZE
import utils



class Actor(pygame.sprite.Sprite):
    def __init__(self, image_path, spawn_pos=(0,0), scaleXY=(-1,-1)):
        super().__init__()

        print(image_path)
        self.image = pygame.image.load(image_path).convert_alpha()
        if not scaleXY == (-1,-1):
            self.image = pygame.transform.scale(self.image, scaleXY)
        self.rect = self.image.get_rect(center = spawn_pos)
        self.health = 100

    def update(self):
        pass



class AnimetableActor(Actor):
    def __init__(self, animations_path, scaleXY: Tuple, spawn_pos=(0, 0)):
        initial_image_path = animations_path + listdir(animations_path)[0] + "/" + listdir(animations_path + listdir(animations_path)[0])[0]
        super().__init__(initial_image_path, spawn_pos = spawn_pos, scaleXY = scaleXY)

        self.animations = utils.loadAnimationSprites(animations_path, scaleXY)
        self.animation_status = next(iter(self.animations))
        self.animation_frame_index = 0
        self.animation_speed = 0.2
        self.animation_facing_right = True
        self.image = self.animations[self.animation_status][self.animation_frame_index]
        self.rect = self.image.get_rect(center=spawn_pos)
        self.velocity = pygame.math.Vector2((0,0))
        self.is_on_ground = False



    def handleAnimations(self):
        self.animation_frame_index += self.animation_speed
        if self.animation_frame_index >= len(self.animations[self.animation_status]):
            self.animation_frame_index = 0

        self.image = self.animations[self.animation_status][int(self.animation_frame_index)]

        if not self.animation_facing_right:
            self.image = pygame.transform.flip(self.image,True,False)

    def handleMovement(self):
        if self.velocity.x != 0:
            self.rect.x += self.velocity.x
        if self.velocity.y != 0:
            self.rect.y += self.velocity.y

    def update(self):
        self.handleAnimations()
        self.handleMovement()
        super().update()




class Wraith(AnimetableActor):
    def __init__(self, animations_path, scaleXY: Tuple, spawn_pos=(0, 0)):
        super().__init__(animations_path, scaleXY, spawn_pos=spawn_pos)

        self.velocity = pygame.math.Vector2(0,0)
        self.damage = 1
        self.run_speed = 1
        self.range = 20
        self.range_box = pygame.Rect(self.rect.left + 20 - (int(not self.animation_facing_right) * (self.range + 40)), self.rect.top, self.rect.width + self.range, self.rect.height)
        self.vision_box = pygame.Rect(int(not self.animation_facing_right)*(-150)+(self.rect.left-50), self.rect.top-50, self.rect.width+250, self.rect.height+50)


        self.target = PlayerActor
        self.behavior = FunctionType


    def runRight(self):
        self.velocity.x = self.run_speed
        self.animation_facing_right = True
        self.animation_status = "Walking"

    def runLeft(self):
        self.velocity.x = -self.run_speed
        self.animation_facing_right = False
        self.animation_status = "Walking"

    def stand(self):
        self.velocity.x = 0
        self.animation_status = "Idle"



    

    def handleBehavior(self):
        if self.vision_box.colliderect(self.target.rect):
            self.behavior = self.seekAndDestroy
        else:
            self.behavior = self.hangAround

    def seekAndDestroy(self):
        if self.range_box.colliderect(self.target):
            self.attackTarget()
        else:
            if self.rect.x < self.target.rect.x:
                self.runRight()
            elif self.rect.x > self.target.rect.x:
                self.runLeft()

    def hangAround(self):
        self.stand()


    def attackTarget(self):
        self.velocity.x = 0
        if self.animation_status != "Attacking":
            self.animation_frame_index = 0
            self.animation_status = "Attacking"

        if int(self.animation_frame_index) == 8:
            self.target.takeDamage(self.damage)
            tinted_image = self.target.image.copy()
            tinted_image.fill((utils.interpolate(self.damage, (0,3), (50,150)), 0, 0), special_flags=pygame.BLEND_ADD)
            self.target.image = tinted_image
    
    def handleDying(self):
        if self.animation_status != "Dying":
            self.animation_frame_index = 0
            self.animation_status = "Dying"
        if self.animation_frame_index > len(self.animations[self.animation_status])-1:
            self.kill()


    def update(self, world_shift):
        super().update()
        self.rect.x += world_shift
        if self.health > 0:
            self.handleBehavior()
            self.behavior()


            self.vision_box = pygame.Rect(int(not self.animation_facing_right)*(-150)+(self.rect.left-50), self.rect.top-50, self.rect.width+250, self.rect.height+50)
            self.range_box = pygame.Rect(self.rect.left + 20 - (int(not self.animation_facing_right) * (self.range + 40)), self.rect.top, self.rect.width + self.range, self.rect.height)

            self.bottom_rect = pygame.Rect(self.rect.left+5, self.rect.bottom-5, self.rect.width-10, 5)
            self.top_rect = pygame.Rect(self.rect.left+6, self.rect.top,self.rect.width-12, 5)
            self.left_rect = pygame.Rect(self.rect.left, self.rect.top, 5, self.rect.height-TILE_SIZE-5)
            self.right_rect = pygame.Rect(self.rect.right-5, self.rect.top, 5, self.rect.height-TILE_SIZE-5)

        else:
            self.handleDying()


class Wraith1(Wraith):
    def __init__(self, spawn_pos=(0, 0)):
        super().__init__("assets/wraith1/animations/", (90,110), spawn_pos=spawn_pos)
        self.damage = 0.8
        self.range = 10
        self.run_speed = 2
        self.health = 60

    def update(self, world_shift):
        return super().update(world_shift)



class Wraith2(Wraith):
    def __init__(self, spawn_pos=(0, 0)):
        super().__init__("assets/wraith2/animations/", (90, 110), spawn_pos=spawn_pos)
        self.health = 120
        self.damage = 2.5
        self.range = -40
        self.run_speed = 1


    def update(self, world_shift):
        return super().update(world_shift)



class Wraith3(Wraith):
    def __init__(self, spawn_pos=(0, 0)):
        super().__init__("assets/wraith3/animations/", (90,110), spawn_pos=spawn_pos)
        self.health = 100
        self.damage = 1.5
        self.range = 100
        self.run_speed = 4
        self.animation_speed = 0.5


    def update(self, world_shift):
        return super().update(world_shift)





class PlayerActor(AnimetableActor):
    def __init__(self, animations_path, scaleXY: Tuple, spawn_pos=(0, 0)):
        super().__init__(animations_path, scaleXY, spawn_pos=spawn_pos)


        self.health_rect_background = pygame.Rect(15, 15, 150, 20)
        self.health_rect = pygame.Rect(15,15,utils.interpolate(self.health, (0,100), (0,150)),20)
        self.health = 100

        # Movement
        self.velocity = pygame.math.Vector2(0,0)
        self.run_speed = 5
        self.jump_speed = 10.35
        self.jump_count = 2
        self.on_ground = False

        # Filled in Level
        self.enemies = Group()


    # Player actions
    def runRight(self):
        self.velocity.x = self.run_speed
        self.animation_facing_right = True
        self.animation_status = "running"

    def runLeft(self):
        self.velocity.x = -self.run_speed
        self.animation_facing_right = False
        self.animation_status = "running"

    def stand(self):
        self.velocity.x = 0
        self.animation_status = "idle"

    def jump(self):
        self.velocity.y = -self.jump_speed
        self.jump_count -= 1
        self.animation_status = "jumping"

    def resetJumpCount(self):
        self.jump_count = 2

    def takeDamage(self, damage):
        self.health -= damage
        if self.health < 0:
            self.health = 0
        self.health_rect = pygame.Rect(15,15,utils.interpolate(self.health, (0,100), (0,150)),20)

    def heal(self, heal):
        self.health += heal
        if self.health > 100:
            self.health = 100
        self.health_rect = pygame.Rect(15,15,utils.interpolate(self.health, (0,100), (0,150)),20)
        

    # questionable
    def interact(self, interactables):
        interactable: JetPack
        for interactable in interactables:
            if self.rect.colliderect(interactable.rect):
                interactable.interacted(self)
    
    # questionable
    def drop(self, interactables):
        interactable: JetPack
        for interactable in interactables:
            interactable.dropped()

    def attack(self):
        for enemy in self.enemies:
            enemy: Wraith
            if self.rect.colliderect(enemy.rect):
                enemy.health -= 20
                enemy.rect.x += 20 + (int(enemy.animation_facing_right)*-40)
                tinted_img = enemy.image.copy()
                tinted_img.fill((50, 0, 200), special_flags=pygame.BLEND_ADD)
                enemy.image = tinted_img

        

    def handleInput(self, events, keys, interactables):
        if keys[pygame.K_a] or keys[pygame.K_d]:
            if keys[pygame.K_a]:
                self.runLeft()
            if keys[pygame.K_d]:
                self.runRight()
        else:
            self.stand()

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    if self.jump_count > 0:
                        self.jump()
                if event.key == pygame.K_e:
                    self.interact(interactables)
                if event.key == pygame.K_f:
                    self.drop(interactables)
                if event.key == pygame.K_k:
                    self.attack()

            if event.type == pygame.MOUSEBUTTONDOWN:
                self.attack()


    def handleAnimationStatus(self):
        if not self.is_on_ground:
            self.animation_status = "jumping"
        if self.velocity.y > 1:
            self.animation_status = "falling"


    def drawHealthBar(self, display_surface):
        pygame.draw.rect(display_surface, 'black', self.health_rect_background)
        pygame.draw.rect(display_surface, COLOR["health"], self.health_rect)


    def update(self, events, keys, interactables):
        self.handleInput(events, keys, interactables)
        self.handleAnimationStatus()

        super().update()
        self.bottom_rect = pygame.Rect(self.rect.left+5, self.rect.bottom-5, self.rect.width-10, 5)
        self.top_rect = pygame.Rect(self.rect.left+6, self.rect.top,self.rect.width-12, 5)
        self.left_rect = pygame.Rect(self.rect.left, self.rect.top, 5, self.rect.height-TILE_SIZE-5)
        self.right_rect = pygame.Rect(self.rect.right-5, self.rect.top, 5, self.rect.height-TILE_SIZE-5)




class JetPack(Actor):
    def __init__(self, spawn_pos=(0, 0), scaleXY=(40, 100)):
        super().__init__("assets/jetpack.png", spawn_pos=spawn_pos, scaleXY=scaleXY)

        self.isGearedUp = False
        self.wearingActor = AnimetableActor
        self.particles = Group()
        self.particle_count = 10
        self.straight_image = pygame.transform.scale(pygame.image.load("assets/jetpack.png"), (40, 100))

    def interacted(self, interactor):
        self.isGearedUp = True
        self.wearingActor = interactor
    
    def dropped(self):
        self.wearingActor = None
        self.isGearedUp = False

    def handleInput(self, keys):
        if keys[pygame.K_KP_PLUS]:
            self.particle_count += 1
            print(self.particle_count)
        if keys[pygame.K_KP_MINUS]:
            self.particle_count -= 1
            print(self.particle_count)


        if keys[pygame.K_SPACE]:
            if self.wearingActor.velocity.y > -4:
                self.wearingActor.velocity.y -= 1.1

            if keys[pygame.K_a]:
                self.wearingActor.image = pygame.transform.rotate(self.wearingActor.image, 10)
                self.image = pygame.transform.rotate(self.image, 10)
                for _ in range(self.particle_count):
                    self.particles.add(Particle(self.rect.move(20,-10).midbottom))
                return

            if keys[pygame.K_d]:
                self.wearingActor.image = pygame.transform.rotate(self.wearingActor.image, -10)
                self.image = pygame.transform.rotate(self.image, -10)
                for _ in range(self.particle_count):
                    self.particles.add(Particle(self.rect.move(0,-10).midbottom))
                return

            for _ in range(self.particle_count):
                self.particles.add(Particle(self.rect.move(0,-10).midbottom))
 


    def update(self, world_shift, keys=None):
        super().update()
        self.image = self.straight_image
        self.particles.update(world_shift)
        if self.isGearedUp:
            self.rect.midright = self.wearingActor.rect.move(20 + int(not self.wearingActor.animation_facing_right)*40,0).midleft
            if keys != None:
                self.handleInput(keys)
        else:
            self.rect.x += world_shift





class Particle(Sprite):
    def __init__(self, pos):
        super().__init__()
        self.frame_index = 0
        self.animation_speed = 0.2

        self.frames = [
                # pygame.surface.Surface((40,40)).convert_alpha(),
                # pygame.surface.Surface((30,30)).convert_alpha(),
                pygame.surface.Surface((25,25)).convert_alpha(),
                pygame.surface.Surface((20,20)).convert_alpha(),
                # pygame.surface.Surface((18,18)).convert_alpha(),
                pygame.surface.Surface((15,15)).convert_alpha(),
                pygame.surface.Surface((10,10)).convert_alpha(),
                # pygame.surface.Surface((10,10)).convert_alpha(),
                pygame.surface.Surface((7,7)).convert_alpha(),
                # pygame.surface.Surface((7,7)).convert_alpha(),
                # pygame.surface.Surface((5,5)).convert_alpha(),
                # pygame.surface.Surface((3,3)).convert_alpha(),
            ]
        for particle in self.frames:
            # particle.fill((200,30,30,50))
            particle.fill((150,100,230,50))

        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center = pos)


    def animate(self):
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.frames):
            self.kill()
        else:
            self.image = self.frames[int(self.frame_index)]
    

    def update(self, world_shift):
        self.animate()
        self.rect.x += world_shift + (random() - 0.42)*10
        self.rect.y += 2 + (random()-0.5)*10
        
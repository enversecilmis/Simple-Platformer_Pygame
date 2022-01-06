from typing import Dict, List
import pygame
from pygame.event import Event
from pygame.sprite import GroupSingle, Sprite, Group, groupcollide
from actors import Actor, JetPack, PlayerActor, AnimetableActor, Wraith, Wraith1, Wraith2, Wraith3
from gamedata import COLOR, TILE_SIZE
from utils import loadImageSurfaceArray
from settings import WIDTH, HEIGHT, OFFSET


class Level:
    def __init__(self, display_surface: pygame.Surface, background_path: str, level_map: list[str]):
        self.display_surface = display_surface
        self.offset = OFFSET
        self.world_shift = 0
        self.tiles = Group()
        self.gravity = 0.7

        self.enemies = Group()
        self.player = PlayerActor("assets/player/animations/",(40,100))
        self.player_group = GroupSingle(self.player)
        self.actors = Group()
        self.actors.add(self.player)
        self.interactables = Group()
        self.dirty_sprites = Group()


        # ********** Enemy JetPacks *************
        # self.enemy_jetpacks = pygame.sprite.Group()

        self.background_sprites_group = loadParallaxBackgroundSpritesDoubleGroup(background_path)
        self.setupLevel(level_map)

        self.is_drawing_hit_boxes = False
        self.is_drawing_vision_boxes = False



    def handleDirtySprites(self):
        self.dirty_sprites = Group()

        for enemy in self.enemies:
            if enemy.rect.right > 0 and enemy.rect.left < WIDTH:
                self.dirty_sprites.add(enemy)
        for tile in self.tiles:
            if tile.rect.right > 0 and tile.rect.left < WIDTH:
                self.dirty_sprites.add(tile)
        for interactables in self.interactables:
            if interactables.rect.right > 0 and interactables.rect.left < WIDTH:
                self.dirty_sprites.add(interactables)

        self.dirty_sprites.add(self.finish)

    def handleWorldShift(self):
        # Sağa yaslanma durumu
        if self.player.rect.right > WIDTH - self.offset:
            self.world_shift = -self.player.run_speed
            self.player.rect.right = WIDTH - self.offset
        # Sola yaslanma durumu
        elif self.player.rect.left < self.offset:
            self.world_shift = self.player.run_speed
            self.player.rect.left = self.offset
        # Yaslanma yok
        else:
            self.world_shift = 0


    def handleParallaxBackground(self):
        for group_index, bg_layer_group in enumerate(self.background_sprites_group): # listedeki her bir grubu al
            bg_layer_group: Group
            for i,bg_sprite in enumerate(bg_layer_group): # gruplardaki her bir sprite'ı al
                bg_sprite: BackgroundSprite
                if bg_sprite.rect.right < 0: # soldan çıktıysa
                    bg_sprite.rect.left = bg_layer_group.sprites()[(i+1)%2].rect.right # diğer sprite'ın sağına koy
                elif bg_sprite.rect.left >= WIDTH: # sağdan çıktıysa
                    bg_sprite.rect.right = bg_layer_group.sprites()[(i+1)%2].rect.left # diğer sprite'ın soluna koy
            
            bg_layer_group.update(group_index*self.world_shift/5)
            bg_layer_group.draw(self.display_surface)

    
    def handleGravityForActors(self):
        collisions : Dict[AnimetableActor, List[Tile]]
        collisions = groupcollide(self.actors, self.tiles, False, False, gravityCollision)

        if collisions:
            for sprite in collisions:
                sprite: AnimetableActor
                if not sprite.velocity.y < 0:
                    sprite.velocity.y = 0
                    sprite.rect.bottom = collisions[sprite][0].rect.top

        for actor in self.actors:
            actor.velocity.y += self.gravity
        
        if self.player in collisions:
            self.player.resetJumpCount()
            self.player.is_on_ground = True
        else:
            self.player.is_on_ground = False



    def handleCollisions(self):
        collisions: Dict[AnimetableActor, List[Tile]]
        collisions = groupcollide(self.actors, self.tiles, False, False)

        for key in collisions:
            for tile in collisions[key]:
                tile: Sprite
                if tile.rect.colliderect(key.top_rect):
                    key.velocity.y = 0
                    key.rect.top = tile.rect.bottom
                elif tile.rect.colliderect(key.right_rect):
                    key.rect.right = tile.rect.left
                elif tile.rect.colliderect(key.left_rect):
                    key.rect.left = tile.rect.right

    def handleDeathOnOffset(self):

        for actor in self.actors:
            if actor.rect.y > 2000:
                actor.health = 0

    def run(self, events, keys):
        self.player.update(events, keys, self.interactables)
        self.interactables.update(self.world_shift, keys)
        self.tiles.update(self.world_shift)
        self.enemies.update(self.world_shift)

        self.handleParallaxBackground()
        self.handleGravityForActors()
        self.handleCollisions()
        self.handleWorldShift()
        self.handleDeathOnOffset()
        self.handleDirtySprites()
        self.handleCheats(events)


        for jet in self.interactables:
            jet: JetPack
            jet.particles.draw(self.display_surface)
            # pygame.draw.rect(self.display_surface, 'yellow', jet.rect, 1)
        

        

        self.dirty_sprites.draw(self.display_surface)
        self.finish.update(self.world_shift)
        self.player_group.draw(self.display_surface)
        self.player.drawHealthBar(self.display_surface)


        if self.is_drawing_hit_boxes:
            self.drawActorBoxes()

        # self.enemy_jetpacks.draw(self.display_surface)
        # self.enemy_jetpacks.update(self.world_shift)


        if self.finish.rect.colliderect(self.player.rect):
            return True
        else:
            return False



    def setupLevel(self, level_map):
        for row_index, row in enumerate(level_map):
            for col_index, col in enumerate(row):
                x = col_index*TILE_SIZE
                y = row_index*TILE_SIZE

                if col == 'G':
                    self.tiles.add(Tile((x,y), COLOR['grass']))
                elif col == 'S':
                    self.tiles.add(Tile((x,y), COLOR['soil']))
                elif col == 'P':
                    self.player.rect.center = (x,y)
                elif col == "1":
                    self.spawnEnemy(Wraith1((x,y)))
                elif col == "2":
                    self.spawnEnemy(Wraith2((x,y)))
                elif col == "3":
                    self.spawnEnemy(Wraith3((x,y)))
                elif col == "J":
                    self.interactables.add(JetPack((x,y)))
                elif col == "F":
                    self.finish = FinishTrigger((x,y))
        



    def spawnEnemy(self, enemy: Wraith):
        jetpack = JetPack()
        jetpack.interacted(enemy)
        # ***************** Enemy Jetpacks ***********
        # self.enemy_jetpacks.add(jetpack)
        self.player.enemies.add(enemy)
        enemy.target = self.player
        self.enemies.add(enemy)
        self.actors.add(enemy)
        


    def drawActorBoxes(self):
        for actor in self.actors:
            actor: AnimetableActor

            pygame.draw.rect(self.display_surface,'red',actor.bottom_rect)
            pygame.draw.rect(self.display_surface,'red',actor.top_rect)
            pygame.draw.rect(self.display_surface,'yellow',actor.left_rect)
            pygame.draw.rect(self.display_surface,'yellow',actor.right_rect)

            if self.is_drawing_vision_boxes and not type(actor) == PlayerActor:
                pygame.draw.rect(self.display_surface,'purple', actor.vision_box)
                pygame.draw.rect(self.display_surface,'red', actor.range_box)
    

    def handleCheats(self, events: List[Event]):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_KP1:
                    self.spawnEnemy(Wraith1((100,100)))
                if event.key == pygame.K_KP2:
                    self.spawnEnemy(Wraith2((100,100)))
                if event.key == pygame.K_KP3:
                    self.spawnEnemy(Wraith3((100,100)))
                if event.key == pygame.K_KP4:
                    if self.is_drawing_hit_boxes:
                        self.is_drawing_vision_boxes = not self.is_drawing_vision_boxes
                    if not self.is_drawing_vision_boxes:
                        self.is_drawing_hit_boxes = not self.is_drawing_hit_boxes

                if event.key == pygame.K_KP8:
                    self.player.takeDamage(10)
                if event.key == pygame.K_KP9:
                    self.player.heal(10)



    


def gravityCollision(sprite1: AnimetableActor, sprite2: Sprite):
    return sprite2.rect.colliderect(sprite1.bottom_rect.move((0, sprite1.velocity.y+1)))
     



def loadParallaxBackgroundSpritesGroup(background_path):
    background_surface_list = loadImageSurfaceArray(background_path, scaleXY=(WIDTH, HEIGHT))
    bg_group = pygame.sprite.Group()

    for bg_surface in background_surface_list:
        bg_group.add(BackgroundSprite(bg_surface))

    return bg_group


def loadParallaxBackgroundSpritesDoubleGroup(background_path):
    bg_double_group = []

    for bg_surface in loadImageSurfaceArray(background_path, scaleXY=(WIDTH, HEIGHT)):
        bg_group = pygame.sprite.Group()
        bg_group.add(BackgroundSprite(bg_surface))
        
        bg_sprite = BackgroundSprite(bg_surface)
        bg_sprite.update(WIDTH)
        bg_group.add(bg_sprite)

        bg_double_group.append(bg_group)

    return bg_double_group



class BackgroundSprite(pygame.sprite.Sprite):
    def __init__(self, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()

    def update(self, shift_x):
        self.rect.x += shift_x



class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, color):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE,TILE_SIZE))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=pos)

    def update(self, shift_x):
        self.rect.x += shift_x

class FinishTrigger(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((100,200))
        self.image.fill('green')
        self.rect = self.image.get_rect(midbottom = pos)
        

    def update(self, world_shift):
        self.rect.x += world_shift
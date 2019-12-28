import os

import pygame
import sys

FPS = 50

pygame.init()
size = WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode(size)

clock = pygame.time.Clock()
# основной персонаж
player = None

# группы спрайтов
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
wall_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
pygame.key.set_repeat(50, 50)


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self, field_size):
        self.dx = 0
        self.dy = 0
        self.field_size = field_size

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy
        if obj.rect.x < -obj.rect.width:
            obj.rect.x += (self.field_size[0] + 1) * obj.rect.width
        if obj.rect.y < -obj.rect.height:
            obj.rect.y += (self.field_size[1] + 1) * obj.rect.height
        if obj.rect.x >= (self.field_size[0]) * obj.rect.width:
            obj.rect.x += -(self.field_size[0] + 1) * obj.rect.width
        if obj.rect.y >= (self.field_size[1]) * obj.rect.height:
            obj.rect.y += -(self.field_size[1] + 1) * obj.rect.height

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        if tile_type == 'wall':
            super().__init__(tiles_group, all_sprites, wall_group)
        else:
            super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        self.stop = False

    def update(self):
        if pygame.sprite.spritecollideany(self, wall_group):
            self.stop = True
        else:
            self.stop = False

    def get_stop(self):
        return self.stop


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)

    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname).convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["ЗАСТАВКА", "",
                  "Правила игры",
                  "Если в правилах несколько строк,",
                  "приходится выводить их построчно"]

    fon = pygame.transform.scale(load_image('fon.png'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)


def mathcing_buttons():
    result = []
    player.rect.x += MOVE
    if pygame.sprite.spritecollideany(player, wall_group):
        player.rect.x -= MOVE
        result.append(key[pygame.K_RIGHT])
    player.rect.x -= MOVE
    if pygame.sprite.spritecollideany(player, wall_group):
        player.rect.x += MOVE
        result.append(key[pygame.K_LEFT])
    player.rect.y += MOVE
    if pygame.sprite.spritecollideany(player, wall_group):
        player.rect.y -= MOVE
        result.append(key[pygame.K_DOWN])
    player.rect.y -= MOVE
    if pygame.sprite.spritecollideany(player, wall_group):
        player.rect.y += MOVE
        result.append(key[pygame.K_UP])
    return result


def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


tile_images = {'wall': load_image('rock.png'), 'empty': load_image('floor.png')}
player_image = load_image('pers.png', -1)

tile_width = tile_height = 100

start_screen()
key_pressed = False
key = ''

running = True
MOVE = 10
player, level_x, level_y = generate_level(load_level('field.txt'))
time_left = 0
camera = Camera((level_x, level_y))
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            key = pygame.key.get_pressed()
            if not player.get_stop():
                if key[pygame.K_RIGHT]:
                    player.rect.x += MOVE
                if key[pygame.K_UP]:
                    player.rect.y -= MOVE
                if key[pygame.K_LEFT]:
                    player.rect.x -= MOVE
                if key[pygame.K_DOWN]:
                    player.rect.y += MOVE

    screen.fill((0, 0, 0))
    # изменяем ракурс камеры
    camera.update(player)
    # обновляем положение всех спрайтов
    for sprite in all_sprites:
        camera.apply(sprite)
    all_sprites.draw(screen)
    # tiles_group.draw(screen)
    player_group.draw(screen)
    player.update()
    print(player.stop)
    pygame.display.flip()
pygame.quit()

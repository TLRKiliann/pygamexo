#!/usr/bin/python3
# -*-coding:utf-8-*-

import os
import sys
from pygame.locals import *

if not pygame.font: print 'Attention, polices désactivées'
if not pygame.mixer: print 'Attention, son désactivé'

# import picture
def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print "Impossible de charger l'image :", name
        raise SystemExit, message
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()

# import sound
def load_sound(name):
    class NoneSound:
        def play(self): pass
    if not pygame.mixer:
        return NoneSound()
    fullname = os.path.join('data', name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error, message:
        print 'Impossible de charger le son :', wav
        raise SystemExit, message
    return sound

class Fist(pygame.sprite.Sprite):
    """Déplacer un poing fermé sur l'écran qui suit la souris"""
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)        #Appel du constructeur de Sprite
        self.image, self.rect = load_image('fist.bmp', -1)
        self.punching = 0
 
    def update(self):
        "Déplace le poing sur la position de la souris"
        pos = pygame.mouse.get_pos()
        self.rect.midtop = pos
        if self.punching:
            self.rect.move_ip(5, 10)
 
    def punch(self, target):
        "Renvoie true si le poing entre en collision avec la cible"
        if not self.punching:
            self.punching = 1
            hitbox = self.rect.inflate(-5, -5)
            return hitbox.colliderect(target.rect)
 
    def unpunch(self):
        "Appelé pour faire revenir le poing"
        self.punching = 0

class Chimp(pygame.sprite.Sprite): 
    """Déplace un singe à travers l'écran. Elle peut faire tournoyer
    le singe quand il est frappé."""
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)        #Appel du constructeur de Sprite
        self.image, self.rect = load_image('chimp.bmp', -1)
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.rect.topleft = 10, 10
        self.move = 9
        self.dizzy = 0
 
    def update(self):
        "Déplace ou fait tournoyer, suivant l'état du singe"
        if self.dizzy:
            self._spin()
        else:
            self._walk()
 
    def _walk(self):
        "Déplacer le singe à travers l'écran, et le faire pivoter à la fin"
        newpos = self.rect.move((self.move, 0))
        if not self.area.contains(newpos):
            if self.rect.left < self.area.left or \
                self.rect.right > self.area.right:
            self.move = -self.move
            newpos = self.rect.move((self.move, 0))
            self.image = pygame.transform.flip(self.image, 1, 0)
        self.rect = newpos
 
    def _spin(self):
        "Faire tournoyer l'image du singe"
        center = self.rect.center
        self.dizzy += 12
        if self.dizzy >= 360:
            self.dizzy = 0
            self.image = self.original
        else:
            rotate = pygame.transform.rotate
            self.image = rotate(self.original, self.dizzy)
        self.rect = self.image.get_rect(center=center)
 
    def punched(self):
        "Entraine le tournoiement du singe"
        if not self.dizzy:
            self.dizzy = 1
            self.original = self.image

# Main app of pygame
pygame.init()
screen = pygame.display.set_mode((468, 60))
pygame.display.set_caption('Monkey Fever')
pygame.mouse.set_visible(0)


background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill((250, 250, 250))

if pygame.font:
    font = pygame.font.Font(None, 36)
    text = font.render("Pummel The Chimp, And Win $$$", 1, (10, 10, 10))
    textpos = text.get_rect(centerx=background.get_width()/2)
    background.blit(text, textpos)

screen.blit(background, (0, 0))
pygame.display.flip()

whiff_sound = load_sound('whiff.wav')
punch_sound = load_sound('punch.wav')
chimp = Chimp()
fist = Fist()
allsprites = pygame.sprite.RenderPlain((fist, chimp))
clock = pygame.time.Clock()

while 1:
    clock.tick(60)

for event in pygame.event.get():
    if event.type == QUIT:
        return
    elif event.type == KEYDOWN and event.key == K_ESCAPE:
        return
    elif event.type == MOUSEBUTTONDOWN:
        if fist.punch(chimp):
            punch_sound.play() #frappé
            chimp.punched()
        else:
            whiff_sound.play() #raté
    elif event.type == MOUSEBUTTONUP:
        fist.unpunch()

allsprites.update()

screen.blit(background, (0, 0))
allsprites.draw(screen)
pygame.display.flip()
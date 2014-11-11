# -*- coding: utf8 -*-
from screen import PyGameScreen as Screen
import pygame
from pygame.locals import *
from utils import *

class Runner(object):
    '''Objeto encarregado de rodar o loop principal da simulação.
    
    Objetos da classe runner monitoram as entradas e saídas do usuário e coordenam
    um objeto world para atualizar e desenhar objetos na tela.'''

    def __init__(self, world, screen=(800, 600), fps=60, background=(255, 255, 255)):
        self.world = world
        self.fps = fps
        self.background = background
        self.screen = screen
        self._screen = Screen(*screen)
        self._clock = clock = pygame.time.Clock()
        self._keydown_callbacks = {}
        self._keyup_callbacks = {}
        self._longpress_callbacks = {}
        self._longpress_keys = set()
        self._mousemotion_callbacks = []

    def register_mouse_motion(self, callback):
        '''Registra uma função que é sempre chamada com as coordendas x, y do 
        ponteiro do mouse'''

        self._mousemotion_callbacks.append(callback)

    def register_key_down(self, key, callback):
        '''Registra uma função de callback que é chamada sempre que a tecla key 
        for apertada'''

        key = KEY_CONVERSIONS[key]
        L = self._keydown_callbacks.setdefault(key, [])
        L.append(callback)

    def register_key_up(self, key, callback):
        '''Registra uma função de callback que é chamada sempre que a tecla key 
        for apertada'''

        key = KEY_CONVERSIONS[key]
        L = self._keyup_callbacks.setdefault(key, [])
        L.append(callback)

    def register_long_press(self, key, callback):
        '''Registra uma função de callback que é chamada em todos os frames que 
        que a tecla key estiver apertada'''

        key = KEY_CONVERSIONS[key]
        L = self._longpress_callbacks.setdefault(key, [])
        L.append(callback)

    def on_key_down(self, key):
        '''Executa todos os callbacks associados à tecla fornecida'''

        # Executa callbacks de keydown
        callbacks = self._keydown_callbacks.get(key)
        if callbacks is not None:
            for cb_func in callbacks:
                cb_func()

        # Registra tecla de longpress
        if key in self._longpress_callbacks:
            self._longpress_keys.add(key)

    def on_key_up(self, key):
        '''Executa todos os callbacks de keyup associados à tecla fornecida'''
        # Executa callbacks de keyup
        callbacks = self._keyup_callbacks.get(key)
        if callbacks is not None:
            for cb_func in callbacks:
                cb_func()

        # Limpa tecla da lista de longpress
        self._longpress_keys.discard(key)


    def on_long_press(self):
        '''Executa todos os callbacks de longpress para as teclas pressionadas'''

        for key in self._longpress_keys:
            callbacks = self._longpress_callbacks.get(key)
            if callbacks is not None:
                for cb_func in callbacks:
                    cb_func()

    def on_mouse_motion(self, pos):
        '''Executa os callbacks acionados pelo movimento do mouse'''

        x, y = pos
        y = self._screen.height / 2. - y
        for cb_func in self._mousemotion_callbacks:
            cb_func(x, y)

    def run(self):
        '''Roda o loop principal da simulação'''

        self.init()

        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.quit()
                elif event.type == KEYDOWN:
                    self.on_key_down(event.key)
                elif event.type == KEYUP:
                    self.on_key_up(event.key)
                elif event.type == MOUSEMOTION:
                    # TODO: converter para coordenadas locais em screen
                    self.on_mouse_motion(event.pos)

            self.on_long_press()
            self._screen.clear(self.background)

            # Atualiza a física
            dt = 1. / self.fps
            self.world.update(dt)

            # Desenha objetos
            self.world.draw(self._screen)

            pygame.display.update()
            self._clock.tick(self.fps)

    def init(self):
        pygame.init()

    def quit(self):
        '''Método acionado quando um evento de saída é ativado'''

        pygame.quit()
        raise SystemExit()

KEY_CONVERSIONS = {
    '<up>': K_UP, '<down>': K_DOWN, '<left>': K_LEFT, '<right>': K_RIGHT,
}

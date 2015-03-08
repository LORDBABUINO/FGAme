#-*- coding: utf8 -*-

__all__ = ['globalvars']

class Globals(object):
    '''Classe que atua apenas como um namespace para as variáveis globais.'''

    # Propriedades relativas ao backend
    backend = None
    backends = ['pygame', 'pygamegfx', 'pygamegl', 'sdl2']
    backends_conf = dict(
        pygame    = ('PyGameCanvas', 'PyGameInput', 'StepperMainLoop'),
        pygamegfx = ('PyGameGFXCanvas', 'PyGameInput', 'StepperMainLoop'),
        pygamegl  = ('PyGameGLCanvas', 'PyGameInput', 'StepperMainLoop'),
        sdl2      = ('SDL2Canvas', 'SDL2Input', 'StepperMainLoop'),
        pyglet    = ('PyGletCanvas', 'PyGletInput', 'PyGletMainLoop'),
        kivy      = ('KivyCanvas', 'KivyInput', 'KivyMainloop'),
    )
    input_class = None
    input_object = None
    mainloop_class = None
    mainloop_object = None
    screen_width = 800
    screen_height = 600
    screen_shape = (800, 600)
    screen_class = None
    screen_object = None
    has_init = False
    
    # Configurações e logging
    app_name = None
    conf_path = None

globalvars = Globals()

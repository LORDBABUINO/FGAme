#-*- coding: utf8 -*-
import importlib
from FGAme.screen import Screen
from FGAme.listener import InputListener
from FGAme.mainloop import MainLoop

SUPPORTED_BACKENDS = ['sdl2', 'pygamegfx', 'pygame', 'kivy', 'pyglet', 'pygamegl']
BACKEND = None
MODULE = None
HAS_INIT = None
SCREEN_CLS = None
SCREEN_CURR = None
INPUT_LISTENER_CLS = None
INPUT_LISTENER_CURR = None
MAINLOOP_CURR = None
MAINLOOP_CLS = MainLoop

def set_backend(backend=SUPPORTED_BACKENDS):
    '''Define o backend a ser utilizado pela FGAme.'''

    global BACKEND, MODULE

    if isinstance(backend, str):
        if backend not in SUPPORTED_BACKENDS:
            raise ValueError('invalid backend: %s' % backend)
        BACKEND = backend
        MODULE = importlib.import_module('FGAme.backends.%s_be' % backend)
    else:
        for be in backend:
            try:
                set_backend(be)
                break
            except (ImportError, NotImplementedError):
                continue
        else:
            raise RuntimeError('none of the supported backends is available')

def init():
    '''Inicia a FGAme.'''

    global HAS_INIT

    if not HAS_INIT:
        HAS_INIT = True
        if not BACKEND:
            set_backend()
        MODULE.init()

        # Salva classes especializadas
        D = globals()
        for cls in vars(MODULE).values():
            if isinstance(cls, type):
                if issubclass(cls, Screen) and cls is not Screen:
                    D['SCREEN_CLS'] = cls
                if issubclass(cls, InputListener) and cls is not InputListener:
                    D['INPUT_LISTENER_CLS'] = cls
                if issubclass(cls, MainLoop) and cls is not MainLoop:
                    D['MAINLOOP_CLS'] = cls

def get_screen(new=False, width=800, height=600, *args, **kwds):
    '''Retorna um objeto do tipo Screen. 
    
    Caso new seja Falso (padrão) retorna a última instância criada. Normalmente
    isto é desejável já que raramente precisaremos de dois objetos Screen
    diferentes rodando simultaneamente.
    '''

    global SCREEN_CURR
    init()

    if SCREEN_CURR is None or new:
        new = SCREEN_CURR = SCREEN_CLS(width, height, *args, **kwds)
        return new
    else:
        return SCREEN_CURR

def get_input_listener(new=False, *args, **kwds):
    '''Retorna um objeto do tipo InputListener. 
    
    Caso new seja Falso (padrão) retorna a última instância criada. Normalmente
    isto é desejável já que raramente precisaremos de dois objetos InputListener
    diferentes rodando simultaneamente.
    '''

    global INPUT_LISTENER_CURR
    init()

    if INPUT_LISTENER_CURR is None or new:
        new = INPUT_LISTENER_CURR = INPUT_LISTENER_CLS(*args, **kwds)
        return new
    else:
        return INPUT_LISTENER_CURR
        
def get_mainloop(new=False, *args, **kwds):
    '''Retorna um objeto do tipo InputListener. 
    
    Caso new seja Falso (padrão) retorna a última instância criada. Normalmente
    isto é desejável já que raramente precisaremos de dois objetos InputListener
    diferentes rodando simultaneamente.
    '''

    global MAINLOOP_CURR
    init()

    if MAINLOOP_CURR is None or new:
        new = MAINLOOP_CURR = MAINLOOP_CLS(*args, **kwds)
        return new
    else:
        return MAINLOOP_CURR
        

if __name__ == '__main__':
    init()

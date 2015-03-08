#-*- coding: utf8 -*-
import importlib
from FGAme.core import log
from FGAme.core.globalvars import globalvars 

def supports_backend(backend):
    '''Retorna True caso o sistema suporte o backend selecionado'''
    
    if backend in ['pygame', 'pygamegfx', 'pygamegl']:
        try:
            import pygame  # @UnusedImport
            return True
        except ImportError:
            return False
    elif backend == 'sdl2':
        try:
            import sdl2  # @UnusedImport
            return True
        except ImportError:
            return False
    else:
        raise ValueError('invalid backend: %s' % backend)

def set_backend(backend=None):
    '''Define o backend a ser utilizado pela FGAme.
    
    Se for chamada sem nenhum argumento, tenta carregar os backends na ordem
    dada por globalvars.backends. Se o argumento for uma lista, tenta carregar os
    backends na ordem especificada pela lista.'''

    # Função chamada sem argumentos
    if backend is None:
        if globalvars.backend is None:
            backend = globalvars.backends
        else:
            return # backend já configurado!
    
    # Previne modificar o backend
    if globalvars.backend is not None:
        if globalvars.backend != backend:
            raise RuntimeError('already initialized to %s, cannot change the backend' % globalvars.backend)
        else:
            return
    
    # Carrega backend pelo nome
    if isinstance(backend, str):
        if not supports_backend(backend):
            raise ValueError('%s backend is not supported in your system' % backend)
        
        screen, input_, mainloop = globalvars.backends_conf[backend]
        core = importlib.import_module('FGAme.core')
        globalvars.screen_class = getattr(core, screen)
        globalvars.input_class = getattr(core, input_)
        globalvars.mainloop_class = getattr(core, mainloop)
        globalvars.backend = backend
        log.info('conf: Backend set to %s' % backend)
        
    # Carrega backend a partir de uma lista
    else:
        for be in backend:
            if supports_backend(be):
                set_backend(be)
                break
        else:
            msg = 'none of the requested backends are available.'
            if 'pygame' in backend:
                msg += (
                    '\nSupported backends are:'
                    '\n    * pygame'
                    '\n    * sdl2'
                    # '\n    * kivy'
                )
            raise RuntimeError(msg)

def set_screen(shape=None):
    '''Configura a tela com a resolução dada em shape'''

    if globalvars.screen_object is not None:
        raise RuntimeError('cannot set the screen twice')
    
    # Configura as variáveis globais
    if shape is None:
        shape = globalvars.screen_shape
    width, height = globalvars.screen_width, globalvars.screen_height = shape
    
    # Inicializa o objeto screen
    set_backend()
    globalvars.screen_object = globalvars.screen_class(width, height)
    
def init():
    '''Inicializa todas as classes relevantes do FGAme'''
    
    # Previne a inicialização repetida
    if globalvars.has_init:
        return
    else:
        set_backend()
    
    # Inicializa o vídeo
    if globalvars.screen_object is None:
        set_screen()
    
    # Inicializa o input e o mainloop
    globalvars.input_object = globalvars.input_class()
    globalvars.mainloop_object = globalvars.mainloop_class()
    globalvars.has_init = True

if __name__ == '__main__':
    init()

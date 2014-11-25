#-*- coding: utf8 -*-
from FGAme.utils import *
from functools import partial

class Listener(object):
    '''Objeto que possui a função 'listen' para registrar callbacks associados 
    a eventos
    '''

    EVENTS = {}

    def __init__(self):
        self._auto_register_listeners(self)

    def listen(self, *args):
        '''Registra um callback a um determinado evento'''

        # Obtem nome do evento e registrador especial, caso especificado
        event = args[0]
        try:
            n_cb, n_f = self.EVENTS[event]
        except KeyError:
            raise ValueError('unknown event: %s' % event)
        if hasattr(self, 'listen_%s' % event.replace('-', '_')):
            method = getattr(self, 'listen_%s' % event.replace('-', '_'))
            return method(*args[1:])
        if hasattr(self, '_listen_%s' % event.replace('-', '_')):
            method = getattr(self, '_listen_%s' % event.replace('-', '_'))
            return method(*args[1:])

        # Extrai argumentos de callback, função de callback
        cb_args = args[1:1 + n_cb]
        try:
            cb_func = args[1 + n_cb]
        except IndexError:
            def decorator(func):
                new_args = args + (func,)
                return self.listen(*new_args)
            return decorator

        # Extrai argumentos opcionais
        f_args = f_kwargs = None
        tail = list(args[2 + n_cb:])
        if tail:
            f_args = tail.pop(0)
        if tail:
            f_kwargs = tail.pop(0)
        args_kwds = (None if (f_kwargs is None and f_args is None)
                          else (f_args or (), f_kwargs or {}))

        # Registra callback no dicionário
        if cb_args:
            D = self._get_cb_container(event, dict)
            L = D.setdefault(cb_args, [])
            L.append((cb_func, args_kwds))
        else:
            L = self._get_cb_container(event, list)
            L.append((cb_func, args_kwds))

    def _get_cb_container(self, event, container):
        attr = '_cb_' + event.replace('-', '_')
        try:
            C = getattr(self, attr)
            if C is None:
                C = container()
                setattr(self, attr, C)
            return C
        except AttributeError:
            C = container()
            setattr(self, attr, C)
            return C

    def trigger(self, event, *args):
        '''Aciona um evento com os argumentos especificados.'''

        try:
            n_cb, n_f = self.EVENTS[event]
        except KeyError:
            raise ValueError('unknown event: %s' % event)
        cb_args = args[:n_cb]
        f_args = args[n_cb: n_cb + n_f]
        attr = '_cb_' + event.replace('-', '_')
        self._cb_run(getattr(self, attr, None), cb_args, f_args)

    def _cb_run(self, registered, cb_args, fargs):
        '''Executa um callback'''

        if registered is None:
            pass
        elif cb_args:
            self._cb_run(registered.get(cb_args, ()), None, fargs)
        else:
            for cb, aux in registered:
                if aux is None:
                    if fargs:
                        cb(*fargs)
                    else:
                        cb()
                else:
                    args, kwargs = aux
                    cb(*(fargs + args), **kwargs)

    def _auto_register_func(self, func, L=None):
        '''Register a single function by checking its cb_signals attribute'''

        if L is None:
            L = func.cb_signals
        for args in L:
            args = list(args)
            evname = args[0]
            nargs = self.EVENTS[evname][0]
            args.insert(nargs + 1, func)
            self.listen(*args)

    def _auto_register_listeners(self, obj=None):
        '''Registra listeners definidos pelo usuário'''

        register = self._auto_register_func
        if obj is None:
            obj = self
        for attr in dir(type(obj)):
            cls_method = getattr(type(obj), attr)
            if hasattr(cls_method, 'cb_signals'):
                register(getattr(obj, attr))

class InputListener(Listener):
    '''Objetos do tipo listener escutam eventos de entrada do usuário e executam
    os callbacks de resposta registrados a estes eventos'''

    KEY_CONVERSIONS = {}
    EVENTS = {'long-press': (1, 0),
              'key-up': (1, 0),
              'key-down': (1, 0),
              'mouse-motion': (0, 1),
              'mouse-click': (1, 1),
    }

    #===========================================================================
    # Registra callbacks de tipos específicos de eventos
    #===========================================================================
    def __init__(self):
        self._cb_key_down = {}
        self._cb_key_up = {}
        self._cb_long_press = {}
        self._longpress_keys = set()
        self._cb_mouse_motion = []
        self._cb_mouse_click = {}

    def listen_mouse_motion(self, callback=None, args=None, kwargs=None):
        '''Registra uma função que é sempre chamada com as coordendas x, y do 
        ponteiro do mouse'''

        if callback is None:
            return partial(self.listen_mouse_motion)
        self.listen('mouse-motion', callback, args, kwargs)

    def listen_mouse_click(self, button, callback=None, args=None, kwargs=None):
        '''Registra uma função que é sempre chamada com as coordendas x, y do 
        ponteiro do mouse'''

        if callback is None:
            return partial(self.listen_mouse_click, button)
        aux = (args or (), kwargs or {}) if (args or kwargs) else None
        L = self._cb_mouse_click.setdefault(button, [])
        L.append((callback, aux))

    def listen_key_down(self, key, callback=None, args=None, kwargs=None):
        '''Registra uma função de callback que é chamada sempre que a tecla key 
        for apertada'''

        if callback is None:
            return partial(self.listen_key_down, key)
        aux = (args or (), kwargs or {}) if (args or kwargs) else None
        key = self.KEY_CONVERSIONS.get(key, key)
        L = self._cb_key_down.setdefault(key, [])
        L.append((callback, aux))

    def listen_key_up(self, key, callback=None, args=None, kwargs=None):
        '''Registra uma função de callback que é chamada sempre que a tecla key 
        for apertada'''

        if callback is None:
            return partial(self.listen_key_up, key)
        aux = (args or (), kwargs or {}) if (args or kwargs) else None
        key = self.KEY_CONVERSIONS.get(key, key)
        L = self._cb_key_up.setdefault(key, [])
        L.append((callback, aux))

    def listen_long_press(self, key, callback=None, args=None, kwargs=None):
        '''Registra uma função de callback que é chamada em todos os frames que 
        que a tecla key estiver apertada'''

        if callback is None:
            return partial(self.listen_long_press, key)
        aux = (args or (), kwargs or {}) if (args or kwargs) else None
        key = self.KEY_CONVERSIONS.get(key, key)
        L = self._cb_long_press.setdefault(key, [])
        L.append((callback, aux))

    #===========================================================================
    # Callbacks globais para cada tipo de evento
    #===========================================================================
    def on_key_down(self, key):
        '''Executa todos os callbacks associados à tecla fornecida'''

        callbacks = self._cb_key_down.get(key)
        if callbacks is not None:
            for cb_func, aux in callbacks:
                if aux is None:
                    cb_func()
                else:
                    args, kwargs = aux
                    cb_func(*args, **kwargs)

        # Registra tecla de longpress
        if key in self._cb_long_press:
            self._longpress_keys.add(key)

    def on_key_up(self, key):
        '''Executa todos os callbacks de keyup associados à tecla fornecida'''

        callbacks = self._cb_key_up.get(key)
        if callbacks is not None:
            for cb_func, aux in callbacks:
                if aux is None:
                    cb_func()
                else:
                    args, kwargs = aux
                    cb_func(*args, **kwargs)

        # Limpa tecla da lista de longpress
        self._longpress_keys.discard(key)

    def on_long_press(self):
        '''Executa todos os callbacks de longpress para as teclas pressionadas'''

        for key in self._longpress_keys:
            callbacks = self._cb_long_press.get(key)
            if callbacks is not None:
                for cb_func, aux in callbacks:
                    if aux is None:
                        cb_func()
                    else:
                        args, kwargs = aux
                        cb_func(*args, **kwargs)

    def on_mouse_motion(self, pos):
        '''Executa os callbacks acionados pelo movimento do mouse'''

        if self._cb_mouse_motion:
            x, y = pos
            y = self._screen.height / 2. - y
            for cb_func, aux in self._cb_mouse_motion:
                if aux is None:
                    cb_func((x, y))
                else:
                    args, kwargs = aux
                    cb_func((x, y) * args, **kwargs)

    #===========================================================================
    # Passo de resposta a eventos executado em cada loop
    #===========================================================================
    def step(self):
        '''Função executada a cada loop, que investiga todos os eventos de 
        usuários que ocorreram. Deve ser reimplementada nas classes filho'''

        raise NotImplementedError

#===============================================================================
# Funções úteis e decoradores
#===============================================================================
def listen(*args):
    '''Decorador que registra uma função como sendo um callback de um 
    determinado sinal'''

    def decorator(func):
        try:
            L = func.cb_signals
        except AttributeError:
            L = func.cb_signals = []
        finally:
            L.append(args)
        return func

    return decorator

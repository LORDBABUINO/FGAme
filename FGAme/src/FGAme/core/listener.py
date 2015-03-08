#-*- coding: utf8 -*-
from functools import partial

class Signal(object):
    '''Classe representa um sinal que pode ser ouvido por um objeto'''
    
    sig_args = ()

    def __init__(self, name, num_args=0, delegate=None):
        self.name = name
        self.num_args = num_args
        self.delegate = delegate
        
    def init(self, obj):
        '''Inicializa o Handler associado ao sinal'''
        
        func_name = 'on_%s' % self.name.replace('-', '_')
        obj._handlers[self.name] = handler = Handler()
        if hasattr(obj, func_name):
            func = getattr(obj, func_name)
            handler.add(func)
            
    def validate_args(self, args):
        '''Valida os argumentos que parametrizam o sinal'''

        if args != ():
            raise ValueError('invalid signal arguments: %r' % args)
        
    def split_args(self, args):
        '''Divide os argumentos passados para um objeto Signal na tupla
        (key, func).'''
        
        L = list(args)
        try:
            sig_args = args[:self.num_args]
            func = args[self.num_args]
            if len(args) > self.num_args + 1:
                x = self.num_args + 1
                y = len(self.args)
                raise ValueError('expected at most %s parameters, got %s' % (x, y))
        except IndexError:
            x = self.num_args + 1
            y = len(self.args)
            raise ValueError('expected at least %s parameters, got %s' % (x, y))
        
        if sig_args:
            key = (self.name,) + sig_args
        else:
            key = self.name
            
        return key, func
    
    def register(self, obj, func, **kwds):
        '''Registra uma função func para responder aos sinais emitidos a partir
        do objeto obj'''
        
        try:
            handler = getattr(obj, self.handler_attr_name)
        except AttributeError:
            handler = Handler()
            setattr(obj, self.handler_attr_name, handler)
        handler.add_handler(func, **kwds)

class PSignal(Signal):
    '''Representa um sinal parametrizado'''
    
    # TODO: remover o objeto PSignal
    
    def __init__(self, name, *args, **kwds):
        self.sig_args = args
        super(PSignal, self).__init__(name, **kwds)
        
    def init(self, obj):
        '''Inicializa o Handler associado ao sinal'''
        
        pass
    
    def register(self, obj, func, *args, **kwds):
        '''Registra uma função func para responder aos sinais emitidos a partir
        do objeto obj'''
        
        if len(args) != self.num_args:
            raise ValueError('expected %s args, got %s' % (self.num_args, len(args)))
        try:
            handler = getattr(obj, self.handler_attr_name)
        except AttributeError:
            handler = Handler()
            setattr(obj, self.handler_attr_name, handler)
        handler.add_handler(func, **kwds)

    
class Handler(object):
    '''Resolve todas as funções de callback associadas a um sinal.
    
    Controla o registro e remoção de funções.'''
    
    __slots__ = ['handlers']
    
    def __init__(self):
        self.handlers = None
    
    def add(self, func, **kwds):
        if kwds:
            func = partial(func, **kwds)
        if self.handlers is not None:
            self.handlers.append(func)
        else:
            self.handlers = [func]

    def remove(self, func):
        pass

    def __call__(self, *args):
        if self.handlers is None:
            return
        
        if args:
            for func in self.handlers:
                func(*args)
        else:
            for func in self.handlers:
                func()
                
class Listener(object):
    '''Objeto que possui a função 'listen' para registrar callbacks associados 
    a eventos.
    
    
    Exemplo
    -------
    
    Criamos uma class que define alguns sinais simples
    
    >>> class Foo(Listener):
    ...     bar = Signal('bar')
    ...
    ...     def on_bar(self):
    ...        print('hello bar!')
    
    Podemos disparar o sinal 'bar' para executar o método `on_bar()` que já é
    automaticamente associado a este sinal.
    
    >>> foo = Foo()
    >>> foo.trigger('bar')
    hello bar!
    
    Agora definimos uma função para mostrar como se cria e registra um handler
    para o sinal 'bar' 
    
    >>> def say_hello():
    ...     print('hello world!')
    
    Registramos a função e depois emitimos o sinal 'bar'. Agora as duas funções
    são executadas
    
    >>> foo.listen('bar', say_hello)
    >>> foo.trigger('bar')
    hello bar!
    hello world!
    '''

    def __init__(self):
        # Introspecção dos sinais registrados na classe
        self._signals = {}
        self._handlers = {}
        self._handlers_delegates = {}
        tt = type(self)
        for attr in dir(tt):
            signal = getattr(tt, attr)
            if isinstance(signal, Signal):
                self._signals[signal.name] = signal
                signal.init(self)
                
        # Procura todos os métodos marcados com o decorador @listen
        for attr in dir(tt):
            cls_method = getattr(tt, attr)
            for (args, kwds) in getattr(cls_method, 'cb_signals', []):
                func = getattr(self, attr)
                args = args + (func,)
                self.listen(*args, **kwds)

    def listen(self, signal, *args, **kwds):
        '''Registra um callback a um determinado evento. Pode ser chamada
        como decorador ou como função.'''

        # Obtem nome do evento e registrador especial, caso especificado
        try:
            signal = self._signals[signal]
        except KeyError:
            raise ValueError('unknown event: %s' % signal)

        # Extrai a chave a partir do sinal e dos parâmetros
        if signal.sig_args:
            N = len(signal.sig_args)
            sig_args = args[:N]
            args = args[N:]
        else:
            key = signal.name
            sig_args = ()

        # Verifica se a função foi chamada como decorador ou não
        if not args:
            handler = self.get_handler(signal.name, *sig_args)
            def decorator(func):
                args = sig_args + (func,)
                self.listen(signal.name, *args, **kwds)
                return func
            return decorator
        elif len(args) == 1:
            if signal.delegate is not None:
                delegate = getattr(self, signal.delegate)
                args = sig_args + args
                delegate.listen(signal.name, *args, **kwds)
            else:
                handler = self.get_handler(signal.name, *sig_args)
                handler.add(args[0], **kwds)
        else:
            x = len(signal.sig_args)
            y = len(args)
            raise TypeError('expected %s or %s arguments, got %s' % (x, x+1, y))
        
    def get_handler(self, signal, *args):
        '''A partir do nome do sinal e dos seus argumentos, retorna o `handler`
        apropriado'''
        
        if not args:
            return self._handlers[signal]
        else:
            key = (signal,) + args
            try:
                return self._handlers[key]
            except KeyError:
                handler = self._handlers[key] = Handler()
                return handler

    def trigger(self, key, *args):
        '''Aciona um evento com os argumentos especificados.'''

        try:
            handler = self._handlers[key]
        except KeyError:
            # Carrega o sinal para obter o evento no caso de falha
            name = key[0] if isinstance(key, tuple) else key
            try:
                signal = self._signals[name]
            except KeyError:
                raise ValueError('unknown signal: %r' % name)
            
            # Trata a falha
            if signal.delegate is not None:
                raise ValueError('cannot trigger delegate events')
            elif len(key) == len(signal.sig_args) + 1:
                handler = self._handlers[key] = Handler()
            else:                
                sig_args = key[1:] if isinstance(key, tuple) else ()
                x = len(signal.sig_args)
                y = len(sig_args)
                raise ValueError('bad format for %s event: expect %s signal args, got %s' % (name, x, y))
            
        handler(*args)

#===============================================================================
# Funções úteis e decoradores
#===============================================================================
def listen(*args, **kwds):
    '''Decorador que registra uma função como sendo um callback de um 
    determinado sinal'''

    def decorator(func):
        try:
            L = func.cb_signals
        except AttributeError:
            L = func.cb_signals = []
        finally:
            L.append((args, kwds))
        return func

    return decorator

def signal(*args, **kwds):
    '''Define um sinal.
    
    Possui a assinatura signal(nome, [arg1, ...,[ num_args]]), onde arg_i são
    strings com os nomes dos argumentos e o valor opcional num_args é um número
    representando o número de argumentos para o handler padrão.'''
    
    if 'num_args' in kwds:
        num_args = kwds['num_args']
    elif isinstance(args[-1], int):
        num_args = args[-1]
        args = args[:-1]
    else:
        num_args = 0
    
    kwds['num_args'] = num_args
    if len(args) == 1:
        return Signal(args[0], **kwds)
    else:
        return PSignal(*args, **kwds)
        

if __name__ == '__main__':
    import doctest
    doctest.testmod()


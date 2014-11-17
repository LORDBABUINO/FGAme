#-*- coding: utf8 -*-
from math import trunc

def shadow_x(A, B):
    '''Retorna o tamanho da sombra comum entre os objetos A e B no eixo x. 
    Caso não haja superposição, retorna um valor negativo que corresponde ao 
    tamanho do buraco'''

    return min(A.xmax, B.xmax) - max(A.xmin, B.xmin)

def shadow_y(A, B):
    '''Retorna o tamanho da sombra comum entre os objetos A e B no eixo y. 
    Caso não haja superposição, retorna um valor negativo que corresponde ao 
    tamanho do buraco'''

    return min(A.ymax, B.ymax) - max(A.ymin, B.ymin)


class lazy(object):
    '''Implementa uma propriedade "preguiçosa": ela é calculada apenas durante o 
    primeiro uso e não durante a inicialização do objeto.'''

    def __init__(self, func):
        self.func = func

    def __get__(self, obj, cls=None):
        value = self.func(obj)
        setattr(obj, self.func.__name__, value)
        return value


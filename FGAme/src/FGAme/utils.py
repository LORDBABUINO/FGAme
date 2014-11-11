# -*- coding: utf8 -*-
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



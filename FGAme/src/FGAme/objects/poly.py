# -*- coding: utf8 -*-
from __future__ import absolute_import
if __name__ == '__main__':
    __package__ = 'FGAme.objects'; import FGAme.objects

import pygame
from math import trunc, sin
from .base import PhysicsObject
from .aabb import AABB
from ..mathutils import Vector2D, area, inertia, center_of_mass, dot, cross, pi
from ..collision import get_collision, Collision, get_collision_aabb

class Poly(PhysicsObject):
    '''Define um polígono arbitrário de N lados.'''

    def __init__(self, vertices, pos_cm=None, **kwds):
        if pos_cm is not None:
            raise TypeError('cannot define pos_cm for polygonal shapes')

        self.vertices = [Vector2D(*pt) for pt in vertices]
        self.pos_cm = center_of_mass(self.vertices)
        self.xmin = min(pt.x for pt in self.vertices)
        self.xmax = max(pt.x for pt in self.vertices)
        self.ymin = min(pt.y for pt in self.vertices)
        self.ymax = max(pt.y for pt in self.vertices)
        self.num_sides = len(self.vertices)
        self._normals_idxs = self.get_li_indexes()
        self.num_normals = len(self._normals_idxs or self.vertices)

        # Aceleramos um pouco o cálculo para o caso onde todas as normais são LI.
        # Isto é sinalizado por self._normals_idx = None, que implica que todas
        # as normais do polígono devem ser calculadas.
        if self.num_normals == self.num_sides:
            self._normals_idxs = None

        super(Poly, self).__init__(**kwds)

    #===========================================================================
    # Construtores alternativos
    #===========================================================================
    @classmethod
    def regular(cls, N, length, pos_cm=(0, 0), **kwds):
        '''Cria um polígono regoular com N lados de tamanho "length".'''

        alpha = pi / N
        theta = 2 * alpha
        b = length / (2 * sin(alpha))
        P0 = Vector2D(b, 0)
        points = [ (P0.rotated(n * theta) + pos_cm) for n in range(N) ]

        return Poly(points, **kwds)

    @classmethod
    def rect(cls, bbox=None, shape=None, pos_cm=None, **kwds):
        '''Cria um retângulo especificando ou a caixa de contorno ou a posição 
        do centro de massa e a forma.'''

        if bbox:
            xmin, xmax, ymin, ymax = bbox
            if pos_cm is not None:
                raise TypeError('cannot set bbox and pos_cm simultaneously')
            points = [ (xmax, ymin), (xmax, ymax), (xmin, ymax), (xmin, ymin) ]

            return Poly(points, **kwds)

        elif shape:
            x, y = pos_cm or (0, 0)
            dx, dy = shape
            xmin, xmax = x - dx / 2., x + dx / 2.
            ymin, ymax = y - dy / 2., y + dy / 2.
            bbox = (xmin, xmax, ymin, ymax)

            return Poly.rect(bbox=bbox, **kwds)

        else:
            raise TypeError('either shape or bbox must be defined')

    @classmethod
    def triangle(cls, sides, pos_cm=(0, 0), **kwds):
        '''Cria um triângulo especificando o tamanho dos lados'''
        pass

    @classmethod
    def blob(cls, N, scale, pos_cm=(0, 0), **kwds):
        '''Cria um polígono convexo aleatório especificando o número de lados e 
        um fator de escala.'''
        pass

    #===========================================================================
    # Métodos específicos da classe polígono
    #===========================================================================
    def get_li_indexes(self):
        '''Retorna os índices referents às normais linearmente independentes 
        entre si.
        
        Este método é invocado apenas na inicialização do objeto e pode involver
        testes de independencia linear relativamente caros.'''

        normals = [ self.get_normal(i).normalized() for i in range(self.num_sides) ]
        LI = []
        LI_idx = []
        for idx, n in enumerate(normals):
            for n_other in LI:
                # Produto vetorial nulo ==> dependência linear
                if abs(cross(n, n_other)) < 1e-3:
                    break
            else:
                # Executado se o loop "for" não terminar em um break
                # Implica em independência linear
                LI.append(n)
                LI_idx.append(idx)
        return LI_idx

    def get_side(self, i):
        '''Retorna um vetor na direção do i-ésimo lado do polígno. Cada segmento 
        é definido pela diferença entre o (i+1)-ésimo ponto e o i-ésimo ponto.'''

        points = self.vertices
        return points[(i + 1) % self.num_sides] - points[i]

    def get_normal(self, i):
        '''Retorna a normal unitária associada ao i-ésimo segmento. Cada segmento 
        é definido pela diferença entre o (i+1)-ésimo ponto e o i-ésimo ponto.'''

        points = self.vertices
        x, y = points[(i + 1) % self.num_sides] - points[i]
        return Vector2D(y, -x).normalized()

    def get_normals(self):
        '''Retorna uma lista com as normais linearmente independentes.'''

        if self._normals_idxs is None:
            N = self.num_sides
            points = self.vertices
            segmentos = (points[(i + 1) % N] - points[i] for i in range(N))
            return [ Vector2D(y, -x).normalized() for (x, y) in segmentos ]
        else:
            return [ self.get_normal(i) for i in self._normals_idxs ]

    def is_internal_point(self, pt):
        '''Retorna True se um ponto for interno ao polígono.'''

        n = self.get_normal
        P = self.vertices
        return all(dot(pt - P[i], n(i)) <= 0 for i in range(self.num_sides))

    #===========================================================================
    # Sobrescrita de PhysicsObject
    #===========================================================================
    def draw(self, screen):
        screen.draw_poly(self.vertices, color=self.color)

    def move(self, delta):
        super(Poly, self).move(delta)
        self.vertices = [pt + delta for pt in self.vertices]

    def rotate(self, theta):
        super(Poly, self).rotate(theta)
        self.vertices = [pt.rotated(theta, self.pos_cm) for pt in self.vertices]
        self.xmin = min(pt.x for pt in self.vertices)
        self.xmax = max(pt.x for pt in self.vertices)
        self.ymin = min(pt.y for pt in self.vertices)
        self.ymax = max(pt.y for pt in self.vertices)

    @property
    def area(self):
        return area(self.vertices)

    @property
    def inertia(self):
        try:
            return self._inertia
        except AttributeError:
            self._inertia = inertia(self.vertices, self.mass)
            return self._inertia

    @inertia.setter
    def inertia(self, value):
        self._inertia = value

    def scale(self, scale, update_physics=False):
        # Atualiza a AABB
        super(Poly, self).scale(scale, update_physics=False)

        # Atualiza os pontos
        Rcm = self.pos_cm
        self.vertices = [ scale * (pt - Rcm) + Rcm for pt in self.vertices ]

#===============================================================================
# Implementa colisões
#===============================================================================
u_x = Vector2D(1, 0)
DEFAULT_DIRECTIONS = [u_x.rotated(n * pi / 12) for n in [0, 1, 2, 3, 4, 5, 7, 8, 9, 10, 11]]

@get_collision.dispatch(Poly, Poly)
def get_collision_poly(A, B, directions=None):
    '''Implementa a colisão entre dois polígonos arbitrários'''

    # Cria a lista de direções a partir das normais do polígono
    if directions is None:
        if A.num_normals + B.num_normals < 9:
            directions = A.get_normals() + B.get_normals()
        else:
            directions = DEFAULT_DIRECTIONS

    # Testa se há superposição de sombras em todas as direções consideradas
    shadows = []
    for u in directions:
        A_coords = [ round(dot(pt, u), 6) for pt in A.vertices ]
        B_coords = [ round(dot(pt, u), 6) for pt in B.vertices ]
        Amax, Amin = max(A_coords), min(A_coords)
        Bmax, Bmin = max(B_coords), min(B_coords)
        minmax, maxmin = min(Amax, Bmax), max(Amin, Bmin)
        shadow = minmax - maxmin
        if shadow < 0 :
            return None
        else:
            shadows.append((shadow, (A_coords, B_coords), (Amax, Amin, Bmax, Bmin)))

    # Reconhece a direção de menor superposição
    min_shadow = min(shadows)
    idx = shadows.index(min_shadow)
    min_shadow, coords, maxmins = min_shadow
    norm = directions[idx]

    # Determina o sinal da normal
    A_coords_cm = dot(A.pos_cm, norm)
    B_coords_cm = dot(B.pos_cm, norm)
    norm_sign = 1
    if A_coords_cm > B_coords_cm:
        norm = -norm
        norm_sign = -1

    # Determina o ponto de colisão
#     for ptA in A.vertices + A.middle_points():
#         if B.is_internal_point(ptA):
#             return Collision(A, B, ptA, norm, delta=min_shadow)
#     for ptB in B.vertices + B.middle_points():
#         if B.is_internal_point(ptB):
#             return Collision(A, B, ptB, norm, delta=min_shadow)

    # Determina se a face está num ponto de A ou de B
    Acoords, Bcoords = coords
    Amax, Amin, Bmax, Bmin = maxmins
    if len(set(Acoords)) == len(Acoords):
        return get_collision(B, A, directions)

    shadow_middle = norm_sign * (Amax + Bmin) / 2
    pass

    A.pause()
    B.pause()

# @get_collision.dispatch(Poly, AABB)
def get_collision_p_a(A, B):
    col = get_collision_aabb(A, B)
    if col: print(col)
    return col

@get_collision.dispatch(Poly, AABB)
def get_collision_poly_aabb(A, B):
    '''Implementa a colisão entre um polígono arbitrário e uma caixa AABB'''

    B_poly = Poly.rect(bbox=B.bbox, is_dynamic_angular=False, is_dynamic_linear=B.is_dynamic_linear)
    col = get_collision_poly(A, B_poly)
    if col is not None:
        assert col.objects[0] is A
        col.objects = (A, B)
        return col

if __name__ == '__main__':
    R = Poly.rect(shape=(100, 100))
    print(R.vertices)
    print([ R.get_normal(i) for i in range(4)])
    print([R.get_side(i) for i in range(4)])
    print([R.get_normal(i) for i in range(4)])
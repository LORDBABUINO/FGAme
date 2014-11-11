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
            segmentos = (pt[(i + 1) % N] - pt[i] for i in range(N))
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

#===============================================================================
# Implementa colisões
#===============================================================================
u_x = Vector2D(1, 0)
DEFAULT_DIRECTIONS = [u_x.rotated(n * pi / 12) for n in [1, 2, 3, 4, 5, 7, 8, 9, 10, 11]]

@get_collision.dispatch(Poly, Poly)
def get_collision_poly(A, B, directions=None):
    '''Implementa a colisão entre dois polígonos arbitrários'''

    if directions is None:
        # Cria a lista de direções a partir das normais do polígono
        if len(A.vertices) + len(B.vertices) < 9:
            directions = []
            for obj in [A, B]:
                points = obj.vertices
                size = len(points)
                for i in range(size):
                    R_next = points[(i + 1) % size]
                    R_prev = points[i]
                    x, y = R_next - R_prev
                    directions.append(Vector2D(-y, x).normalized())
        else:
            directions = DEFAULT_DIRECTIONS

    # Testa se há superposição de sombras em todas as direções consideradas
    shadows = []
    shadow_centers = []
    for u in directions:
        A_coords = [ dot(pt, u) for pt in A.vertices ]
        B_coords = [ dot(pt, u) for pt in B.vertices ]
        Amax, Amin = max(A_coords), min(A_coords)
        Bmax, Bmin = max(B_coords), min(B_coords)
        minmax, maxmin = min(Amax, Bmax), max(Amin, Bmin)
        shadow = minmax - maxmin
        if shadow < 0 :
            return None
        else:
            shadows.append(shadow)
            shadow_centers.append((minmax + maxmin) / 2)

    # TRABALHO DE FÌSICA PARA JOGOS
    #
    # Implemente o resto desta função. Leia os comentários para saber o que
    # falta ser implementado.
    #
    # O objetivo do trabalho é utilizar o método das sombras (ou teorema de
    # eixos de separação) para resolver a colisão entre dois polígonos. O código
    # acima já detecta esta colisão corretamente pelo critério de que a
    # superposição da sombra dos objetos A e B é positiva em todas as direções
    # consideradas.
    #
    # Precisamos agora determinar o ponto de colisão e a direção da normal para
    # que seja possível dar a resposta física adequada. Este problema é análogo
    # à resposta de colisões das caixas AABB, mas com a dificuldade que a
    # direção normal de colisão agora não é mais alinhada aos eixos.
    #
    # Para facilitar a implementação, dividimos a discussão em 3 etapas, das
    # quais é necessário implementar 2.
    #
    #
    # Etapa 1: Reconhece a direção de menor superposição (implementado)
    # -----------------------------------------------------------------
    #
    # Encontramos o tamanho da menor superposição de sombras e qual é a direção
    # associada a ela. Estes valores são salvos nas variáveis min_shadow e norm.
    #
    # Opcionalmente, podemos alterar o loop anterior para já calcular a menor
    # sombra, seu centro e a direção normal enquanto testa a presenção de
    # colisões.
    #
    min_shadow = min(shadows)
    idx = shadows.index(min_shadow)
    norm = directions[idx]
    shadow_center = shadow_centers[idx]

    # Etapa 2: Determina o sinal da normal
    # ------------------------------------
    #
    # A normal encontrada anteriormente pode ser a correta ou apontar para a
    # direção oposta. Aqui garantimos que a convenção que a normal é externa a
    # A e interna a B deva ser respeitada. (Dica, podemos determinar esta
    # propriedade analisando a projeção dos centros de massa na linha da normal)
    #
    # ... a implementar

    A_coords_cm = dot(A.pos_cm, norm)
    B_coords_cm = dot(B.pos_cm, norm)

    if A_coords_cm > B_coords_cm:
        norm = -norm

    # Etapa 3: Determina o ponto de colisão
    # -------------------------------------
    #
    # Precisamos encontrar o ponto onde ocorre a colisão e salvar na variável pt.
    # Para isso é necessário analisar novamente a sombra de todos os pontos de
    # A e B para encontrar aquele mais próximo de uma reta ortogonal à direção
    # da normal e que passe pelo centro da sombra de superposição.
    #
    # ... a implementar

    A_coords = [ dot(pt, norm) for pt in A.vertices ]
    B_coords = [ dot(pt, norm) for pt in B.vertices ]
    Amax, Amin = max(A_coords), min(A_coords)
    Bmax, Bmin = max(B_coords), min(B_coords)
    minmax, maxmin = min(Amax, Bmax), max(Amin, Bmin)

    # norm_orto = norm.rotated(90);
	# print shadow_center
    # print A_coords
    # print B_coords

    mais_proximo = 9999;
    isA = 0;

    for i in A_coords:
        if abs(shadow_center - i) < mais_proximo:
            idx = A_coords.index(i)
            mais_proximo = shadow_center - i
            isA = 1

    for i in B_coords:
        if abs(shadow_center - i) < mais_proximo:
            idx = B_coords.index(i)
            mais_proximo = shadow_center - i
            isA = 0;

    # print idx,isA,mais_proximo

    if isA:
        pt = A.vertices[idx]
    else:
		pt = B.vertices[idx]

    # print pt

    # Retorna o objeto de colisão adequado
    return Collision(A, B, pt, norm, delta=min_shadow)


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

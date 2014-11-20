#-*- coding: utf8 -*-
from math import sqrt, sin, cos, pi

class Vector(object):
    __slots__ = ['_x', '_y']

    def __init__(self, x, y):
        '''Inicia um vetor de qualquer número de componentes a partir das suas
        componentes reais:
        
        Exemplo
        -------
        
        Criamos um vetor chamando a classe com as componentes como argumento.
        
        >>> v = Vector(3, 4); print(v)
        Vector(3, 4)

        Os métodos de listas funcionam para objetos do tipo Vector:
        
        >>> v[0], v[1], len(v)
        (3.0, 4.0, 2)
        
        Objetos do tipo Vector também aceitam operações matemáticas
        
        >>> v + 2 * v
        Vector(9, 12)
        
        Além de algumas funções de conveniência para calcular o módulo, 
        vetor unitário, etc.
        
        >>> v.norm()
        5.0
        
        >>> v.normalized()
        Vector(0.6, 0.8)
        '''

        try:
            self._x = float(x)
            self._y = float(y)
        except TypeError:
            raise TypeError('invalid arguments: x=%r, y=%r' % (x, y))

    def as_tuple(self):
        '''Retorna a representação do vetor como uma tupla'''
        return (self._x, self._y)

    def __len__(self):
        return 2

    def __repr__(self):
        '''x.__repr__() <==> repr(x)'''

        x, y = self
        x = str(x) if x != int(x) else str(int(x))
        y = str(y) if y != int(y) else str(int(y))
        return 'Vector(%s, %s)' % (x, y)

    def __str__(self):
        '''x.__str__() <==> str(x)'''
        return repr(self)

    def __iter__(self):
        yield self._x
        yield self._y

    def __getitem__(self, i):
        '''x.__getitem__(i) <==> x[i]'''
        if i == 0:
            return self._x
        elif i == 1:
            return self._y
        else:
            raise IndexError(i)

    def __mul__(self, other):
        '''x.__mul__(y) <==> x * y'''
        return type(self)(self._x * other, self._y * other)

    def __rmul__(self, other):
        '''x.__rmul__(y) <==> y * x'''
        return self * other

    def __div__(self, other):
        '''x.__div__(y) <==> x / y'''
        return type(self)(self._x / other, self._y / other)

    __truediv__ = __div__  # Python 3

    def __add__(self, other):
        '''x.__add__(y) <==> x + y'''
        x, y = other
        return type(self)(self._x + x, self._y + y)

    def __radd__(self, other):
        '''x.__radd__(y) <==> y + x'''
        return self +other

    def __sub__(self, other):
        '''x.__sub__(y) <==> x - y'''
        x, y = other
        return type(self)(self._x - x, self._y - y)

    def __rsub__(self, other):
        '''x.__rsub__(y) <==> y - x'''
        x, y = other
        return type(self)(x - self._x, y - self._y)

    def __neg__(self):
        '''x.__neg() <==> -x'''
        return type(self)(-self._x, -self._y)

    def __nonzero__(self):
        return True

    def norm(self):
        '''Retorna o módulo (norma) do vetor'''

        return sqrt(self._x ** 2 + self._y ** 2)

    def norm_sqr(self):
        '''Retorna o módulo do vetor ao quadrado'''

        return self._x ** 2 + self._y ** 2

    def normalized(self):
        '''Retorna um vetor unitário'''

        norm = self.norm()
        return self / norm if norm else Vector(*self)

    def rotated(self, theta, axis=(0, 0)):
        '''Retorna um vetor rotacionado por um ângulo theta'''

        x, y = self -axis
        cos_t, sin_t = cos(theta), sin(theta)
        return type(self)(x * cos_t - y * sin_t, x * sin_t + y * cos_t) + axis

    @property
    def x(self): return self._x

    @property
    def y(self): return self._y

class VectorM(Vector):
    '''Como Vector, mas com elementos mutáveis'''

    def __iadd__(self, other):
        '''x.__iadd__(y) <==> x += y'''

        self._x += other[0]
        self._y += other[1]
        return self

    def __isub__(self, other):
        '''x.__isub__(y) <==> x -= y'''

        self._x -= other[0]
        self._y -= other[1]
        return self

    def __imul__(self, other):
        '''x.__imul__(y) <==> x *= y'''

        self._x *= other
        self._y *= other
        return self

    def __idiv__(self, other):
        '''x.__idiv__(y) <==> x /= y'''

        self._x /= other
        self._y /= other
        return self

    __itruediv__ = __idiv__

    def rotate(self, theta, axis=(0, 0)):
        '''Realiza rotação *inplace*'''

        x, y = self -axis
        cos_t, sin_t = cos(theta), sin(theta)
        self._x = x * cos_t - y * sin_t + axis[0]
        self._y = x * sin_t + y * cos_t + axis[1]

    def copy_from(self, other):
        '''Copia as coordenadas x, y do objeto other'''

        try:
            self._x = other._x
            self._y = other._y
        except AttributeError:
            self._x = other[0]
            self._y = other[1]

    def copy(self):
        '''Retorna uma cópia de si mesmo'''

        return VectorM(self._x, self._y)

    x = property(Vector.x.fget)
    y = property(Vector.y.fget)

    @x.setter
    def x(self, value): self._x = float(value)

    @y.setter
    def y(self, value): self._y = float(value)

def asvector(v):
    if isinstance(v, Vector):
        return v
    else:
        return Vector(*v)

#===============================================================================
# Funções com vetores
#===============================================================================
def dot(v1, v2):
    '''Calcula o produto escalar entre dois vetores'''

    return sum(x * y for (x, y) in zip(v1.as_tuple(), v2.as_tuple()))

def cross(v1, v2):
    '''Retorna a compontente z do produto vetorial de dois vetores bidimensionais'''

    x1, y1 = v1
    x2, y2 = v2
    return x1 * y2 - x2 * y1

def as2d(v):
    '''Retorna o vetor ou tupla como um objeto do tipo Vector. 
    
    Caso a compontente z não seja nula, produz um erro ValueError.'''

    if isinstance(v, Vector):
        return v
    elif isintance(v, (tuple, list)):
        if len(v) == 2:
            return Vector(v[0], v[1])
        elif len(v) == 3:
            if v.z != 0:
                raise ValueError('z component is not null')
            return Vector(v[0], v[1])
        else:
            raise ValueError('sequence of invalid size: %s' % len(v))
    raise TypeError('invalid type: %s' % type(v).__name__)

def sign(x):
    '''Retorna -1 para um numero negativo e 1 para um número positivo'''

    if x > 0:
        return 1
    elif x < 0:
        return -1
    else:
        return 0

#===============================================================================
# Área, centro de massa, etc
#===============================================================================
def _w_list(L):
    '''Calcula os termos W0 = 1/2 * (y1*x0 - y0*x1) de todos os pontos da lista'''

    N = len(L)
    out = []
    for i in range(N):
        x1, y1 = L[(i + 1) % N]
        x0, y0 = L[i]
        out.append(0.5 * (y1 * x0 - y0 * x1))
    return out

def area(L):
    '''Calcula a área do polígono definido por uma lista de pontos.
    
    A lista de pontos deve rodar no sentido anti-horário. Caso contrário, o 
    resultado da área será negativo.
    
    >>> pontos = [(0, 0), (1, 0), (1, 1), (0, 1)]
    >>> area(pontos)
    1.0
    '''

    return sum(_w_list(L))

def center_of_mass(L):
    '''Calcula o vetor centro de massa de um polígono definido por uma lista de 
    pontos.
    
    >>> pontos = [(0, 0), (1, 0), (1, 1), (0, 1)]
    >>> center_of_mass(pontos)
    Vector(0.5, 0.5)
    '''

    W = _w_list(L)
    A = sum(W)
    N = len(L)
    x_cm = 0
    y_cm = 0
    for i in range(N):
        x1, y1 = L[(i + 1) % N]
        x0, y0 = L[i]
        wi = W[i]
        x_cm += (x1 + x0) * wi / 3.0
        y_cm += (y1 + y0) * wi / 3.0
    x_cm /= A
    y_cm /= A
    return Vector(x_cm, y_cm)

def ROG_sqr(L, axis=None):
    '''Calcula o quadrado do raio de giração. O raio de giração é uma grandeza
    geométrica definida como o momento de inércia de um objeto com densidade 
    igual a 1.
    
    >>> pontos = [(0, 0), (2, 0), (2, 2), (0, 2)]
    
    Se o eixo axis não for determinado, assume o centro de massa (no caso de
    um quadrado, o raio de giração ao quadrado é igual a L**2/6)
    
    >>> ROG_sqr(pontos)                             # doctest: +ELLIPSIS
    0.666...
    
    Outro eixo pode ser determinado. Por exemplo, em torno da origem temos 
    I=2*M*L**2/3
    
    >>> ROG_sqr(pontos, axis=(0, 0))                # doctest: +ELLIPSIS
    2.666...
    '''

    W = _w_list(L)
    A = sum(W)
    N = len(L)
    ROG2_orig = 0
    for i in range(N):
        x1, y1 = L[(i + 1) % N]
        x0, y0 = L[i]
        ROG2_orig += ((x1 + x0) ** 2 - x1 * x0 + (y1 + y0) ** 2 - y1 * y0) * W[i] / 6
    ROG2_orig /= A

    # Usa o teorema dos eixos paralelos para determinar o momento em torno
    # do centro de massa
    cm = center_of_mass(L)
    ROG2_cm = ROG2_orig - (cm.x ** 2 + cm.y ** 2)
    if axis is None:
        return ROG2_cm
    else:
        # Usa o teorema dos eixos paralelos novamente para deslocar para o outro
        # eixo
        D = (cm - axis)
        return ROG2_cm + (D.x ** 2 + D.y ** 2)

def clip(poly1, poly2):
    '''Sutherland-Hodgman polygon clipping'''

    def inside(pt):
        '''Retorna verdadeiro se o ponto estiver dentro do polígono 2'''
        pt_rel = pt - r0
        return T.x * pt_rel.y >= T.y * pt_rel.x

    def intercept_point():
        '''Retorna o ponto de intercepção entre os segmentos formados por 
        r1-r0 e v1-v0'''

        A = r0.x * r1.y - r0.y * r1.x
        B = v0.x * v1.y - v0.y * v1.x
        C = 1.0 / (T.x * T_.y - T.y * T_.x)
        return Vector((-A * T_.x + B * T.x) * C, (-A * T_.y + B * T.y) * C)

    out = poly1[:]
    r0 = poly2[-1]

    # Itera sobre todas as linhas definidas pelos lados do polígono 2
    for r1 in poly2:
        if not out:
            raise ValueError('no superposition detected')

        T = r1 - r0
        points, out = out, []
        v0 = points[-1]
        v0_inside = inside(v0)

        # Em cada linha, itera sobre todos os pontos do polígono de saída
        # (inicialmente, o polígono 1)
        for v1 in points:
            T_ = v1 - v0

            # Um vértice dentro e outro fora ==> cria ponto intermediário
            # Dois vértices dentro ==> copia para a lista de saída
            # Dois vértices fora ==> abandona o ponto anterior
            v1_inside = inside(v1)
            if (v1_inside + v0_inside) == 1:
                out.append(intercept_point())
            if v1_inside:
                out.append(v1)

            # Atualiza ponto anterior
            v0 = v1
            v0_inside = v1_inside

        # Atualiza ponto inicial da face
        r0 = r1
    return(out)


def convex_hull(points):
    '''Retorna a envoltória convexa do conjunto de pontos fornecidos.
    
    Implementa o algorítimo da cadeia monótona de Andrew, O(n log n)
    
    Exemplo
    -------
    
    >>> convex_hull([(0, 0), (1, 1), (1, 0), (0, 1), (0.5, 0.5)])
    [Vector(0, 0), Vector(1, 0), Vector(1, 1), Vector(0, 1)]
    '''

    # Ordena os pontos pela coordenada x, depois pela coordenada y
    points = sorted(set(map(tuple, points)))
    points = [ Vector(*pt) for pt in points ]
    if len(points) <= 1:
        return points

    # Cria a lista L: lista com os vértices da parte inferior da envoltória
    #
    # Algoritimo: acrescenta os pontos de points em L e a cada novo ponto
    # remove o último caso não faça uma volta na direção anti-horária
    L = []
    for p in points:
        while len(L) >= 2 and cross(L[-1] - L[-2], p - L[-2]) <= 0:
            L.pop()
        L.append(p)

    # Cria a lista U: vértices da parte superior
    # Semelhante à anterior, mas itera sobre os pontos na ordem inversa
    U = []
    for p in reversed(points):
        while len(U) >= 2 and cross(U[-1] - U[-2], p - U[-2]) <= 0:
            U.pop()
        U.append(p)

    # Remove o último ponto de cada lista, pois ele se repete na outra
    return L[:-1] + U[:-1]

if __name__ == '__main__':
    import doctest
    doctest.testmod()

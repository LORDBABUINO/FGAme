# -*- coding: utf8 -*-
from math import sqrt, sin, cos, pi

class Vector2D(object):
    __slots__ = ['x', 'y']

    def __init__(self, x, y):
        '''Inicia um vetor de qualquer número de componentes a partir das suas
        componentes reais:
        
        Exemplo
        -------
        
        Criamos um vetor chamando a classe com as componentes como argumento.
        
        >>> v = Vector2D(3, 4); print(v)
        Vector2D(3.0, 4.0)

        Os métodos de listas funcionam para objetos do tipo Vector:
        
        >>> v[0], v[1], len(v)
        (3.0, 4.0, 2)
        
        Objetos do tipo Vector também aceitam operações matemáticas
        
        >>> v + 2 * v
        Vector2D(9.0, 12.0)
        
        Além de algumas funções de conveniência para calcular o módulo, 
        vetor unitário, etc.
        
        >>> v.norm()
        5.0
        
        >>> v.normalized()
        Vector2D(0.6, 0.8)
        '''

        self.x = float(x)
        self.y = float(y)

    def as_tuple(self):
        '''Retorna a representação do vetor como uma tupla'''
        return (self.x, self.y)

    def __len__(self):
        return 2

    def __repr__(self):
        '''x.__repr__() <==> repr(x)'''
        return 'Vector2D%s' % str(self.as_tuple())

    def __str__(self):
        '''x.__str__() <==> str(x)'''
        return repr(self)

    def __iter__(self):
        yield self.x
        yield self.y

    def __getitem__(self, i):
        '''x.__getitem__(i) <==> x[i]'''
        if i == 0:
            return self.x
        elif i == 1:
            return self.y
        else:
            raise IndexError(i)

    def __mul__(self, other):
        '''x.__mul__(y) <==> x * y'''
        return Vector2D(self.x * other, self.y * other)

    def __rmul__(self, other):
        '''x.__rmul__(y) <==> y * x'''
        return self * other

    def __div__(self, other):
        '''x.__div__(y) <==> x / y'''
        return Vector2D(self.x / other, self.y / other)

    def __add__(self, other):
        '''x.__add__(y) <==> x + y'''
        x, y = other
        return Vector2D(self.x + x, self.y + y)

    def __radd__(self, other):
        '''x.__radd__(y) <==> y + x'''
        return self +other

    def __sub__(self, other):
        '''x.__sub__(y) <==> x - y'''
        x, y = other
        return Vector2D(self.x - x, self.y - y)

    def __rsub__(self, other):
        '''x.__rsub__(y) <==> y - x'''
        x, y = other
        return Vector2D(x - self.x, y - self.y)

    def __neg__(self):
        '''x.__neg() <==> -x'''
        return Vector2D(-self.x, -self.y)

    def __nonzero__(self):
        return True

    def norm(self):
        '''Calcula o módulo (norma) do vetor'''

        return sqrt(self.x ** 2 + self.y ** 2)

    def normalized(self):
        '''Retorna um vetor unitário'''

        norm = self.norm()
        return self / norm if norm else Vector2D(*self)

    def rotated(self, theta, axis=(0, 0)):
        '''Retorna um vetor rotacionado por um ângulo theta'''

        x, y = self -axis
        cos_t, sin_t = cos(theta), sin(theta)
        return Vector2D(x * cos_t - y * sin_t, x * sin_t + y * cos_t) + axis

################################################################################
#                          Funções com vetores
################################################################################
def dot(v1, v2):
    '''Calcula o produto escalar entre dois vetores'''

    return sum(x * y for (x, y) in zip(v1.as_tuple(), v2.as_tuple()))

def cross(v1, v2):
    '''Retorna a compontente z do produto vetorial de dois vetores bidimensionais'''

    x1, y1 = v1
    x2, y2 = v2
    return x1 * y2 - x2 * y1

def as2d(v):
    '''Retorna o vetor ou tupla como um objeto do tipo Vector2D. 
    
    Caso a compontente z não seja nula, produz um erro ValueError.'''

    if isinstance(v, Vector2D):
        return v
    elif isintance(v, (tuple, list)):
        if len(v) == 2:
            return Vector2D(v[0], v[1])
        elif len(v) == 3:
            if v.z != 0:
                raise ValueError('z component is not null')
            return Vector2D(v[0], v[1])
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

################################################################################
#                        Área, centro de massa, etc
################################################################################
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
    Vector2D(0.5, 0.5)
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
    return Vector2D(x_cm, y_cm)

def inertia(L, mass, axis=None):
    '''Calcula o momento de inércia de um polígono polígono definido por uma 
    lista de pontos e com determinada mass.
    
    >>> pontos = [(0, 0), (1, 0), (1, 1), (0, 1)]
    
    Se o eixo axis não for determinado, assume o centro de massa (no caso de
    um quadrado, o momento de inércia é igual a M*L**2/6)
    
    >>> inertia(pontos, mass=1)                             # doctest: +ELLIPSIS
    0.1666...
    
    Outro eixo pode ser determinado, por exemplo, em torno da origem temos 
    I=2*M*L**2/3
    
    >>> inertia(pontos, mass=1, axis=(0, 0))                # doctest: +ELLIPSIS
    0.666...
    '''

    W = _w_list(L)
    A = sum(W)
    N = len(L)
    I_orig = 0
    for i in range(N):
        x1, y1 = L[(i + 1) % N]
        x0, y0 = L[i]
        I_orig += ((x1 + x0) ** 2 - x1 * x0 + (y1 + y0) ** 2 - y1 * y0) * W[i] / 6
    I_orig *= mass / A

    # Usa o teorema dos eixos paralelos para determinar o momento em torno
    # do centro de massa
    cm = center_of_mass(L)
    D2 = cm.x ** 2 + cm.y ** 2
    I_cm = I_orig - mass * D2
    if axis is None:
        return I_cm
    else:
        # Usa o teorema dos eixos paralelos novamente para deslocar para o outro
        # eixo
        D = (cm - axis)
        return I_cm + mass * (D.x ** 2 + D.y ** 2)

if __name__ == '__main__':
    import doctest
    doctest.testmod()

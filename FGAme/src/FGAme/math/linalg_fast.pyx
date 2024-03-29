#-*- coding: utf8 -*-
from math import pi
cdef extern from "math.h":
    double log(double)
    double sqrt(double)
    double cos(double)
    double sin(double)
    
cdef double PI = pi
cdef double SQRT_2 = sqrt(2)

__all__ = ['Vector', 'VectorM', 'asvector', 'Matrix', 'MatrixM', 'MatrixR', 'dot', 'cross']

#===============================================================================
# Vetores
#===============================================================================
cdef class Vector(object):
    cdef double _x, _y

    def __cinit__(Vector self, x, y):
        '''Representa um vetor bidimensional.
        
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

        self._x = x
        self._y = y

    def __init__(self, x, y):
        pass

    def as_tuple(self):
        '''Retorna a representação do vetor como uma tupla'''
        return (self._x, self._y)

    cpdef double norm(self):
        '''Retorna o módulo (norma) do vetor'''

        return sqrt(self._x * self._x + self._y * self._y)

    cpdef double norm_sqr(self):
        '''Retorna o módulo do vetor ao quadrado'''

        return self._x * self._x + self._y *self._y

    cpdef Vector normalized(self):
        '''Retorna um vetor unitário'''

        cdef double norm = self.norm()
        if norm != 0:
            return Vector(self._x/norm, self._y/norm)
        else:
            return Vector(0, 0)

    cpdef Vector rotated(Vector self, theta, axis=None):
        '''Retorna um vetor rotacionado por um ângulo theta'''

        cdef double t = float(theta)
        cdef double x, y, cos_t = cos(t), sin_t = sin(t)
    
        if axis is None:
            x = self._x
            y = self._y
            return self._new(x * cos_t - y * sin_t, x * sin_t + y * cos_t)
        else:
            x, y = self - axis
            return self._new(x * cos_t - y * sin_t, x * sin_t + y * cos_t) + axis

    # Métodos mágicos ----------------------------------------------------------
    def __len__(self):
        return 2

    def __repr__(Vector self):
        '''x.__repr__() <==> repr(x)'''

        x, y = self
        x = str(x) if x != int(x) else str(int(x))
        y = str(y) if y != int(y) else str(int(y))
        tname = type(self).__name__
        return '%s(%s, %s)' % (tname, x, y)

    def __str__(Vector self):
        '''x.__str__() <==> str(x)'''
        return repr(self)

    def __iter__(Vector self):
        yield self._x
        yield self._y

    def __getitem__(Vector self, i):
        '''x.__getitem__(i) <==> x[i]'''
        if i == 0:
            return self._x
        elif i == 1:
            return self._y
        else:
            raise IndexError(i)

    def __mul__(self, other):
        '''x.__mul__(y) <==> x * y'''
        
        cdef Vector vector
        cdef double scalar
        
        if isinstance(self, Vector):
            vector = self
            scalar = float(other)
        else:
            vector = other
            scalar = float(self)
            
        return vector._new(vector._x * scalar, vector._y * scalar)


    def __div__(Vector self, other):
        '''x.__div__(y) <==> x / y'''
        
        return self._new(self._x / other, self._y / other)

    __truediv__ = __div__  # Python 3

    def __add__(self, other):
        '''x.__add__(y) <==> x + y'''
        
        cdef double X=0, Y=0
        cdef Vector aux
        new = None
        
        # Processa o primeiro argumento
        if isinstance(self, Vector):
            aux = self
            X += aux._x
            Y += aux._y
            new = self._new
        else:
            x, y = self
            X += x
            Y += y
            
        # Processa o segundo argumento
        if isinstance(other, Vector):
            aux = other
            X += aux._x
            Y += aux._y
            if new is None:
                new = other._new
        else:
            x, y = other
            X += x
            Y += y
            
        return new(X, Y)

    def __sub__(self, other):
        '''x.__sub__(y) <==> x - y'''
        
        
        cdef double X=0, Y=0
        cdef Vector aux
        new = None
        
        # Processa o primeiro argumento
        if isinstance(self, Vector):
            aux = self
            X += aux._x
            Y += aux._y
            new = self._new
        else:
            x, y = self
            X += x
            Y += y
            
        # Processa o segundo argumento
        if isinstance(other, Vector):
            aux = other
            X -= aux._x
            Y -= aux._y
            if new is None:
                new = other._new
        else:
            x, y = other
            X -= x
            Y -= y
            
        return new(X, Y)

    def __neg__(Vector self):
        '''x.__neg() <==> -x'''
        return self._new(-self._x, -self._y)

    def __nonzero__(self):
        return True
    
    def __richcmp__(Vector self, other, int method):
        x, y = other
        return self._x == x and self._y == y            
        
    cpdef Vector _new(self, double x, double y):
        return type(self)(x, y)

    property x:
        def __get__(Vector self): 
            return self._x
        
        def __set__(self, value): 
            raise AttributeError

        def __del__(self):
            raise AttributeError

    property y:
        def __get__(Vector self): 
            return self._y
        
        def __set__(self, value): 
            raise AttributeError
        
        def __del__(self):
            raise AttributeError

cdef class VectorM(Vector):
    '''Como Vector, mas com elementos mutáveis'''

    def __iadd__(Vector self, other):
        '''x.__iadd__(y) <==> x += y'''

        self._x += other[0]
        self._y += other[1]
        return self

    def __isub__(Vector self, other):
        '''x.__isub__(y) <==> x -= y'''

        self._x -= other[0]
        self._y -= other[1]
        return self

    def __imul__(Vector self, other):
        '''x.__imul__(y) <==> x *= y'''

        self._x *= other
        self._y *= other
        return self

    def __idiv__(Vector self, other):
        '''x.__idiv__(y) <==> x /= y'''

        self._x /= other
        self._y /= other
        return self

    __itruediv__ = __idiv__

    def rotate(Vector self, theta, axis=(0, 0)):
        '''Realiza rotação *inplace*'''

        x, y = self -axis
        cos_t, sin_t = cos(theta), sin(theta)
        self._x = x * cos_t - y * sin_t + axis[0]
        self._y = x * sin_t + y * cos_t + axis[1]

    def copy_from(Vector self, other):
        '''Copia as coordenadas x, y do objeto other'''

        cdef Vector vector 
        try:
            vector = other
            self._x = vector._x
            self._y = vector._y
        except AttributeError:
            self._x = other[0]
            self._y = other[1]

    def copy(self):
        '''Retorna uma cópia de si mesmo'''

        return VectorM(self._x, self._y)
    
    property x:
        def __get__(Vector self): 
            return self._x
        
        def __set__(self, value): 
            self._x = value

        def __del__(self):
            raise AttributeError
        
    property y:
        def __get__(Vector self): 
            return self._y
        
        def __set__(self, value): 
            self._y = value
        
        def __del__(self):
            raise AttributeError

def asvector(v):
    '''Retorna o objeto como uma instância da classe Vetor'''

    if isinstance(v, Vector):
        return v
    else:
        return Vector(*v)

#===============================================================================
# Matrizes
#===============================================================================
class Matrix(object):
    '''Implementa uma matriz bidimensional e operações básicas de álgebra 
    linear
    
    Example
    -------
    
    Criamos uma matriz a partir de uma lista de listas
    
    >>> M = Matrix([[1, 2],
    ...             [3, 4]])
    
    Podemos também utilizar os construtores especializados, como por exemplo
    o `Matrix.R`, que cria uma matriz de rotação
    
    >>> R = Matrix.R(pi); R 
    |-1  -0|
    | 0  -1|
    
    Os objetos da classe Matrix implementam as operações básicas de álgebra 
    linear
    
    >>> M + 2 * R
    |-1  2|
    | 3  2|
    
    As multiplicações são como definidas em ágebra linear
    
    >>> M * M
    | 7  10|
    |15  22|
    
    >>> M * Vector(2, 3)
    Vector(8, 18)
    
    Além disto, temos operações como cálculo da inversa, autovalores, 
    determinante, etc
    
    >>> M.inv() * M
    |1  0|
    |0  1|
    
    >>> Matrix.I().eigval()  # Matrix.I() --> retorna uma matriz de identidade
    (1.0, 1.0)
    '''

    def __init__(self, data):
        self._data = tuple(Vector(*row) for row in data)

    # Construtores alternativos ------------------------------------------------
    @classmethod
    def _from_lists_(cls, M):
        '''Inicia a matriz a partir de uma lista de linhas. Corresponde ao 
        método de inicialização padrão, mas pode ser invocado por subclasses
        caso a assinatura do construtor padrão seja diferente'''

        return cls(M)

    @classmethod
    def R(cls, theta):
        '''Cria uma matriz de rotação que realiza a rotação pelo ângulo theta
        especificado'''

        C = cos(theta)
        S = sin(theta)
        M = [[C, -S], [S, C]]
        return cls._from_lists_(M)

    @classmethod
    def I(cls):
        '''Retorna a matriz identidade'''
        try:
            return cls.__dict__['_I']
        except KeyError:
            cls._I = I = cls._from_lists_([[1, 0], [0, 1]])
            return I

    # API básica ---------------------------------------------------------------
    def astuple(self):
        '''Retorna a matrix como uma tupla de tuplas'''

        return tuple(tuple(row) for row in self._data)

    def flat(self):
        '''Itera sobre todos elementos da matriz, primeiro os elementos da 
        primeira linha e depois da segunda'''

        for L in self._data:
            for x in L:
                yield x

    def det(self):
        '''Retorna o determinante da matriz'''

        return self[0, 0] * self[1, 1] - self[1, 0] * self[0, 1]

    def trace(self):
        '''Retorna o traço da matriz'''

        return self[0, 0] + self[1, 1]

    def transposed(self):
        '''Retorna a transposta da matriz'''

        M = [[self[0, 0], self[1, 0]],
             [self[0, 1], self[1, 1]]]
        return self._from_lists_(M)

    def rotated(self, theta):
        '''Retorna uma matriz rotacionada por um ângulo theta'''

        R = self.R(theta)
        return R * self * R.transposed()

    def inv(self):
        '''Retorna a inversa da matriz'''

        det = self.det()
        a, b, c, d = self.flat()
        M = [[d / det, -b / det],
             [-c / det, a / det]]
        return self._from_lists_(M)

    def eig(self):
        '''Retorna uma tupla com a lista de autovalores e a matriz dos 
        autovetores
        
        Example
        -------
        
        >>> M = Matrix([[1,2], [3,4]])
        >>> vals, vecs = M.eig()
        >>> v1, v2 = vecs.colvecs()
        >>> M * v1, vals[0] * v1
        (Vector(2.23472697618, 4.88542751029), Vector(2.23472697618, 4.88542751029))
        '''
        v1, v2 = self.eigvec()
        a, c = v1
        b, d = v2
        return (self.eigval(), self._from_lists_([[a, b], [c, d]]))

    def eigval(self):
        '''Retorna uma tupla com os autovalores da matriz'''

        a, b, c, d = self.flat()
        l1 = (d + a + sqrt(d * d - 2 * a * d + a * a + 4 * c * b)) / 2
        l2 = (d + a - sqrt(d * d - 2 * a * d + a * a + 4 * c * b)) / 2
        return (l1, l2)

    def eigvec(self, transpose=False):
        '''Retorna uma lista com os autovetores normalizados da matriz.
        
        A ordem dos autovetores corresponde àquela retornada pelo método 
        `M.eigval()`'''

        a, b = self._data[0]
        l1, l2 = self.eigval()
        try:
            v1 = Vector(b / (l1 - a), 1)
        except ZeroDivisionError:
            v1 = Vector(1, 0)
        try:
            v2 = Vector(b / (l2 - a), 1)
        except ZeroDivisionError:
            v2 = Vector(1, 0)

        return v1.normalized(), v2.normalized()

    def colvecs(self):
        '''Retorna uma lista com os vetores coluna da matriz.'''

        a, b, c, d = self.flat()
        return [Vector(a, c), Vector(b, d)]

    def rowvecs(self):
        '''Retorna uma lista com os vetores linha. Este método existe por 
        simetria a `M.colvecs()`. Mesma coisa que list(M).'''

        return list(self)

    # Métodos mágicos ----------------------------------------------------------
    def __len__(self):
        return 2

    def _fmt_number(self, x):
        '''Função auxiliar para __repr__: formata número para impressão'''

        return ('%.3f' % x).rstrip('0').rstrip('.')

    def __repr__(self):
        '''x.__repr__() <==> repr(x)'''

        l1, l2 = self._data
        a, b = l1
        c, d = l2
        a, b, c, d = map(self._fmt_number, [a, b, c, d])
        n = max(len(a), len(c))
        m = max(len(b), len(d))
        l1 = '|%s  %s|' % (a.rjust(n), b.rjust(m))
        l2 = '|%s  %s|' % (c.rjust(n), d.rjust(m))
        return '%s\n%s' % (l1, l2)

    def __str__(self):
        '''x.__str__() <==> str(x)'''
        return repr(self)

    def __iter__(self):
        return iter(self._data)

    def __getitem__(self, idx):
        '''x.__getitem__(i) <==> x[i]'''

        if isinstance(idx, tuple):
            i, j = idx
            return self._data[i][j]

        elif isinstance(idx, int):
            return self._data[idx]

    def __mul__(self, other):
        '''x.__mul__(y) <==> x * y'''

        if isinstance(other, Matrix):
            u = (other[0, 0], other[1, 0])
            v = (other[0, 1], other[1, 1])
            U, V = self
            M = [[dot(U, u), dot(U, v)],
                 [dot(V, u), dot(V, v)]]
            return Matrix(M)
        elif isinstance(other, (Vector, tuple, list)):
            u, v = self
            return Vector(dot(u, other), dot(v, other))
        else:
            return self._new([other * v for v in self._data])

    def __rmul__(self, other):
        '''x.__rmul__(y) <==> y * x'''

        return self * other

    def __div__(self, other):
        '''x.__div__(y) <==> x / y'''

        u, v = self
        return self._from_lists_([u / other, v / other])

    __truediv__ = __div__  # Python 3

    def __add__(self, other):
        '''x.__add__(y) <==> x + y'''
        u, v = other
        U, V = self
        return self._from_lists_([U + u, V + v])

    def __radd__(self, other):
        '''x.__radd__(y) <==> y + x'''
        return self +other

    def __sub__(self, other):
        '''x.__sub__(y) <==> x - y'''
        x, y = other
        return self._from_lists_([self._data[0] - x, self._data[1] - y])

    def __rsub__(self, other):
        '''x.__rsub__(y) <==> y - x'''
        x, y = other
        return self._from_lists_([x - self._data[0], y - self._data[1]])

    def __neg__(self):
        '''x.__neg() <==> -x'''
        return self._from_lists_([-self._data[0], -self._data[1]])

    def __nonzero__(self):
        return True

class MatrixM(Matrix):
    '''Implementa matrizes mutáveis'''
    # TODO: implementar
    
class MatrixR(Matrix):
    '''Implementa matrizes de rotação'''
    # TODO: implementar

def asmatrix(m):
    '''Retorna o objeto como uma instância da classe Vetor'''

    if isinstance(m, Matrix):
        return m
    else:
        return Matrix(m)

#===============================================================================
# Funções com vetores
#===============================================================================
def dot(v1, v2):
    '''Calcula o produto escalar entre dois vetores'''

    cdef Vector u1, u2
    
    if isinstance(v1, Vector) and isinstance(v2, Vector):
        u1 = v1
        u2 = v2
        return u1._x * u2._x + u1._y * u2._y
    else:
        return sum(zip(v1, v2))

def cross(v1, v2):
    '''Retorna a compontente z do produto vetorial de dois vetores bidimensionais'''

    cdef Vector u1, u2
    
    if isinstance(v1, Vector) and isinstance(v2, Vector):
        u1 = v1
        u2 = v2
        return u1._x * u2._y - u2._x * u1._y
    else:
        x1, y1 = v1
        x2, y2 = v2
        return x1 * y2 - x2 * y1

if __name__ == '__main__':
    import doctest
    doctest.testmod()

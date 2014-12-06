from FGAme.mathutils import *
import math

#===============================================================================
# Gerenciamento de cores
#===============================================================================
class Color(object):
    '''Objeto básico que representa uma cor'''
    __slots__ = ['_color']
    _CACHE = {}

    def __new__(cls, color):
        try:
            return cls._CACHE[color]
        except KeyError:
            return object.__new__(cls)

    def __init__(self, value):
        if len(value) == 4:
            R, G, B, A = value
        else:
            R, G, B = value
            if isinstance(R, float):
                A = 1.0

        if isinstance(R, float):
            R = int(255, R)
            G = int(255, G)
            B = int(255, B)
            A = int(255, A)
        self._color = (R, G, B, A)

    @property
    def color_rgba(self):
        return self._color

    @property
    def color_rgb(self):
        return self.color[:2]

    @property
    def fcolor_rgb(self):
        return tuple(x / 255. for x in self._color[:2])

    @property
    def fcolor_rgba(self):
        return tuple(x / 255. for x in self._color)

    @property
    def ucolor_rgba(self):
        c = self._color
        return (c[0] << 24) + (c[1] << 16) + (c[2] << 8) + c[3]

    @property
    def ucolor_rgb(self):
        c = self._color
        return (c[0] << 16) + (c[1] << 8) + c[2]

Color._CACHE = dict(
    # Tons de cinza
    white=Color(255, 255, 255), black=Color(0, 0, 0),

    # Cores básicas
    red=Color(255, 0, 0), green=Color(0, 255, 0), blue=Color(0, 0, 255)
)

#===============================================================================
# Objetos desenháveis
#===============================================================================
class Drawable(object):
    '''Classe pai para todos os objetos que podem ser desenhados na tela'''

    def __init__(self, pos=(0, 0), theta=0, scale=1.0):
        self._pos = VectorM(*pos)
        self._theta = float(theta)
        self._scale = float(scale)
        self._cache = None

    @property
    def pos(self):
        return Vector(*self._pos)

    @property
    def theta(self):
        return self._theta

    @property
    def scale(self):
        return self._scale

    def rotate(self, theta, axis=None):
        if axis is None:
            if theta:
                self._theta += theta
                self._cache = None
        else:
            delta = self._pos - axis
            self.rotate(theta)
            self.move(delta.rotated(theta))

    def move(self, delta):
        if delta[0] or delta[1]:
            self._pos += delta
            self._cache = None

    def scale(self, scale):
        self._scale *= 1


class Geometric(Drawable):
    '''Classe pai para todos os objetos geométricos'''

    def __init__(self, pos=(0, 0), theta=0, color=None, filled=True, lw=0):
        super(Geometric, self).__init__(pos)
        if color is not None:
            self.color = Color(color)
        else:
            self.color = None
        self.filled = True
        self.lw = lw

    def as_poly(self):
        vertices = self.as_vertices(relative=True)
        return Poly(vertices, pos=self.pos, color=self.color, filled=self.filled)

    def as_vertices(self, relative=False):
        raise NotImplementedError

class Circle(Geometric):
    def __init__(self, radius, *args, **kwds):
        super(Circle, self).__init__(*args, **kwds)
        self._radius = float(radius)

    @property
    def radius(self):
        return self._scale * self._radius

    def as_poly(self, N=20):
        '''Retorna a aproximação do círculo como um polígono de N lados'''

        vertices = self.as_vertices(N, relative=True, scaled=True)
        return Poly(vertices, pos=self.pos, color=self.color, filled=self.filled)

    def as_vertices(self, N=20, relative=False, scaled=True):
        R = self._radius * (self._scale if scaled else 1)
        cos, sin = math.cos, math.sin

        if relative == False:
            delta = 2 * pi / N
            vertices = ((cos(delta * t), sin(delta * t)) for t in range(N))
            return list(vertices)
        X, Y = self._pos
        return [ (x + X, y + Y) for (x, y) in vertices ]

class Rect(Geometric):
    def __init__(self, shape, *args, **kwds):
        super(Rect, self).__init__(*args, **kwds)
        self.shape = VectorM(shape)

    def rotate(self, theta):
        raise ValueError('cannot rotate a Rect object')

    def as_poly(self, mode=4, scaled=True):
        '''Retorna o retângulo como um objeto do tipo polígono'''

        vertices = self.as_vertices(mode, relative=True)
        return Poly(vertices, pos=self.pos, color=self.color, filled=self.filled)

    def as_vertices(self, mode=4, relative=False, scaled=True):
        '''Calcula apenas os vértices do polígono
        
        Parameters
        ----------
        
        mode : int
            Modo de conversão, caso a posição seja relativa: 0-começa no canto
            inferior direito, em sentido anti-horário até 3. `mode=4` 
            corresponde ao centro.
        '''
        if scaled:
            dX, dY = self.shape * self._scale
        else:
            dX, dY = self.shape
        X, Y = self._pos

        if not relative:
            mode = 0

        if mode == 4:
            dX /= 2
            dY /= 2
            vertices = [(X - dX, Y - dY), (X + dX, Y - dY),
                        (X + dX, Y + dY), (X - dX, Y + dY)]
        elif mode == 0:
            vertices = [(X, Y), (X + dX, Y),
                        (X + dX, Y + dY), (X, Y + dY)]
        elif mode == 1:
            vertices = [(X - dX, Y), (X, Y),
                        (X, Y + dY), (X - dX, Y + dY)]
        elif mode == 2:
            vertices = [(X - dX, Y - dY), (X, Y - dY),
                        (X, Y), (X - dX, Y)]
        elif mode == 3:
            vertices = [(X, Y - dY), (X + dX, Y - dY),
                        (X + dX, Y), (X, Y)]
        else:
            raise ValueError('mode must be in range(0, 5)')

        if relative:
            return vertices
        else:
            return [ (x + X, y + Y) for (x, y) in vertices ]


class Poly(Geometric):
    def __init__(self, vertices, *args, **kwds):
        super(Rect, self).__init__(*args, **kwds)
        self.vertices = vertices

    @classmethod
    def rect(cls):
        pass

    @classmethod
    def triangle(cls):
        pass

    @classmethod
    def regular(cls):
        pass

    @classmethod
    def convex(cls):
        pass

    def clip(self, other):
        pass

    def convex_hull(self, other):
        pass

    def as_poly(self):
        return copy.deepcopy(self)

    def as_vertices(self, relative=False, scaled=True):
        vertices = self.vertices
        if scaled and self._scale != 0:
            scale = self._scale
            vertices = [ v * scale for v in vertices ]
        if relative:
            pos = self._pos
            return [ v + pos for v in vertices ]
        return vertices

class Group(Drawable):
    def __init__(self, members):
        self.members = list(members)

    def add(self, member):
        self.members.append(member)

    def rotate(self, theta, axis=None):
        super(Group, self).rotate(theta, axis)
        for member in self.members:
            member.rotate(theta, member.pos)

    def scale(self, scale):
        if scale != 1:
            super(Group, self).scale(scale)
            for member in self.members:
                member.scale(scale)
                if member.pos[0] or member.pos[1]:
                    member.move((scale - 1) * member._pos)

    def as_poly(self):
        return TypeError

    def as_vertices(self, relative=False, scaled=True):
        raise TypeError

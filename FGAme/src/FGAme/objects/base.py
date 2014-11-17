#-*- coding: utf8 -*-
'''

Modificando o estado físico do objeto
-------------------------------------

.. autoclass :: FGAme.Object
    :members:
    :member-order: bysource
    
.. autoclass :: FGAme.LinearObject

'''

from __future__ import absolute_import
if __name__ == '__main__':
    __package__ = 'FGAme.objects'; import FGAme.objects

from math import pi
import pygame
from copy import copy
from ..mathutils import *
from ..utils import *
from ..collision import *
from ..utils import lazy
from ..listener import Listener
PAUSE_SPEED = 5
PAUSE_W_SPEED = 0.05
COLOR_CODES = {
   'red': (255, 0, 0), 'green': (0, 255, 0), 'blue': (0, 0, 255),
   'black': (0, 0, 0), 'white': (255, 255, 255),
}

TWO_PI = 2 * pi

#===============================================================================
# Objetos de colisão -- define a interface básica para a colisão entre 2 objetos
# Todos os outros objetos devem derivar de PhysicsObject. As colisões entre pares
# de objetos são implementadas por multidispatch a partir das funções
# get_collision, avoid_superposition e adjust_superposition no módulo collisions
#===============================================================================
class Object(Listener):
    '''Classe pai para todos os objetos físicos da FGAme.
    
    Attributes
    ----------

    :: 
        **Propriedades físicas do objeto**
    mass
        Massa do objeto. Por padrão é calculada como se a densidade fosse 1.
        Uma massa infinita transforma o objeto num objeto cinemático que não
        responde a forças lineares.
    inertia
        Momento de inércia do objeto com relação ao eixo z no centro de massa.
        Calculado automaticamente a partir da geometria e densidade do objeto.
        Caso seja infinito, o objeto não responderá a torques.
    ROG, ROG_sqr
        Raio de giração e o quadrado do raio de giração. Utilizado para calcular
        o momento de inércia: $I = M R^2$, onde I é o momento de inércia, M a 
        massa e R o raio de giração.
    density
        Densidade de massa: massa / área
    area
        Área que o objeto ocupa

    :: 
        **Variáveis dinâmicas**
    pos_cm
        Posição do centro de massa do objeto
    vel_cm
        Velocidade linear medida a partir do centro de massa
    theta_cm
        Ângulo da rotação em torno do eixo saindo do centro de massa do objeto
    ometa_cm
        Velocidade angular de rotação
    
    :: 
        **Caixa de contorno**
    xmin, xmax, ymin, ymax 
        Limites da caixa de contorno alinhada aos eixos que envolve o objeto
    bbox
        Uma tupla com (xmin, xmax, ymin, ymax)
    shape
        Uma tupla (Lx, Ly) com a forma caixa de contorno nos eixos x e y.
    rect
        Uma tupla com (xmin, ymin, Lx, Ly)
        
    :: 
        **Forças globais**
    
    gravity
        Valor da aceleração da gravidade aplicada ao objeto
    damping, adamping
        Constantes de amortecimento linear e angulor para forças viscosas 
        aplicadas ao objeto
    owns_gravity, owns_damping, owns_adamping
        Se Falso (padrão) utiliza os valores de gravity, damping e adamping
        fornecidos pelo mundo 
    
    
    '''
    def __init__(self, pos_cm=None, vel_cm=None,
                       theta_cm=None, omega_cm=None,
                       mass=None, density=None, inertia=None,
                       color=None, name=None,
                       damping=None, adamping=None, gravity=None,
                       world=None):

        # Variáveis dinâmicas
        self._pos_cm = VectorM(*(pos_cm or (0, 0)))
        self._vel_cm = VectorM(*(vel_cm or (0, 0)))
        self._omega_cm = float(omega_cm or 0)
        self._theta_cm = 0.0
        if theta_cm is not None:
            self.rotate(theta_cm)

        # Propriedades de inércia
        self._density = density or 1.0
        if mass is not None:
            self.mass = mass
        else:
            self.mass  # computa massa a partir da densidade 1.0
        if inertia is not None:
            self.inertia = inertia
        else:
            self.inertia  # computa inércia a partir da densidade 1.0

        # Forças globais
        self._damping = 0.0
        self._adamping = 0.0
        self._gravity = Vector(0, 0)
        if damping:
            self.owns_damping = True
            self._damping = damping
        if adamping:
            self.owns_adamping = True
            self._adamping = adamping
        if gravity:
            self.owns_gravity = True
            self._gravity = Vector(*gravity)

        # Cor/material
        if color is not None: self.color = color

        # Marcas para desenho/debug
        self._draw_ticks = []
        self.name = name

        # Adiciona ao mundo
        if world is not None:
            world.add(self)

    #===========================================================================
    #: Propriedades e constantes físicas
    #===========================================================================

    #---------------------------------------------------------------------------
    # Propriedades da caixa de contorno AABB

    @property
    def xmin(self): return self._xmin

    @property
    def xmax(self): return self._xmax

    @property
    def ymin(self): return self._ymin

    @property
    def ymax(self): return self._ymax

    @property
    def bbox(self):
        return (self._xmin, self._xmax, self._ymin, self._ymax)

    @property
    def shape(self):
        return (self._xmax - self._xmin, self._ymax - self._ymin)

    @property
    def rect(self):
        x, y = self._xmin, self._ymin
        return (x, y, self._xmax - x, self._ymax - y)

    #---------------------------------------------------------------------------
    # Parâmetros físicos
    @property
    def mass(self):
        try:
            return self._mass
        except AttributeError:
            self.mass = self._density * self.area
            return self._mass

    @mass.setter
    def mass(self, value):
        value = float(value)
        self._density = value / self.area
        self._mass = value
        self._invmass = 1.0 / value

    @property
    def inertia(self):
        try:
            return self._inertia
        except AttributeError:
            self.inertia = self._mass * self.ROG_sqr
            return self._inertia

    @inertia.setter
    def inertia(self, value):
        value = float(value)
        self._inertia = value
        self._invinertia = 1.0 / value

    @lazy
    def area(self):
        return (self._xmax - self._xmin) * (self._ymax - self._ymin)

    @lazy
    def ROG_sqr(self):
        a, b = self.shape
        return (a ** 2 + b ** 2) / 12

    @property
    def ROG(self):
        return sqrt(self.R_sqr)

    @property
    def density(self):
        return self._density

    #---------------------------------------------------------------------------
    # Variáveis de estado
    @property
    def pos_cm(self):
        return Vector(*self._pos_cm)

    @pos_cm.setter
    def pos_cm(self, value):
        self.set_pos(value)

    @property
    def vel_cm(self):
        return Vector(*self._vel_cm)

    @vel_cm.setter
    def vel_cm(self, value):
        self.set_vel(value)

    @property
    def theta_cm(self):
        return self._theta_cm

    @theta_cm.setter
    def theta_cm(self, value):
        self.set_theta(value)

    @property
    def omega_cm(self):
        return self._omega_cm

    @omega_cm.setter
    def omega_cm(self, value):
        self.set_omega(value)

    #---------------------------------------------------------------------------
    # Parâmetros físicos derivados
    @property
    def linearE(self):
        if self.can_move_linear:
            return self.mass * dot(self.vel_cm, self.vel_cm) / 2
        else:
            return 0

    @property
    def angularE(self):
        if self.can_move_angular:
            return self.inertia * self.omega_cm ** 2 / 2
        else:
            return 0

    @property
    def kineticE(self):
        return self.kinetic_energy + self.angular_energy

    @property
    def momentumP(self):
        return self.mass * self.vel_cm

    @property
    def momentumL(self):
        return self.inertia * self.omega_cm

    #---------------------------------------------------------------------------
    # Parâmetros que modificam a resposta física de um objeto às forças externas
    # e colisões
    is_alive = is_internal = is_paused = False
    owns_gravity = owns_damping = owns_adamping = False

    @property
    def gravity(self):
        return self._gravity

    @gravity.setter
    def gravity(self, value):
        self._gravity = Vector(*value)
        self.owns_gravity = True

    @property
    def damping(self):
        return self._damping

    @damping.setter
    def damping(self, value):
        self._damping = float(value)
        self.owns_damping = True

    @property
    def adamping(self):
        return self._adamping

    @adamping.setter
    def adamping(self, value):
        self._adamping = float(value)
        self.owns_adamping = True

    EVENTS = {'collision': (0, 1)}

    @property
    def color(self):
        try:
            return self._color
        except AttributeError:
            return (0, 0, 0)

    @color.setter
    def color(self, value):
        value = COLOR_CODES.get(value, value)
        self._color = value

    #===========================================================================
    # Deslocamentos
    #===========================================================================
    def set_pos(self, pos=None):
        '''Reposiciona o centro de massa do objeto nas coordenadas especificadas 
        ou na origem.'''

        if pos is None:
            self.move(-self._pos_cm)
        else:
            self.move(pos - self._pos_cm)

    def set_vel(self, vel=None):
        '''Redefine a velocidade linear do centro de massa para o valor 
        especificado (ou para zero, em caso de omissão).'''

        if vel is None:
            self.boost(-self._vel_cm)
        else:
            self.boost(vel - self._vel_cm)

    def set_theta(self, theta=None):
        '''Reorienta o objeto para o ângulo fornecido ou para a orientação 
        inicial.'''

        if theta is None:
            self.rotate(-self._theta_cm)
        else:
            self.rotate(theta - self._theta_cm)

    def set_omega(self, omega=None):
        '''Redefine a velocidade angular do centro de massa para o valor 
        especificado (ou para zero, em caso de omissão).'''

        if omega is None:
            self.aboost(-self._omega_cm)
        else:
            self.aboost(omega - self._omega_cm)

    def move(self, delta):
        '''Move o objeto por vetor de deslocamento delta'''

        x, y = delta
        self._pos_cm += delta
        self._xmin += x
        self._xmax += x
        self._ymin += y
        self._ymax += y

    def boost(self, delta):
        '''Adiciona um valor vetorial delta à velocidade linear'''

        self._vel_cm += delta

    def rotate(self, theta):
        '''Rotaciona o objeto por um ângulo theta'''

        self._theta_cm += theta
        self._theta_cm %= TWO_PI

    def aboost(self, delta):
        '''Adiciona um valor delta à velocidade ângular'''

        self._omega_cm += delta_omega

    def vpoint(self, pos, relative=False):
        '''Retorna a velocidade linear de um ponto em pos preso rigidamente ao 
        objeto.
        
        Se o parâmetro `relative` for verdadeiro, o vetor `pos` é interpretado
        como a posição relativa ao centro de massa. O padrão é considerá-lo
        como a posição absoluta no centro de coordenadas do mundo.'''

        x, y = pos - self._pos_cm
        return self._vel_cm + self._omega_cm * Vector2D(-y, x)

    #===========================================================================
    # Resposta a forças, impulsos e atualização da física
    #===========================================================================
    def global_force(self):
        return self._mass * (self._gravity - self._damping * self._vel_cm)

    def global_torque(self):
        return -self._inertia * self._omega_cm * self._adamping

    def external_force(self, t):
        '''Define uma força externa que depende do tempo t.
        
        Pode ser utilizado por sub-implementações para definir uma força externa
        aplicada aos objetos de uma sub-classe ou usando o recurso de "duck typing"
        do Python
        
        >>> c = Circle(10)
        >>> c.external_force = lambda t: -c.pos_cm.x  
        '''

        return None

    def external_torque(self, t):
        '''Define uma torque externo análogo ao método .external_force()'''

        return None

    def apply_force(self, force, dt):
        '''Aplica uma força linear durante um intervalo de tempo dt'''

        a = force * self._invmass
        self.boost(a * dt)
        self.move(self._vel_cm * dt + a * (dt ** 2 / 2.))

    def apply_torque(self, torque, dt):
        '''Aplica um torque durante um intervalo de tempo dt'''

        alpha = torque * self._invinertia
        self.aboost(alpha * dt)
        self.rotate(self._omega_cm * dt + alpha * dt ** 2 / 2.)

    def apply_impulse(self, impulse, pos=None, relative=False):
        '''Aplica um impulso linear ao objeto. Isto altera sua velocidade 
        linear com relação ao centro de massa.
        
        Se for chamado com dois agumentos aplica o impulso em um ponto específico
        e também resolve a dinâmica angular.
        '''

        self.boost(impulse / self.mass)

    def apply_aimpulse(self, itorque):
        '''Aplica um impulso angular ao objeto.'''

        self.aboost(itorque / self.inertia)

    def update(self, dt, time=0):
        '''Atualiza o estado do objeto.
        
        Essa função *não* é chamada pelo mundo, mas apenas define uma interface
        uniforme para que objetos isolados possam ser simulados.
        '''

        self.pre_update(t, dt)
        if self.is_dynamic_linear:
            self.apply_force(self.external_force(time), dt)
        if self.is_dynamic_angular:
            self.apply_torque(self.external_torque(time), dt)
        self.post_update(dt)

    def rescale(self, scale, update_physics=True):
        '''Modifica o tamanho do objeto pelo fator de escala fornecido'''

        xcm, ycm = self.pos_cm
        deltax, deltay = self.shape
        deltax, deltay = scale * deltax / 2, scale * deltay / 2
        self.xmin = xcm - deltax
        self.xmax = xcm + deltax
        self.ymin = ycm - deltay
        self.ymax = ycm + deltay

        if update_physics:
            self.mass /= scale ** 2
            self.inertia /= scale ** 2

    #===========================================================================
    # Controle de estado dinâmico
    #===========================================================================
    def pause(self):
        '''Pausa a dinâmica do objeto'''

        if not self.is_paused:
            self.is_paused = True
            self.can_move_linear = False
            self.can_move_angular = False
            self.can_move = False

    def unpause(self):
        '''Retira a pausa de um objeto'''

        self.is_paused = False
        self.can_move_linear = self.is_dynamic_linear
        self.can_move_angular = self.is_dynamic_angular
        self.can_move = self.is_dynamic_linear or self.is_dynamic_angular

        try:
            self.color = self._old_color
        except AttributeError:
            pass

    def is_still(self):
        '''Retorna verdadeiro se o objeto estiver parado ou se movendo muito 
        lentamente'''

        if not self.can_move:
            return True
        else:
            return (self.vel_cm.norm() < PAUSE_SPEED and
                    self.omega_cm < PAUSE_W_SPEED)

    def is_dynamic(self, what=None):
        if what is None:
            return bool(self._invmass) or bool(self._invinertia)
        elif what == 'linear':
            return bool(self._invmass)
        elif what == 'angular':
            return bool(self._invintertia)
        elif what == 'both':
            return bool(self._invmass and self._invinertia)
        else:
            raise ValueError('unknown mode: %r' % what)

    def is_kinematic(self, what=None):
        if what is None:
            return not (self._invmass or self._invinertia)
        elif what == 'linear':
            return not self._invmass
        elif what == 'angular':
            return not self._invintertia
        elif what == 'any':
            return not (self._invmass and self._invinertia)
        else:
            raise ValueError('unknown mode: %r' % what)

    def is_static(self, what=None):
        if what == 'linear':
            return not bool(self._invmass) and not (self._vel_cm.x or self.vel_cm.y)
        elif what == 'angular':
            return not bool(self._invinertia) and not self._omega_cm
        elif what is None:
            return self.is_static('linear') and self.is_static('angular')
        elif what == 'any':
            return self.is_static('linear') or self.is_static('angular')
        else:
            raise ValueError('unknown mode: %r' % what)

    def make_dynamic(self, what=None):
        linear = angular = True
        if what == 'linear':
            angular = False
        elif what == 'angular':
            linear = False
        elif what is not None:
            raise ValueError('unknown mode: %r' % what)

        if linear:
            if not self._invmass: self.mass = self._oldmass
            if not self._vel_cm.norm_sqr(): self.vel_cm = self._oldvel
        if angular:
            if not self._invinertia: self.inertia = self._oldinertia
            if not self._omega_cm: self.omega_cm = self._oldomega

    def make_kinematic(self, what=None):
        linear = angular = True
        if what == 'linear':
            angular = False
        elif what == 'angular':
            linear = False
        elif what is not None:
            raise ValueError('unknown mode: %r' % what)

        if linear:
            if self._invmass:
                self._oldmass = self._mass
                self.mass = 'inf'
        if angular:
            if self._invinertia:
                self._oldinertia = self._inertia
                self.inertia = 'inf'

    def make_static(self, what=None):
        linear = angular = True
        if what == 'linear':
            angular = False
        elif what == 'angular':
            linear = False
        elif what is not None:
            raise ValueError('unknown mode: %r' % what)

        self.make_kinematic(what)
        if linear:
            if self._vel_cm.norm_sqr():
                self._oldvel = tuple(self._vel_cm)
                self.vel_cm = (0, 0)
        if angular:
            if self._omega_cm:
                self._oldomega = self._omega_cm
                self.omega_cm *= 0

    #===========================================================================
    # Desenhando objeto
    #===========================================================================
    def add_point(self, rel_pos, color=(255, 0, 0), radius=5):
        '''Adiciona um ponto para ser desenhado na tela na posição relativa 
        fornecida'''
        self._draw_ticks.append(('point', self.theta_cm, Vector2D(*rel_pos), radius, color))

    def draw(self, screen):
        '''Desenha objeto na tela'''

        self.draw_aabb(screen, color=self.color)
        screen.draw_circle(self.pos, 5, color=self.color)

    def draw_ticks(self, screen):
        '''Desenha pontos na lista de ticks'''

        for i, data in enumerate(self._draw_ticks):
            head, data = data[0], data[1:]
            if head == 'point':
                theta, pos, radius, color = data
                pos = pos.rotated(self.theta_cm - theta) + self.pos_cm
                screen.draw_circle(pos, radius, color=color)

    def draw_aabb(self, screen, color=(255, 0, 0), fill=False):
        '''Desenha a caixa de contorno alinhada ao eixo'''

        screen.draw_aabb(self.xmin, self.xmax, self.ymin, self.ymax,
                         color=color)

    #===========================================================================
    # Interface Python
    #===========================================================================
    # Faz os objetos serem ordenado pelo valor da sua coordenada xmin. Isto
    # facilita a implementação do reordenamento de objetos, já que é possível
    # aplicar a função sort() diretamente na lista de objetos.
    def __gt__(self, other):
        return self.xmin > other.xmin

    def __lt__(self, other):
        return self.xmin < other.xmin

    # Define igualdade <==> identidade
    def __eq__(self, other):
        return self is other

    def __hash__(self):
        return id(self)

    # Representação do objeto como string
    def __repr__(self):
        tname = type(self).__name__
        pos = ', '.join('%.1f' % x for x in self.pos_cm)
        vel = ', '.join('%.1f' % x for x in self.vel_cm)
        return '%s(pos_cm=(%s), vel_cm=(%s))' % (tname, pos, vel)

#===============================================================================
# Classes derivadas
#===============================================================================
class LinearObject(Object):
    '''Classe base para todos os objetos que não possuem dinâmica angular.'''

    def __init__(self, **kwds):
        if 'inertia' in kwds or 'omega_cm' in kwds or 'theta_cm' in kwds:
            raise TypeError('cannot set angular properties of linear objects')
        super(LinearObject, self).__init__(**kwds)
        self._invinertia = self._omega_cm = self._theta_cm = 0.0
        self._inertia = float('inf')

    @property
    def inertia(self):
        return float('inf')

    omega_cm = copy(Object.omega_cm)
    @omega_cm.setter
    def omega_cm(self, value):
        if value:
            raise ValueError('LinearObjects have null angular velocity')

    theta_cm = copy(Object.theta_cm)
    @omega_cm.setter
    def theta_cm(self, value):
        if value:
            raise ValueError('LinearObjects have fixed orientation')

if __name__ == '__main__':
    from FGAme import *
    import doctest
    doctest.testmod()

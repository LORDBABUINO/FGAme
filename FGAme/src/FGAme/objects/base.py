# -*- coding: utf8 -*-
from __future__ import absolute_import
if __name__ == '__main__':
    __package__ = 'FGAme.objects'; import FGAme.objects

from math import pi
import pygame
from ..mathutils import *
from ..utils import *
from ..collision import *
PAUSE_SPEED = 10
PAUSE_W_SPEED = 0.1

#===============================================================================
# Objetos de colisão -- define a interface básica para a colisão entre 2 objetos
# Todos os outros objetos devem derivar de PhysicsObject. As colisões entre pares
# de objetos são implementadas por multidispatch a partir das funções
# get_collision, avoid_superposition e adjust_superposition no módulo collisions
#===============================================================================
class PhysicsObject(object):
    '''Documente-me!'''
    def __init__(self, pos_cm=None, vel_cm=None,
                       theta_cm=None, omega_cm=None,
                       mass=None, density=None, inertia=None,
                       is_dynamic_linear=None, is_dynamic_angular=None,
                       color=None, obj_class=None, material=None):

        # Variáveis dinâmicas
        if pos_cm is not None: self.pos_cm = Vector2D(*pos_cm)
        if vel_cm is not None: self.vel_cm = Vector2D(*vel_cm)
        if omega_cm is not None: self.omega_cm = float(omega_cm)
        if theta_cm is not None:
            self.theta_cm = 0.0
            self.rotate(theta_cm)

        # Propriedades de inércia
        if density:
            mass = self.area * density
        if mass is not None: self.mass = mass
        if inertia is not None: self.inertia = inertia

        # is_dynamic* e similares
        if is_dynamic_linear is not None: self.is_dynamic_linear = is_dynamic_linear
        if is_dynamic_angular is not None: self.is_dynamic_angular = is_dynamic_angular

        # Cor/material
        if color is not None: self.color = color
        if obj_class is not None: self.obj_class = obj_class
        if material is not None: self.material = material

        # Marcas para desenho/debug
        self._draw_ticks = []

        # Testa a sanidade da caixa de contorno
        assert self.xmin < self.xmax, 'xmin: %.1f, xmax: %.1f' % (self.xmin, self.xmax)
        assert self.ymin < self.ymax, 'ymin: %.1f, ymax: %.1f' % (self.ymin, self.ymax)

    #===========================================================================
    # Propriedades e constantes físicas
    #===========================================================================

    #---------------------------------------------------------------------------
    # Propriedades da caixa de contorno AABB
    xmin = xmax = ymin = ymax = 0

    @property
    def bbox(self):
        return (self.xmin, self.xmax, self.ymin, self.ymax)

    @property
    def shape(self):
        return (self.xmax - self.xmin, self.ymax - self.ymin)

    @property
    def rect(self):
        x, y = self.xmin, self.ymin
        return (x, y, self.xmax - x, self.ymax - y)

    #---------------------------------------------------------------------------
    # Parâmetros físicos
    mass = inertia = 1

    @property
    def area(self):
        return (self.xmax - self.xmin) * (self.ymax - self.ymin)

    @property
    def density(self):
        return self.mass / self.area

    #---------------------------------------------------------------------------
    # Variáveis de estado
    pos_cm = vel_cm = Vector2D(0, 0)
    theta_cm = omega_cm = 0

    #---------------------------------------------------------------------------
    # Parâmetros físicos derivados
    @property
    def kinetic_energy(self):
        if self.can_move_linear:
            return self.mass * dot(self.vel_cm, self.vel_cm) / 2
        else:
            return 0

    @property
    def angular_energy(self):
        if self.can_move_angular:
            return self.inertia * self.omega_cm ** 2 / 2
        else:
            return 0

    @property
    def total_energy(self):
        return self.kinetic_energy + self.angular_energy

    @property
    def linear_momentum(self):
        return self.mass * self.vel_cm

    @property
    def angular_momentum(self):
        return self.inertia * self.omega_cm

    #---------------------------------------------------------------------------
    # Parâmetros que modificam a resposta física de um objeto às forças externas
    # e colisões
    can_move_linear = can_move_angular = can_move = True
    _is_dynamic_linear = _is_dynamic_angular = True
    is_alive = is_internal = is_paused = False

    @property
    def is_dynamic_linear(self):
        return self._is_dynamic_linear

    @is_dynamic_linear.setter
    def is_dynamic_linear(self, value):
        self._is_dynamic_linear = value
        if not value:
            self.can_move_linear = False
            self.can_move = self.can_move_linear or self.can_move_angular

    @property
    def is_dynamic_angular(self):
        return self._is_dynamic_angular

    @is_dynamic_angular.setter
    def is_dynamic_angular(self, value):
        self._is_dynamic_angular = value
        if not value:
            self.can_move_angular = False
            self.can_move = self.can_move_linear or self.can_move_angular

    #---------------------------------------------------------------------------
    # Material, classe, desenho e outras formas de interação com World()
    obj_class = material = None
    COLOR_CODES = {
       'red': (255, 0, 0), 'green': (0, 255, 0), 'blue': (0, 0, 255),
       'black': (0, 0, 0), 'white': (255, 255, 255),
    }

    @property
    def color(self):
        try:
            return self._color
        except AttributeError:
            if self.obj_class is not None and self.obj_class.color is not None:
                return self.obj_class.color
            elif self.material is not None and self.material.color is not None:
                return self.material.color
            else:
                return (0, 0, 0)

    @color.setter
    def color(self, value):
        value = self.COLOR_CODES.get(value, value)
        self._color = value

    ############################################################################
    # Deslocamentos
    ############################################################################
    def scale(self, scale, update_physics=False):
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
            self.intertia /= scale ** 2

    def move(self, delta_pos):
        '''Move o objeto por vetor de deslocamento delta_r'''

        x, y = delta_pos
        self.pos_cm += delta_pos
        self.xmin += x
        self.xmax += x
        self.ymin += y
        self.ymax += y

    def set_position(self, pos=None):
        '''Posiciona o centro de massa do objeto na origem
        
        O segundo argumento opcional define um ponto de reposicionamento fora da
        origem.'''

        if pos is None:
            self.move(-self.pos_cm)
        else:
            self.move(pos - self.pos_cm)

    def rotate(self, theta):
        '''Rotaciona o objeto por um ângulo theta'''

        self.theta_cm += theta

    def reorient(self, theta=None):
        '''Reorienta o objeto para a sua orientação original'''

        self.theta_cm = theta or 0.0

    #===========================================================================
    # Mudança de velocidade
    #===========================================================================
    def linear_boost(self, delta_vel):
        '''Modifica a velocidade linear por um valor delta_v'''

        self.vel_cm += delta_vel

    def linear_stop(self, vel=None):
        '''Zera a velocidade linear do objeto.
        
        O segundo argumento permite definir uma velocidade de parada diferente 
        de zero'''

        self.vel_cm = vel or Vector2D(0, 0)

    def angular_boost(self, delta_omega):
        '''Modifica a velocidade angular por um valor delta_v'''

        self.omega_cm += delta_omega

    def angular_stop(self, vel=None):
        '''Zera a velocidade angular do objeto
        
        O segundo argumento permite definir uma velocidade de parada diferente 
        de zero'''

        self.omega_cm = vel or 0.0

    def get_vpoint(self, pos):
        '''Retorna a velocidade linear de um ponto em pos preso ao objeto.'''

        x, y = pos - self.pos_cm
        return self.vel_cm + self.omega_cm * Vector2D(-y, x)

    #===========================================================================
    # Resposta a forças, impulsos e atualização da física
    #===========================================================================
    def external_force(self, t):
        '''Retorna o valor atual de uma força externa aplicada ao objeto'''

        return Vector2D(0, 0)

    def external_torque(self, t):
        '''Retorna o valor atual de um torque externo aplicado ao objeto'''

        return 0

    def apply_force(self, force, dt):
        '''Aplica uma força linear durante um intervalo de tempo dt'''

        a = force / self.mass
        self.linear_boost(a * dt)
        self.move(self.vel_cm * dt + a * (dt ** 2 / 2.))

    def apply_torque(self, torque, dt):
        '''Aplica um torque durante um intervalo de tempo dt'''

        alpha = torque / self.inertia
        self.angular_boost(alpha * dt)
        self.rotate(self.omega_cm * dt + alpha * dt ** 2 / 2.)

    def apply_linear_impulse(self, impulse):
        '''Aplica um impulso linear ao objeto. Isto altera sua velocidade 
        linear com relação ao centro de massa.'''

        self.linear_boost(impulse / self.mass)

    def apply_angular_impulse(self, itorque):
        '''Aplica a resposta angular de um impulso aplicado ao objeto no ponto 
        'pos'. Isto resulta em uma variação descontínua da velocidade angular do 
        objeto.'''

        self.angular_boost(itorque / self.inertia)

    def pre_update(self, t, dt):
        '''Função chamada pelo mundo *antes* de atualizar a física do objeto
        que permite ao mesmo atualizar o seu estado interno.
        
        A implementação padrão não faz nada.'''

    def post_update(self, t, dt):
        '''Função chamada pelo mundo *após* de atualizar a física do objeto
        e que permite ao mesmo atualizar o seu estado interno.
        
        A implementação padrão não faz nada.'''

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

    #===========================================================================
    # Ajustes de superposição
    #===========================================================================
    def pause(self):
        '''Pausa a dinâmica do objeto'''

        if not self.is_paused:
            self.is_paused = True
            self.can_move_linear = False
            self.can_move_angular = False
            self.can_move = False
            self._old_color = self.color
            self.color = 'black'

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
class LinearObject(PhysicsObject):
    '''Classe base para todos os objetos que não possuem dinâmica angular.'''

    @property
    def is_dynamic_angular(self):
        return False

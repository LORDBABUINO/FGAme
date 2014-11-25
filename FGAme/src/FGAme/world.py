#-*- coding: utf8 -*-
from __future__ import print_function

from FGAme.mathutils import *
from FGAme.backends import get_mainloop, get_input_listener
from FGAme.objects import AABB, Poly
from FGAme.collision import get_collision, get_collision_aabb, CollisionError
from FGAme.utils import shadow_y
from FGAme.listener import Listener, InputListener

#===============================================================================
# Classe Mundo -- coordena todos os objetos com uma física definida e resolve a
# interação entre eles
#===============================================================================
class World(Listener):
    '''Documente-me!
    '''

    def __init__(self, background=None,
                 gravity=None, damping=0, adamping=0,
                 rest_coeff=1, sfriction=0, dfriction=0, stop_velocity=1e-6,
                 skip_draw=None, skip_physics=None):

        if background is not None:
            background = tuple(background)
        self.background = background
        self._objects_col = []
        self._objects_render = [[]]
        self._layer_shift = 0

        # Inicia a gravidade e as constantes de força dissipativa
        self.gravity = gravity or (0, 0)
        self.damping = damping
        self.adamping = adamping

        # Colisão
        self.rest_coeff = float(rest_coeff)
        self.sfriction = float(sfriction)
        self.dfriction = float(dfriction)
        self.stop_velocity = float(stop_velocity)
        self.time = 0
        self._bounds = None
        self._hard_bounds = None

        # Controle de callbacks
        self.is_paused = False
        self._main_loop = get_mainloop()
        self._input_listener = get_input_listener()
        super(World, self).__init__()

    #===========================================================================
    # Propriedades
    #===========================================================================
    @property
    def gravity(self):
        return self._gravity

    @gravity.setter
    def gravity(self, value):
        try:
            gravity = self._gravity = Vector(*value)
        except TypeError:
            gravity = self._gravity = Vector(0, -value)

        for obj in self._objects_col:
            if not obj.owns_gravity:
                obj._gravity = gravity

    @property
    def damping(self):
        return self._damping

    @damping.setter
    def damping(self, value):
        value = self._damping = float(value)

        for obj in self._objects_col:
            if not obj.owns_damping:
                obj._damping = value

    @property
    def adamping(self):
        return self._adamping

    @adamping.setter
    def adamping(self, value):
        value = self._adamping = float(value)

        for obj in self._objects_col:
            if not obj.owns_adamping:
                obj._adamping = value

    #===========================================================================
    # Gerenciamento de objetos
    #===========================================================================
    def add(self, obj, layer=0, has_collision=True):
        '''Adiciona um novo objeto ao mundo.
        
        Exemplos
        --------
        
        >>> obj = AABB((-10, 10, -10, 10))
        >>> world = World()
        >>> world.add(obj, layer=-1)
        
        '''

        # Verifica se trata-se de uma lista de objetos
        if not hasattr(obj, 'draw'):
            for obj in obj:
                self.add(obj, layer=layer, has_collision=has_collision)
            return

        # Adiciona na lista de renderização
        if layer < 0:
            self._layer_shift = min(layer, self._layer_shift)
        idx = layer - self._layer_shift
        try:
            self._objects_render[idx].append(obj)
        except IndexError:
            extra = [ [] for _ in range(idx - len(self._objects_render) + 1) ]
            self._objects_render.extend(extra)
            self._objects_render[idx].append(obj)

        # Adiciona na lista de colisões
        if has_collision:
            obj.is_alive = True
            if not obj.owns_gravity:
                obj._gravity = self.gravity
            if not obj.owns_damping:
                obj._damping = self.damping
            if not obj.owns_adamping:
                obj._adamping = self.adamping

            self._objects_col.append(obj)

    def remove(self, obj):
        '''Descarta um objeto do mundo'''

        for i, obj_i in enumerate(self._objects_col):
            if obj is obj_i:
                del self._objects_col[i]
                break

        for layer in self._objects_render:
            for i, obj_i in enumerate(layer):
                if obj is obj_i:
                    del layer[i]
                    return

    #===========================================================================
    # Event control
    #===========================================================================
    EVENTS = InputListener.EVENTS.copy()
    EVENTS.update({
        'collision': (0, 1),
        'collision-pair': (2, 1),
        'frame-enter': (0, 0),
    })

    def _listen_long_press(self, key, cb_func=None, args=None, kwargs=None):
        if cb_func:
            self._input_listener.listen('long-press', key, cb_func, args, kwargs)
        else:
            return self._input_listener.listen('long-press', key)

    def _listen_key_up(self, key, cb_func=None, args=None, kwargs=None):
        if cb_func:
            self._input_listener.listen('key-up', key, cb_func, args, kwargs)
        else:
            return self._input_listener.listen('key-up', key)

    def _listen_key_down(self, key, cb_func=None, args=None, kwargs=None):
        if cb_func:
            self._input_listener.listen('key-down', key, cb_func, args, kwargs)
        else:
            return self._input_listener.listen('key-down', key)

    #===========================================================================
    # Simulação de Física
    #===========================================================================
    def pause(self):
        '''Pausa a simulação de física'''

        self.is_paused = True

    def unpause(self):
        '''Resume a simulação de física'''

        self.is_paused = False

    def toggle_pause(self):
        '''Alterna entre o estado de pausa da simulação'''

        self.is_paused = not self.is_paused

    def update(self, dt):
        '''Rotina principal da simulação de física.'''

        if self.is_paused:
            return
        self.trigger('frame-enter')
        self.resolve_forces(dt)
        self.pre_update(dt)
        collisions = self.detect_collisions(dt)
        collisions = self.broadcast_collisions(collisions, dt)
        self.resolve_collisions(collisions, dt)
        self.post_update(dt)
        self.time += dt
        return self.time

    def pre_update(self, dt):
        '''Executa a rotina de pré-atualização em todos os objetos.
        
        A fase de pré-atualização é executada no início de cada frame antes da 
        atualização da física. Nesta fase objetos podem atualizar o estado 
        interno ou realizar qualquer tipo de modificação antes do cálculo das 
        forças e colisões.
        '''

        # Chama a pre-atualização de cada objeto
        t = self.time
        for obj in self._objects_col:
            # obj.pre_update(t, dt)
            # obj.is_colliding = False
            pass

    def post_update(self, dt):
        '''Executa a rotina de pós-atualização em todos os objetos. 
        
        Este passo é executado em cada frame após resolver a dinâmica de 
        forças e colisões.'''

        t = self.time
        for obj in self._objects_col:
            # obj.post_update(t, dt)
            pass

    def detect_collisions(self, dt):
        '''Retorna uma lista com todas as colisões atuais.
        
        Uma colisão é caracterizada por um objeto da classe Collision() ou 
        subclasse.'''

        objects = self._objects_col
        objects.sort()
        collisions = []
        objects.sort()

        # Os objetos estão ordenados. Este loop detecta as colisões AABB e,
        # caso elas aconteçam, delega a tarefa de detecção fina de colisão para
        # a função get_collision
        for i, A in enumerate(objects):
            xmax = A.xmax
            for j in range(i + 1, len(objects)):
                B = objects[j]

                # Procura na lista enquanto xmin de B for menor que xmax de A
                if B.xmin > xmax:
                    break

                # Não detecta colisão entre dois objetos estáticos/cinemáticos
                if A._invmass == A._invinertia == B._invmass == B._invinertia == 0:
                    continue

                # Somente testa as colisões positivas por AABB
                if shadow_y(A, B) < 0:
                    continue

                # Detecta colisões e atualiza as listas internas de colisões de
                # cada objeto
                col = self.get_collision(A, B)
                if col is not None:
                    col.world = self
                    collisions.append(col)
                    A.trigger('collision', col)
                    B.trigger('collision', col)

        return collisions

    def resolve_collisions(self, collisions, dt):
        '''Resolve todas as colisões na lista collisions'''

        for col in collisions:
            col.resolve(dt)

    def broadcast_collisions(self, collisions, dt):
        '''Anuncia todas as colisões para os objetos envolvidos'''

#         if self._cb_object or self._cb_pair or self._cb_unbound:
#             for col in collisions:
#                 # Recupera os objetos que participam da colisão
#                 A, B = pair = col.objects
#
#                 # Executa todos os callbacks do _cb_unbound
#                 for cb in self._cb_unbound:
#                     cb(col)
#
#                 # Executa o callback se A ou B estiverem registrados como
#                 # callback simples
#                 for obj, cb in self._cb_object.items():
#                     if obj is A or obj is B:
#                         cb(col)
#
#                 # Executa um callback registrado para o par de objetos
#                 if pair in self._cb_pair:
#                     self._cb_pair[pair](col)
#
        return collisions

    def get_collision(self, A, B):
        '''Retorna a colisão entre os objetos A e B depois que a colisão AABB
        foi detectada'''

        try:
            return get_collision(A, B)
        except CollisionError:
            pass

        # Colisão não definida. Primeiro tenta a colisão simétrica e registra
        # o resultado caso bem sucedido. Caso a colisão simétrica também não
        # seja implementada, define a colisão como uma aabb
        try:
            col = get_collision(B, A)
            if col is None:
                return
            col.normal *= -1
        except CollisionError:
            get_collision[type(A), type(B)] = get_collision_aabb
            get_collision[type(B), type(A)] = get_collision_aabb
            return get_collision_aabb(A, B)
        else:
            def inverse(A, B):
                '''Automatically created collision for A, B from the supported
                collision B, A'''
                col = direct(B, A)
                if col is not None:
                    return col.swapped()

            direct = get_collision[type(B), type(A)]
            get_collision[type(A), type(B)] = inverse
            return col

    def resolve_forces(self, dt):
        '''Resolve a dinâmica de forças durante o intervalo dt'''

        t = self.time

        # Acumula as forças e acelerações
        for obj in self._objects_col:
            if obj._invmass:
                F = obj._init_frame_force()
                F += obj.external_force(t) or (0, 0)
            elif obj.accel_static:
                a = obj._init_frame_accell()
                obj.apply_accel(a)

            if obj._invinertia:
                tau = obj.global_torque()
                tau += obj.external_torque(t) or 0
                self._frame_tau = tau
            elif obj.accel_static:
                a = obj._init_frame_alpha()
                obj.apply_alpha(a)

        # Applica as forças e acelerações
        for obj in self._objects_col:
            if obj._invmass:
                obj.apply_force(obj._frame_force, dt)
            elif obj._vel_cm.x or obj._vel_cm.y:
                obj.move(obj._vel_cm * dt)

            if obj._invinertia:
                obj.apply_torque(obj._frame_tau, dt)
            elif obj._omega_cm:
                obj.rotate(obj._omega_cm * dt)

    #===========================================================================
    # Cálculo de parâmetros físicos
    #===========================================================================
    def kinetic_energy(self):
        '''Retorna a soma da energia cinética de todos os objetos do mundo'''
        return sum(obj.kinetic() for obj in self.objects)

    #===========================================================================
    # Desenha objetos
    #===========================================================================
    def draw(self, screen):
        '''Desenha todos os objetos no mundo'''

        if self.background:
            screen.clear(self.background)
        for layer in self._objects_render:
            for obj in layer:
                obj.draw(screen)
                obj.draw_ticks(screen)

    #===========================================================================
    # Laço principal
    #===========================================================================
    def run(self, timeout=None, sym_timeout=None):

        self._main_loop.physics_update = self.update
        self._main_loop.draw = self.draw
        self._main_loop.run()

    def stop(self):
        self._main_loop.stop()

    def set_next_state(self, value):
        pass

    #===========================================================================
    # Criação de objetos especiais
    #===========================================================================
    def make_bounds(self, xmin, xmax, ymin, ymax, hard=True, delta=100, use_poly=False):
        '''Cria contorno'''

        assert xmin < xmax and ymin < ymax, 'invalid bounds'
        maker = Poly.rect if use_poly else AABB
        up = maker(bbox=(xmin - delta, xmax + delta, ymax, ymax + delta))
        down = maker(bbox=(xmin - delta, xmax + delta, ymin - delta, ymin))
        left = maker(bbox=(xmin - delta, xmin, ymin, ymax))
        right = maker(bbox=(xmax, xmax + delta, ymin, ymax))
        for box in [up, down, left, right]:
            box.make_static()
        self.add(down)
        self.add(up)
        self.add(left)
        self.add(right)
        self._bounds = (left, right, up, down)
        self._hard_bounds = hard

    def populate_random(self, size, tt, random_sizes=True, random_colors=True):
        '''Insere uma população aleatória de tamanho igual à size com objetos
        da classe tt'''

        raise

if __name__ == '__main__':
    import doctest
    doctest.testmod()


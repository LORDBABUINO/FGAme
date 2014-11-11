# -*- coding: utf8 -*-
from __future__ import print_function
from screen import PyGameScreen as Screen
from mathutils import *
from objects import AABB, Circle, Poly
from collision import get_collision, get_collision_aabb, CollisionError
from utils import shadow_y

#===============================================================================
# Classe Mundo -- coordena todos os objetos com uma física definida e resolve a
# interação entre eles
#===============================================================================
class World(object):
    '''Documente-me!
    '''

    def __init__(self, background=None,
                 gravity=None, alpha=0, beta=0,
                 rest_coeff=1, sfriction=0, dfriction=0, stop_velocity=1e-6):

        if background is not None:
            background = tuple(background)
        self.background = background
        self._objects_col = []
        self._objects_render = [[]]
        self._layer_shift = 0

        # Inicia a gravidade e as constantes de força dissipativa
        if isinstance(gravity, (int, float)):
            self.gravity = Vector2D(0, -gravity)
        else:
            self.gravity = Vector2D(*(gravity  or (0, 0)))

        # Salva outros parâmetros físicos
        self.alpha = float(alpha)
        self.beta = float(beta)
        self.rest_coeff = float(rest_coeff)
        self.sfriction = float(sfriction)
        self.dfriction = float(dfriction)
        self.stop_velocity = float(stop_velocity)
        self.time = 0
        self._bounds = None
        self._hard_bounds = None

        # Controle de callbacks de colisão
        self._cb_pair = {}
        self._cb_object = {}
        self._cb_unbound = []

    #===========================================================================
    # Gerenciamento de objetos
    #===========================================================================
    def add_object(self, obj, layer=0, has_collision=True):
        '''Adiciona um novo objeto ao mundo.
        
        Exemplos
        --------
        
        >>> obj = AABB((-10, 10, -10, 10))
        >>> world = World()
        >>> world.add_object(obj, layer=-1)
        
        '''

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
            self._objects_col.append(obj)

    def remove_object(self, obj):
        '''Descarta um objeto do mundo'''

        for i, obj_i in enumerate(self._objects_col):
            if obj is obj_i:
                del self._objects_col[i]
                break

        for layer in self._objects_render:
            for i, obj_i in enumerate(layer):
                if obj is obj_i:
                    del self._objects_col[i]
                    break
            else:
                continue
            break

    def clean_objects(self):
        '''Limpa todos os objetos que foram marcados para destruição'''

        # TODO: remover da lista de desenho
        del_list = [ idx for idx, obj in enumerate(self.objects) if not obj.is_alive ]

    def register_collision_callback(self, cb, *objects):
        '''Registra uma função de callback para quando ocorre a colisão com um
        determinado objeto ou par de objetos.
        
        O callback fornecido é uma função que recebe um objeto de colisão como 
        único argumento.'''

        if len(objects) == 0:
            self._cb_unbound.append(cb)
        elif len(objects) == 1:
            self._cb_object[objects[0]] = cb
        elif len(objects) == 2:
            obj1, obj2 = objects
            self._cb_pair[obj1, obj2] = self._cb_pair[obj2, obj1] = cb
        else:
            raise ValueError('only 0, 1 or 2 objects are necessary')

    #===========================================================================
    # Simulação de Física
    #===========================================================================
    def update(self, dt):
        '''Rotina principal da simulação de física.'''

        self.resolve_forces(dt)
        self.pre_update(dt)
        collisions = self.detect_collisions(dt)
        collisions = self.broadcast_collisions(collisions, dt)
        self.resolve_collisions(collisions, dt)
        self.post_update(dt)
        self.time += dt

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
            obj.pre_update(t, dt)
            obj.is_colliding = False

    def post_update(self, dt):
        '''Executa a rotina de pós-atualização em todos os objetos. 
        
        Este passo é executado em cada frame após resolver a dinâmica de 
        forças e colisões.'''

        t = self.time
        for obj in self._objects_col:
            obj.post_update(t, dt)

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

                # Não detecta colisão entre dois objetos estáticos
                if ((A.can_move_linear == B.can_move_linear == False) and
                    (A.can_move_angular == B.can_move_angular == False)):
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

        return collisions

    def resolve_collisions(self, collisions, dt):
        '''Resolve todas as colisões na lista collisions'''

        for col in collisions:
            col.resolve(dt)

    def broadcast_collisions(self, collisions, dt):
        '''Anuncia todas as colisões para os objetos envolvidos'''

        if self._cb_object or self._cb_pair or self._cb_unbound:
            for col in collisions:
                # Recupera os objetos que participam da colisão
                A, B = pair = col.objects

                # Executa todos os callbacks do _cb_unbound
                for cb in self._cb_unbound:
                    cb(col)

                # Executa o callback se A ou B estiverem registrados como
                # callback simples
                for obj, cb in self._cb_object.items():
                    if obj is A or obj is B:
                        cb(col)

                # Executa um callback registrado para o par de objetos
                if pair in self._cb_pair:
                    self._cb_pair[pair](col)

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

        gaccel = self.gravity
        alpha = self.alpha
        beta = self.beta
        t = self.time

        for obj in self._objects_col:
            if obj.can_move_linear:
                F = obj.external_force(t)
                mass = obj.mass
                if gaccel:
                    F += gaccel * mass
                if alpha:
                    F += (-alpha * mass) * obj.vel_cm
                obj.apply_force(F, dt)
            if obj.can_move_angular:
                tau = obj.external_torque(t)
                if beta:
                    I = obj.inertia
                    tau += -beta * I * obj.omega_cm
                obj.apply_torque(tau, dt)

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
    # Criação de objetos especiais
    #===========================================================================
    def make_bounds(self, xmin, xmax, ymin, ymax, hard=True, delta=100, use_poly=False):
        '''Cria contorno'''

        assert xmin < xmax and ymin < ymax, 'invalid bounds'
        maker = Poly.rect if use_poly else AABB
        down = maker(bbox=(xmin - delta, xmax + delta, ymin - delta, ymin), is_dynamic_linear=False)
        up = maker(bbox=(xmin - delta, xmax + delta, ymax, ymax + delta), is_dynamic_linear=False)
        left = maker(bbox=(xmin - delta, xmin, ymin, ymax), is_dynamic_linear=False)
        right = maker(bbox=(xmax, xmax + delta, ymin, ymax), is_dynamic_linear=False)
        if use_poly:
            for box in [up, down, left, right]:
                box.is_dynamic_angular = False
        self.add_object(down)
        self.add_object(up)
        self.add_object(left)
        self.add_object(right)
        self._bounds = (left, right, up, down)
        self._hard_bounds = hard

    def populate_random(self, size, tt, random_sizes=True, random_colors=True):
        '''Insere uma população aleatória de tamanho igual à size com objetos
        da classe tt'''

        raise

if __name__ == '__main__':
    import doctest
    doctest.testmod()


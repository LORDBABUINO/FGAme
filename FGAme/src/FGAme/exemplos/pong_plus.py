#-*- coding: utf8 -*-
from FGAme import *
from random import uniform, choice, random
from math import pi

class Pong:
    def __init__(self, **kwds):
        self.ball = self.make_ball()
        self.pong = self.make_pong()
        self.time_bar = self.make_time_bar()
        self.world = self.make_world()
        self.world.add(self.pong)
        self.world.add(self.ball)
        self.world.add(self.time_bar, layer=1, has_collision=False)
        self.pong_x = self.pong.pos_cm.x
        self.hits = 0

        # Adiciona objetos extra
        self.stray = []
        for i in range(self.stray_N):
            new = self.make_stray()
            self.stray.append(new)
            self.world.add(new)

        # Define amplitude de movimento do pong
        self.max_pong_y = (self.screen_height - self.pong_height - 20) / 2
        self.min_pong_y = -self.max_pong_y

        # Desenha pontos de hit acinzentados
        for i in range(self.max_hits):
            hit = self.make_hit_mark(i, self.hits_bg)
            self.world.add(hit, layer=1, has_collision=False)

        # Salva parâmetros adicionais
        for k, v in kwds.items():
            setattr(self, k, v)

    #===========================================================================
    # Variáveis
    #===========================================================================
    # Formas, tamanhos e posições
    screen_height = 600
    screen_width = 800
    pong_height = 150
    pong_width = 20
    ball_sides = 5
    ball_size = 30
    hit_size = 10
    pong_step = 5
    inertia_multiplier = 20

    # Velocidades
    ball_speed = 400
    max_ball_speed = 500

    # Lógica do jogo
    max_hits = 10
    stray_N = 20
    stray_sides = 4
    stray_size = 30
    stray_color = (50, 50, 100)
    stray_dynamic = True

    # Cores
    hits_bg = (150, 150, 150)
    gravity = 0
    next_params = {}

    #===========================================================================
    # Criação e inicialização de objetos
    #===========================================================================
    def make_world(self):
        '''Inicializa o mundo'''

        H, W = self.screen_height / 2, self.screen_width / 2
        world = World(rest_coeff=0.9, dfriction=0.3, gravity=self.gravity)
        world.make_bounds(-W + 10, 2 * W, -H + 10, H - 10, delta=400)
        world.listen('frame-enter', self.check_fail)
        world.listen('frame-enter', self.update_time)
        world.listen('frame-enter', self.accelerate_ball)
        world.listen('long-press', 'up', self.move_up)
        world.listen('long-press', 'down', self.move_down)

        return world

    def make_pong(self):
        '''Inicializa a raquete'''

        Y = self.pong_height
        X = self.pong_width
        pong = Poly([(0, 0), (0, Y), (-X / 3, Y), (-X, 0.66 * Y), (-X, 0.33 * Y), (-X / 3, 0)])
        pong.move((350, -Y / 2))
        pong.make_static('angular')
        pong.listen('collision', self.pong_collision)
        pong.external_force = lambda t:-15000 * pong.vel_cm - 10000 * Vector(pong.pos_cm.x - self.pong_x, 0)
        return pong

    def make_ball(self):
        '''Inicializa o a bola'''

        ball = Poly.regular(self.ball_sides, self.ball_size, color='red', density=1)
        ball.inertia *= self.inertia_multiplier
        V = self.ball_speed
        speed = -V, choice([-1, 1]) * uniform(0.25 * V, 2 * V)
        ball.boost(speed)
        return ball

    def make_stray(self):
        '''Cria um objeto aleatório que fica no meio da tela'''

        # Cria obstáculo
        obj = Poly.regular(self.stray_sides, self.stray_size,
                           color=self.stray_color, density=1)
        obj.scale(uniform(0.75, 2))
        obj.rotate(uniform(0, 2 * pi))
        obj.inertia *= self.inertia_multiplier
        if not self.stray_dynamic:
            obj.make_static()

        # Define amplitude de movimento para posições aleatórias
        W, H = self.screen_width / 2, self.screen_height / 2
        xmin = -W - obj.xmin
        xmax = W - obj.xmax - 2 * self.pong_width
        ymin = -H - obj.ymin
        ymax = H - obj.ymax

        # Retorna objeto em nova posição
        obj.move((uniform(xmin, xmax), uniform(ymin, ymax)))
        return obj

    def make_hit_mark(self, n_hits, color='red'):
        '''Retorna um objeto que mostra na tela o número de hits'''

        W, H = self.screen_width / 2, self.screen_height / 2
        pos_x = 2 * self.hit_size - W + 3 * self.hit_size * n_hits + 10
        pos_y = H - 2 * self.hit_size - 10
        return Circle(self.hit_size, pos_cm=(pos_x, pos_y), color=color)

    def make_time_bar(self):
        '''Cria uma nova barra de tempo na lateral da tela'''

        H, W = self.screen_height / 2, self.screen_width / 2
        return AABB(shape=(20, 20), pos_cm=(W - 10, -H + 20), color=(255, 225, 0))

    #===========================================================================
    # Callbacks de interação com o usuário
    #===========================================================================
    def move_up(self):
        '''Acionado com a seta para cima'''

        if self.pong.pos_cm.y < self.max_pong_y:
            self.pong.move((0, self.pong_step))
            self.pong.vel_cm = (0, 400)

    def move_down(self):
        '''Acionado com a seta para baixo'''

        if self.pong.pos_cm.y > self.min_pong_y:
            self.pong.move((0, -self.pong_step))
            self.pong.vel_cm = (0, -400)

    def update_time(self):
        '''Atualizado a cada frame para incrementar a barra de contagem do 
        tempo'''

        self.time_bar.ymax = ymax = self.world.time * 20 - self.screen_height / 2 + 20
        if ymax > (self.screen_height / 2 - 10):
            self.next()

    def accelerate_ball(self):
        '''Incrementa a velocidade da bola até um determinado limite'''

        V = self.ball.vel_cm.norm()
        if V < self.max_ball_speed:
            V += 5
            self.ball.vel_cm = self.ball.vel_cm.normalized() * V

    def check_fail(self):
        '''Checa se o jogador perdeu e acrecenta um hitpoint, em caso positivo'''

        if self.ball.pos_cm.x > self.screen_width / 2:
            self.hit_increment()
            self.hit_increment()
            self.world.remove(self.ball)
            self.ball = self.make_ball()
            self.world.add(self.ball)

        for i, obj in enumerate(self.stray):
            if obj.pos_cm.x > self.screen_width / 2:
                self.hit_increment()
                self.world.remove(obj)
                del self.stray[i]
                break

    def hit_increment(self):
        '''Incrementa os hit counts'''
        # Testa derrota
        if self.hits >= self.max_hits - 1:
            self.loose()

        # Incrementa o número de hits
        hit = self.make_hit_mark(self.hits)
        self.world.add(hit, layer=1, has_collision=False)
        self.hits += 1

    def pong_collision(self, col):
        '''Chamado quando a bola colide com o pong'''

        # testa se é uma colisão com a bola ou com as paredes
        if self.ball in col.objects:
            col.resolve()

            y_ball = self.ball.pos_cm.y
            y_pong = self.pong.pos_cm.y
            delta_y = y_ball - y_pong
            delta_vel = Vector(0, delta_y * 10)

            # Edita a velocidade
            vel = self.ball.vel_cm
            vel += delta_vel
            if abs(vel.x) > abs(0.2 * vel.y):
                vel *= self.ball.vel_cm.norm() / vel.norm()
                self.ball.vel_cm = vel

    def loose(self):
        '''Chamado quando o usuário perde a fase'''

        self.world.stop()
        game_over()

    def next(self):
        '''Chama a próxima fase'''

        self.world.stop()
        new = Pong(**self.next_params)
        new.run()

    #===========================================================================
    # API
    #===========================================================================
    def run(self):
        '''Inicia o jogo'''

        self.world.run()

def game_over():
    '''Executed when the game finishes'''

    Sx, Sy = 5, 2
    world = World(background=(255, 0, 0), gravity=10)
    letters = add_word('game over', world, scale=5, pos=(-220, 50))
    for l in letters:
        l.omega_cm = uniform(-0.1, 0.1)
        l.vel_cm += uniform(-Sx, Sx), uniform(-Sy, Sy)
        l.inertia *= 20
    world.run()

if __name__ == '__main__':
    Pong().run()

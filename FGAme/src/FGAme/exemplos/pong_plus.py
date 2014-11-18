#-*- coding: utf8 -*-
from FGAme import *
from random import uniform, choice, random
from math import pi

class Pong(World):
    def __init__(self, **kwds):
        # Inicializa o mundo
        H, W = self.screen_height / 2, self.screen_width / 2
        super(Pong, self).__init__(rest_coeff=0.9, gravity=self.gravity)
        self.make_bounds(-W + 10, 2 * W, -H + 10, H - 10, delta=400)
        self.listen('frame-enter', self.check_fail)
        self.listen('frame-enter', self.update_time)
        self.listen('frame-enter', self.accelerate_ball)
        self.listen('long-press', 'up', self.move_up)
        self.listen('long-press', 'down', self.move_down)

        # Cria a raquete
        Y = self.pong_height
        X = self.pong_width
        self.pong = pong = Poly([(0, 0), (0, Y), (-X / 3, Y),
                                 (-X, 0.66 * Y), (-X, 0.33 * Y), (-X / 3, 0)])
        pong.make_static('angular')
        pong.move((350, -Y / 2))
        pong.listen('collision', self.pong_collision)
        pong.external_force = \
            lambda t:-10000 * Vector(pong.pos_cm.x - self.pong_x, 0)
        pong.damping = 3
        self.pong_x = self.pong.pos_cm.x

        # Cria a barra de tempo
        self.timebar = AABB(shape=(20, 20), pos_cm=(W - 10, -H + 20),
                            color=(255, 225, 0))

        # Adiciona objetos
        self.ball = self.new_ball()
        self.add([self.pong, self.ball])
        self.add(self.timebar, layer=1, has_collision=False)
        self.obstacle = []
        for i in range(self.obstacle_N):
            new = self.new_obstacle()
            self.obstacle.append(new)
            self.add(new)

        # Define amplitude de movimento do pong
        self.max_pong_y = H - self.pong_height / 2 - 10
        self.min_pong_y = -self.max_pong_y

        # Desenha pontos de hit acinzentados
        self.hits = 0
        for i in range(self.max_hits):
            self.make_hit_mark(i, self.hits_bg)

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
    obstacle_N = 20
    obstacle_sides = 4
    obstacle_size = 30
    obstacle_color = (50, 50, 100)
    obstacle_dynamic = True

    # Cores
    hits_bg = (150, 150, 150)
    gravity = 0
    next_params = {}

    #===========================================================================
    # Criação e inicialização de objetos
    #===========================================================================
    def new_ball(self):
        '''Inicializa o a bola'''

        ball = Poly.regular(self.ball_sides, self.ball_size, color='red', density=1)
        ball.inertia *= self.inertia_multiplier
        V = self.ball_speed
        speed = -V, choice([-1, 1]) * uniform(0.25 * V, 2 * V)
        ball.boost(speed)
        return ball

    def new_obstacle(self):
        '''Cria um objeto aleatório que fica no meio da tela'''

        # Cria obstáculo
        obj = Poly.regular(self.obstacle_sides, self.obstacle_size,
                           color=self.obstacle_color, density=1)
        obj.scale(uniform(0.75, 2))
        obj.rotate(uniform(0, 2 * pi))
        obj.inertia *= self.inertia_multiplier
        if not self.obstacle_dynamic:
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
        hit = Circle(self.hit_size, pos_cm=(pos_x, pos_y), color=color)
        self.add(hit, layer=1, has_collision=False)

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

        self.timebar.ymax = ymax = self.time * 20 - self.screen_height / 2 + 20
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
            self.remove(self.ball)
            self.ball = self.new_ball()
            self.add(self.ball)

        for i, obj in enumerate(self.obstacle):
            if obj.pos_cm.x > self.screen_width / 2:
                self.hit_increment()
                self.remove(obj)
                del self.obstacle[i]
                break

    def hit_increment(self):
        '''Incrementa os hit counts'''
        # Testa derrota
        if self.hits >= self.max_hits - 1:
            self.loose()

        # Incrementa o número de hits
        hit = self.make_hit_mark(self.hits)
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

        self.stop()
        game_over()

    def next(self):
        '''Chama a próxima fase'''

        self.stop()
        new = Pong(**self.next_params)
        new.run()

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

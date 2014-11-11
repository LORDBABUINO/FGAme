# -*- coding: utf8 -*-
from __future__ import print_function

from FGAme import *
from random import uniform, choice

def random_color():
    return tuple(int(uniform(0, 255)) for i in range(3))

# Inicializa o mundo
world = World(rest_coeff=1.0)
world.make_bounds(-390, 600, -290, 290, delta=400)
fundo = AABB((550, 599, -289, 289))
fundo.pause()
world.add_object(fundo)
runner = Runner(world)
PONTOS = 0

# Bola
MAXSPEED = 800
class Ball(Circle):
    def post_update(self, t, dt):
        if self.vel_cm.norm() > MAXSPEED:
            self.vel_cm = self.vel_cm.normalized() * MAXSPEED

SPEED = 600
vel = Vector2D(-SPEED, choice([1, -1]) * uniform(SPEED / 2, SPEED))
bola = Ball(radius=40, vel_cm=vel, color=random_color(), mass=1e-6)
bola.scale(2.0)
world.add_object(bola)

# Raquete
class Raquete(AABB):
    def avoid_superposition_aabb(self, other, dt):
        '''Evita a superposição das caixas de contorno AABB'''

        deltay = shadow_y(self, other)
        n = 1 if other.ymin < self.ymin else -1
        self.move((0, n * deltay))

    def draw(self, screen):
        self.draw_aabb(screen, fill=True)

pos = Vector2D(300, 100)
raquete = Raquete(pos_cm=pos, shape=(15, 70), vel_cm=(0, 0), color=random_color(), mass=1e9)
raquete.is_dynamic = True
world.add_object(raquete)
raquete.scale(2.0)

# Registra callbacks de interação com o usuário
def setpos(x, y):
    x_, y_ = raquete.pos_cm
    raquete.set_position((x_, y))

runner.register_mouse_motion(setpos)

# Registra callbacks de colisão
def pong(col):
    y_bola = bola.pos_cm.y
    y_raquete = raquete.pos_cm.y
    delta_y = y_bola - y_raquete
    delta_vel = Vector2D(0, delta_y * 10)

    # Edita a velocidade
    vel = bola.vel_cm
    vel += delta_vel
    if abs(vel.x) > abs(0.2 * vel.y):
        vel *= bola.vel_cm.norm() / vel.norm()
        bola.vel_cm = vel

def make_pts(col):
    global PONTOS
    PONTOS += 1

    pos_x = 20 * PONTOS
    pos_y = 360

    mark = Circle(5, (pos_x - 390, 270), color='red')
    world.add_object(mark, layer=1, has_collision=False)

    if PONTOS >= 5:
        print('Perdeu, playboy!')
        raise SystemExit

world.register_collision_callback(pong, raquete, bola)
world.register_collision_callback(make_pts, bola, fundo)

# Inicia a simulação
runner.run()

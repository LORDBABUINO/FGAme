from FGAme import *

set_backend('pyglet')

world = World()
p = Poly.regular(4, 100, world=world, omega_cm=2, adamping=0.1)
p.external_torque = lambda t: - p.inertia * p.theta_cm
world.run()


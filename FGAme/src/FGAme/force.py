#-*- coding: utf8 -*-
'''
Created on 19/11/2014

@author: chips
'''
from FGAme.mathutils import *
import numpy as np

class ForceFunc(object):
    def __init__(self, func):
        self._funcs = []

    def __call__(self, t):
        F = VectorM(0, 0)
        for func in self._funcs:
            res = func(t)
            F.x += res[0]
            F.y += res[1]
        return F

    def __add__(self, other):
        if isinstance(other, ForceFunc):
            self._funcs.extend(other._funcs)
        else:
            self._funcs.append(other)

class SingleForce(object):
    '''Implementa uma força simples aplicada a um objeto.
    
    O modo 'mode' possui o mesmo significado que na classe PairForce().'''

    def __init__(self, obj, func, mode='time'):
        self._obj = obj
        self._func = func
        self._mode = mode

        # Converte func para a assinatura func(t) -> F
        if mode == 'time':
            self._func_ready = func
        elif mode == 'none':
            self._func_ready = lambda t: func()
        elif mode == 'objects':
            self._func_ready = lambda t: func(obj)
        elif mode == 'all':
            self._func_ready = lambda t: func(obj, t)
        elif mode == 'positions':
            pos = obj._pos_cm
            def new_func(t):
                assert pos is obj._pos_cm
                return func(pos)
            self._func_ready = new_func
        else:
            raise ValueError('invalid value for fargs: %r' % fargs)

    obj = property(lambda x: x._obj)
    func = property(lambda x: x._func)
    mode = property(lambda x: x._mode)

class SingleConservativeForce(SingleForce):
    '''Força conservativa que atua em um único objeto.
    
    Recebe o elemento, a força e o potencial como argumentos'''

    def __init__(self, obj, force, U):
        super(SingleConservativeForce, self).__init__(obj, force, 'positions')
        self._U = U

    def totalE(self):
        '''Energia total do par de partículas'''

        return self.obj.kineticE + self.potentialE()

    def kineticE(self):
        '''Energia cinética do par de partículas'''

        return self.obj.kineticE

    def potentialE(self):
        '''Energia potencial do par de partículas'''

        return self.U(self.obj._pos_cm)

    U = property(lambda x: x._U)

class GravitySF(SingleConservativeForce):
    '''Implementa uma força de gravitacional produzida por um objeto de massa M
    fixo na posição r0.
    
    O parâmetro de suavização epsilon possui o mesmo significado que em 
    GravityF'''

    def __init__(self, obj, G, M=None, epsilon=0, r0=(0, 0)):
        if M is None:
            M = obj.mass
        M = self._M = float(M)
        self._epsilon = float(epsilon)
        self._G = float(G)
        r0 = self._r0 = Vector(*r0)

        def F(R):
            R = R - r0
            r = R.norm()
            r3 = (r + epsilon) ** 2 * r
            R *= G * obj._mass * M / r3
            return R

        def U(R):
            R = (R - r0).norm()
            return -self._G * obj._mass * M / (R + self._epsilon)

        super(GravitySF, self).__init__(obj, F, U)

class PairForce(object):
    '''
    Força que opera em um par de partículas respeitando a lei de ação e reação.
    
    Parameters
    ----------
    
    A, B : Object instances
        Objetos em que a força atua
    func : callable
        Uma função que retorna o vetor com a força resultante. A assinatura da
        função depende do último argumento `fargs`
    mode : str
        Existem quatro possibilidades. Cada um assume uma assinatura específica.
            'none':
                func() -> F
            'time':
                func(t) -> F
            'objects':
                func(A, B) -> F
            'positions':
                func(A.pos_cm, B.pos_cm) -> F
            'all':
                func(A, B, t) -> F
        O valor padrão é 'time', que corresponde à convenção empregada pelo
        sistema do obj.external_force da classe Object.

    '''
    def __init__(self, A, B, func, mode='time'):
        self._A = A
        self._B = B
        self._func = func
        self._mode = mode
        self._cacheF = None

        # Converte func para a assinatura func(t) -> F
        if mode == 'time':
            self._func_ready = func
        elif mode == 'none':
            self._func_ready = lambda t: func()
        elif mode == 'objects':
            self._func_ready = lambda t: func(A, B)
        elif mode == 'all':
            self._func_ready = lambda t: func(A, B, t)
        elif mode == 'positions':
            A_pos, B_pos = A._pos_cm, B._pos_cm
            def new_func(t):
                assert A_pos is A._pos_cm and B_pos is B._pos_cm
                return func(A_pos, B_pos)
            self._func_ready = new_func
        else:
            raise ValueError('invalid value for fargs: %r' % fargs)

    # Atributos somente para leitura
    A = property(lambda x: x._A)
    B = property(lambda x: x._B)
    func = property(lambda x: x._func)
    mode = property(lambda x: x._mode)

    def force_A(self, t):
        '''Função que calcula a força sobre o objeto A no instante t'''

        if self._cacheF is None:
            res = self._func_ready(t)
            self._cacheF = -res
            return res
        else:
            res = self._cacheF
            self._cacheF = None
            return res

    def force_B(self, t):
        '''Função que calcula a força sobre o objeto B no instante t'''

        if self._cacheF is None:
            res = self._func_ready(t)
            self._cacheF = res
            return -res
        else:
            res = self._cacheF
            self._cacheF = None
            return res

    def accel_A(self, t):
        '''Função que calcula a aceleração sobre o objeto A no instante t'''

        return self.force_A(t) / self._A._mass

    def accel_B(self, t):
        '''Função que calcula a aceleração sobre o objeto B no instante t'''

        return self.force_A(t) / self._A._mass

    def __iter__(self):
        yield self.force_A
        yield self.force_B

    def forces(self):
        '''Itera sobre as funções [force_A, force_B]'''

        yield self.force_A
        yield self.force_B

    def accels(self):
        '''Itera sobre as acelerações [accel_A, accel_B]'''

        yield self.accel_A
        yield self.accel_B

class PairConservativeForce(PairForce):
    '''
    Uma força que opera em um par de partículas e possui uma energia potencial
    associada.
    
    Esta classe é iniciada a partir de uma função force(rA, rB) e de um 
    potencial U(rA, rB). 
    '''
    def __init__(self, A, B, force, U):
        super(PairConservativeForce, self).__init__(A, B, force, 'positions')
        self._U = U

    def totalE(self):
        '''Energia total do par de partículas'''

        return self.A.kineticE + self.B.kineticE + self.potentialE()

    def kineticE(self):
        '''Energia cinética do par de partículas'''

        return self.A.kineticE + self.B.kineticE

    def potentialE(self):
        '''Energia potencial do par de partículas'''

        return self.U(self.A._pos_cm, self.B._pos_cm)

    U = property(lambda x: x._U)

class SpringF(PairConservativeForce):
    '''
    Liga as duas partículas por uma força de Hooke com uma dada constante de
    mola e uma certa separação de equilíbrio delta.
    
    A constante de mola pode ser anisotrópica. Neste caso, deve ser especificado
    uma tupla (kx, ky) ou (kx, ky, kxy) com cada um dos termos no potencial:
        
        U_AB = kx * dx**2 / 2 + ky * dy**2 /2 + kxy * dx * dy
    
    Os termos dx e dy são as componentes do vetor rA - rB - delta.  
    '''
    def __init__(self, A, B, k, delta=(0, 0)):
        kxy = 0
        dx, dy = delta = self._delta = Vector(*delta)

        try:  # Caso isotrópico
            kx = ky = k = self._k = float(k)
        except TypeError:  # Caso anisotrópico
            k = self._k = tuple(map(float, k))
            if len(k) == 2:
                kx, ky = k
            else:
                kx, ky, kxy = k

        # Define forças e potenciais
        def F(rA, rB):
            Dx = rB._x - rA._x + dx
            Dy = rB._y - rA._y + dy
            return Vector(kx * Dx + kxy * Dy, +ky * Dy + kxy * Dx)

        def U(rA, rB):
            Dx = rB._x - rA._x + dx
            Dy = rB._y - rA._y + dy
            return (kx * Dx ** 2 + ky * Dy ** 2 + 2 * kxy * Dx * Dy) / 2

        super(SpringF, self).__init__(A, B, F, U)

    k = property(lambda x: x._k)
    delta = property(lambda x: x._delta)

class GravityF(PairConservativeForce):
    '''
    Implementa a força de gravidade "amaciada" com um parâmetro epsilon.
    
    A energia potencial desta força é dada por
    
        U(rA, rB) = -G mA mB / (|rB - rA| + e)
        
    O parâmetro de amaciamento pode ser necessário para melhorar a estabilidade
    numérica caso as duas posições rA e rB se aproximem muito. O valor padrão
    é zero e o usuário deve ponderar sobre valores adequados caso a caso. Na 
    prática epsilon limita o valor máximo que a força gravitacional pode
    assumir.
    '''

    def __init__(self, A, B, G, epsilon=0):
        self._G = G = float(G)
        self._epsilon = epsilon = float(epsilon)

        def F(Ra, Rb):
            R = Rb - Ra
            r = R.norm()
            r3 = (r + epsilon) ** 2 * r
            R *= G * A._mass * B._mass / r3
            return R

        def U(Ra, Rb):
            R = (Ra - Rb).norm()
            return -self._G * B._mass * A._mass / (R + self._epsilon)

        super(GravityF, self).__init__(A, B, F, U)

    G = property(lambda x: x._G)
    epsilon = property(lambda x: x._epsilon)


class GravityPool(object):
    def __init__(self, objects):
        self.objects = list(objects)

    def get_force(self, obj, mutable=True):
        pass

    def get_all_forces(self, mutable=True):
        return [ self.get_force(obj, mutable) for obj in self.objects ]

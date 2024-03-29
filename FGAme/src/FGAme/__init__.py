#-*- coding: utf8 -*-
'''
========
Tutorial
========

Exemplo básico
==============

Este tutorial explica como utilizar a FGAme para a criação de jogos ou
simulações de física simples. A FGAme é um motor de jogos com ênfase na
simulação de física. Todos os objetos, portanto, possuem propriedades físicas
bem definidas como massa, momento de inércia, velocidade, etc. A simulação da
física é feita, em grande parte, de modo automático.

O primeiro passo é definir o palco que os objetos habitarão. Isto pode ser feito
criando um objeto da classe World(). 

>>> world = World()

A partir daí, podemos criar objetos e inserí-los na simulação

>>> obj1 = Circle(50)
>>> obj2 = Circle(50, color='red')
>>> world.add([obj1, obj2])

Para modificar as propriedades físicas dos objetos basta modificar diretamente 
os atributos correspondentes. Para uma lista completa de atributos, consulte
o módulo ?Objects.

>>> obj1.mass = 10
>>> obj2.mass = 20
>>> obj1.pos_cm = (150, 50)
>>> obj1.vel_cm = (-100, 0)

As variáveis dinâmicas podem ser modificadas diretamente, mas sempre que
possível, devemos utilizar os  métodos que realizam os deslocamentos relativos
(ex.: .move(), .boost(), etc). Estes métodos são mais eficientes.

+----------+-----------+---------------+-------------------------------+---------+
| Variável | Escrita   | Deslocamentos | Descrição                     | Unidade |
+==========+===========+===============+===============================+=========+
| pos_cm   | set_pos   | move          | Posição do centro de massa    | px      |
+----------+-----------+---------------+-------------------------------+---------+
| vel_cm   | set_vel   | boost         | Velocidade do centro de massa | px/s    |
+----------+-----------+---------------+-------------------------------+---------+
| theta_cm | set_theta | rotate        | Ângulo de rotação             | rad     |
+----------+-----------+---------------+-------------------------------+---------+
| omega_cm | set_omega | aboost        | Velocidade angular            | rad/s   |
+----------+-----------+---------------+-------------------------------+---------+

Aplicamos uma operação de `.move()` e movê-lo com relação à posição anterior.
Veja como fica a posiição final do objeto.

>>> obj1.move((150, 0)) # deslocamento com relação à posição inicial
>>> obj1.pos_cm
Vector(300, 50)

Para iniciar a simulação, basta chamar o comando

>>> world.run() # doctest: +SKIP
    

Objetos dinâmicos
=================

Apesar do FGAme não fazer uma distinção explícita durante a criação, os objetos
no mundo podem ser do tipo dinâmicos, cinemáticos ou estáticos. Todos eles
participam das colisões normalmente, mas a resposta física pode ser diferente em
cada caso. Os objetos dinâmicos se movimentam na tela e respondem às forças
externas e de colisão. Os objetos cinemáticos se movimentam (usualmente em
movimento retilíneo uniforme), mas não sofrem a ação de nenhuma força. Já os
objetos estáticos permanecem parados e não respondem a forças.

A diferenciação é feita apenas pelo valor das massas e das velocidades. 
Convertemos um objeto em cinemático atribuindo um valor infinito para a massa. 
Um objeto será estático se tanto a massa quanto a velocidade forem nulas.

>>> obj2.mass = 'inf' # automaticamente se torna estático pois a velocidade é nula

O FGAme utiliza esta informação para acelerar os cálculos de detecção de colisão
e resolução de forças. As propriedades dinâmicas/estáticas dos objetos, no 
entanto são inteiramente transparentes ao usuário.

Vale observar que a condição de dinâmico vs. estático pode ser atribuída 
independentemente para as variáveis lineares e angulares. No segundo caso, o 
controle é feito pelo valor do momento de inércia no atributo `.inertia` do 
objeto. Para transformar um objeto dinâmico em inteiramente estático, seria 
necessário fazer a sequência de operações

>>> obj2.mass = 'inf'
>>> obj2.inertia = 'inf'
>>> obj2.vel_cm *= 0
>>> obj2.omega_cm *= 0

De modo mais simples, podemos fazer todas as operações de uma vez utilizando os
métodos `.make_static()` (ou kinematic/dynamic) para controlar as propriedades
dinâmicas do objeto.

>>> obj2.make_static()

Já os métodos `.is_static()` (ou kinematic/dynamic) permitem investigar se um
determinado objeto satisfaz a alugma destas propriedades.

>>> obj2.is_dynamic()
False
>>> obj2.is_static()
True

Lembramos que as colisões são calculadas apenas se um dos objetos envolvidos for
dinâmico. Deste modo, quando dois objetos cinemáticos ou um objeto estático
e um cinemático se encontram, nenhuma força é aplicada e eles simplemente 
atravessam um pelo outro. 

Forças básicas
==============

Além das forças arbitrárias que podem atuar em qualquer objeto e dos impulsos
associados às colisões, existem algumas forças que podem ser definidas 
globalmente no objeto World(). Trata-se da força da gravidade e das forças 
viscosas para as velocidades lineares e angulares. 

Na realidade, não definimos as forças diretamente, mas sim as acelerações que
elas provocam em cada objeto. São as constantes `gravity`, `damping` e
`adamping`. As forças são criadas a partir da fórmula
    
    F = obj.mass * (gravity - obj.vel_cm * damping)
    
E o torque é gerado por

    tau = -obj.inertia * adamping *  obj.omega_cm
    
Estas constantes podem ser definidas globalmente no objeto mundo ou
individualmente. Deste modo, é possível que algum objeto possua uma gravidade
diferente do resto do mundo. O mesmo se aplica às forças de amortecimento.
 
>>> world.gravity = (0, -50)
>>> world.adamping = 0.1

Todos objetos que não definirem explicitamente o valor destas constantes
assumirão os valores definidos no mundo no qual estão inseridos. Acrescentamos
um terceiro objeto com um valor de gravidade diferente do resto do mundo, para
demonstrar este conceito.

>>> obj3 = Circle(20, (0, -100), gravity=(20, 50), world=world, color='blue')

(Obs.: se o parâmetro world for fornecido, o objeto é adicionado 
automaticamente durante a criação) 

Interação com o usuário
=======================

Até agora vimos apenas como controlar os parâmetros de simulação física. É
lógico que em um jogo deve ser existir alguma forma de interação com o usuário.
Na FGAme, esta interação é controlada a partir da noção de eventos e callbacks.
É possível registrar funções que são acionadas sempre que um determinado evento
acontecer. Eventos podem ser disparados pelo usuário (ex.: apertar uma tecla),
ou pela simulação (ex.: ocorrência de uma colisão).

Digamos que a simulação deva pausar ou despausar sempre que a tecla de espaço 
for apertada. Neste caso, devemos ligar o evento "apertou a tecla espaço" 
com a função `.toggle_pause()` do mundo, que alterna o estado de pausa da 
simulação.

>>> world.listen('key-down', 'space', world.toggle_pause)

A tabela abaixo mostra os eventos mais comuns e a assinatura das funções de 
callback

+----------------+-------------+---------------------------------------------------+
| Evento         | Argumento   | Descrição                                         |
+================+=============+===================================================+
| key-down       | tecla       | Chamado no frame que uma tecla é pressionada.     | 
|                |             | O argumento pode ser um objeto 'tecla', que       |
|                |             | depende do back end utilizado ou uma string,      |
|                |             | que é portável para todos back ends.              |
|                |             |                                                   |
|                |             | A string corresponde à tecla escolhida. Teclas    |
|                |             | especiais podem ser acessadas pelos seus nomes    |
|                |             | como em 'space', 'up', 'down', etc.               |
|                |             |                                                   |
|                |             | Os callbacks do tipo 'key-down' são funções que   |
|                |             | não recebem nenhum argumento.                     |
+----------------+-------------+---------------------------------------------------+
| key-up         | tecla       | Como em 'key-down', mas é executado no frame em   |
|                |             | que a tecla é liberada pelo usuário.              |
+----------------+-------------+---------------------------------------------------+
| long-press     | tecla       | Semelhante aos anteriores, mas é executado em     |
|                |             | *todos* os frames em que a tecla se mantiver      |
|                |             | pressionada.                                      |
+----------------+-------------+---------------------------------------------------+
| mouse-motion   | nenhum      | Executado sempre que o ponteiro do mouse estiver  |
|                |             | presente na tela.                                 |
|                |             |                                                   |
|                |             | O callback é uma função que recebe um vetor com a |
|                |             | posição do mouse como primeiro argumento.         |
+----------------+-------------+---------------------------------------------------+
| mouse-click    | botão       | Como 'mouse-motion', mas só é executada após o    | 
|                |             | clique. Deve ser registrada com 'left', 'right'   |
|                |             | 'middle' correspondendo a um dos 3 tipos de botão |
|                |             | do mouse.                                         |
|                |             |                                                   |
|                |             | O callback recebe apeans a posição do ponteiro    |
|                |             | como primeiro argumento.                          |
+----------------+-------------+---------------------------------------------------+

Simulação simples
=================

Uma simulação de física pode ser criada facilmente adicionando objetos à uma
instância daclasse World(). O jeito mais recomendado, no entanto, é criar uma
subclasse pois isto incentiva o código a ficar mais organizado. No exemplo
abaixo, montamos um sistema "auto-gravitante" onde as duas massas estão presas
entre si por molas.


>>> class Gravity(World):
...     def __init__(self):
...         # Chamamos o __init__ da classe pai
...         super(Gravity, self).__init__() 
...
...         # Criamos dois objetos
...         A = Circle(20, pos_cm=(100, 0), vel_cm=(100, 300), color='red')
...         B = Circle(20, pos_cm=(-100, 0), vel_cm=(-100, -300))  
...         self.A, self.B = A, B
...         self.add([A, B])
...
...         # Definimos a força de interação entre ambos
...         K = self.K = A.mass
...         self.A.external_force = lambda t: -K * (A.pos_cm - B.pos_cm)
...         self.B.external_force = lambda t: -K * (B.pos_cm - A.pos_cm) 


Agora que temos uma classe mundo definida, basta iniciá-la com o comando

>>> if __name__ == '__main__':
...     Gravity().run()


==========
Referência
==========

Objetos
=======

.. automodule:: FGAme.objects


Classe mundo e aplicações
=========================

.. automodule:: FGAme.world


Colisões
========

.. automodule:: FGAme.collision


Funções matemáticas
===================

.. automodule:: FGAme.mathutils


Tópicos avançados
=================

Anatomia de uma colisão
=======================



Loop principal
==============

'''
from __future__ import absolute_import

#===============================================================================
# Importa pacotes
#===============================================================================
from . import math
from . import draw
from .core import *
from .physics import *
from .app import *

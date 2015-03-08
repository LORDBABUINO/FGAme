=====
FGAme
=====

FGAme é um motor de jogos 2D para Python utilizado na aula de introdução à 
física de jogos. A FGAme tem como objetivos principais a simplicidade e 
modularidade: queremos desenvolver jogos rapidamente e conseguir trocar qualquer 
aspecto da simulação de física de maneira relativamente simples. Trata-se de
um motor de jogos didático cujo maior objetivo é o uso em sala de aula. 

Este não é (e provavelmente nunca será) um motor de alto desempenho. Ainda que
se tenha dado alguma atenção à otimização, esta não é uma prioridade do código.
É lógico que computadores modernos são extremamente poderosos e, apesar das 
limitações desta biblioteca, ainda assim podem ser capazes de simular algumas 
centenas de polígonos e criar jogos interessantes baseados em física.

O foco da FGAme está ná física e não na apresentação gráfica. Espere um motor 
de jogos bastante limitado no segundo quesito, mas relativamente versátil e 
muito simples de utilizar no primeiro.

Instalação
==========

A engine é capaz de rodar em diversas plataformas. A FGAme funciona tanto em 
Python2 quanto em Python3 e utiliza algumas extensões escritas em Cython (que 
são traduzidas para C e posteriormente compiladas). Além disto, é necessário
instalar pelo menos um backend entre os suportados: pygame ou sdl2 (e 
futuramente kivy e possivelmente PyQT5 e pyglet). Recomendamos utilizar Python3
e pygame como uma opção inicial e os guias abaixo discutem como realizar este
tipo de instalação.

Linux
-----

Ubuntu
......

(Alguém confirme pois não utilizo o Ubuntu, e sim o Archlinux. Provavelmente
o nome dos pacotes está errado.)
No Ubuntu e similares, basta utilizar o comando apt-get para instalar as 
dependências necessárias. Depois instale a biblioteca utilizando o PIP. Basta
rodar o comando abaixo no terminal e esperar a instalação terminar::

  $ sudo apt-get install python3-pygame python3-pip cython

Se quiser instalar algum dos outros backends, também execute o comando 
apropriado::

  $ sudo apt-get install python3-kivy
  $ sudo apt-get install python3-sdl2

O FGAme está presente no PIP e pode ser instalado simplesmente executando

  $ sudo pip3 install FGAme

O PIP se encarrega de baixar, compilar e instalar a última versão disponível.

Archlinux
.........

Alguns dos pacotes necessários estão nos repositórios principais e alguns estão
disponíveis apenas no AUR. Certifique-se que a versão desejada do PIP e do 
Cython estão instaladas 

  # pacman -S python-pip cython
  
para Python 3 ou

  # pacman -S python2-pip cython
  
para Python 2.

O pygame está disponível nos repositórios principais apenas para Python2 sob o 
nome de ``python2-pygame``. A versão de desenvolvimento do Pygame com suporte 
para Python3 está no pacote ``python-pygame-hg`` do AUR.

Finalmente, execute o PIP para compilar e instalar a FGAme

   # pip install FGAme

(ou utilize o pip2, para Python2).

Windows
-------

(Algum usuário de Windows confirme, pois não tenho Windows e esse guia foi 
feito no achômetro.)

Os usuários de Windows devem baixar a versão de Python desejada junto com os 
pacotes compilados para esta versão. Este guia fornece os endereços para o 
Python 3.4, mas o usuário pode instalar outra versão com mínimas modificações.
Baixe e instale os arquivos na ordem mesma ordem da lista indicada abaixo:

	* Python 3.4:
	* Pygame para Python3: 
	* PIP:
	* GCC:  
	* Cython:

Agora execute o PIP no terminal do Windows:

	# pip install FGAme 

Para abrir o terminal, pressione ``Win+R`` para abrir a caixa de executar 
programas e digite ``cmd``.  

Mac OS
------

Alguém com Mac pode ajudar aqui!

Android
-------

Provavelmente roda o usando o Pygame subset for android. Talvez precisamos de 
um guia mais detalhado que possa ser colocado aqui.

iOS
---

Ni puta idea! Supostamente pode ser instalado com o Kivy. É preciso terminar o
port e verificar como fazer o deploy para iOS. Alguém com experiência pode ajudar.


Orientação para estudantes
==========================

Qual plataforma escolher?
-------------------------







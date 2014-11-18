#-*- coding: utf8 -*-
from distutils.core import setup
import os

setup(name='FGAme',
      version='0.1a',
      description='A game engine for 2D physics',
      author='Fábio Macêdo Mendes',
      author_email='fabiomacedomendes@gmail.com',
      url='code.google.com/p/fgame',
      long_description=(
r'''A game engine for 2D physics. FGAme was developed for a course on computer 
games physics. Hence simplicity and ease to use were valued more than raw 
performance.

Main features:
  * AABB's, Circle and Convex Polygons collisions.
  * Backend agnostic (only Pygame is supported, for now).
'''),
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries',
          ],
      package_dir={'': 'src'},
      packages=['FGAme', 'FGAme.objects', 'FGAme.backends', 'FGAme.exemplos'],
)

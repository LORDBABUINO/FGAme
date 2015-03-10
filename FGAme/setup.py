#-*- coding: utf8 -*-
import os
from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

setup(name='FGAme',
      version='0.3a',
      description='A game engine for 2D physics',
      author='Fábio Macêdo Mendes',
      author_email='fabiomacedomendes@gmail.com',
      url='code.google.com/p/fgame',
      long_description=(
r'''A game engine for 2D physics. FGAme was developed for a course on computer 
games physics. Simplicity and ease to use were valued more than raw performance
and fancy graphics.

Main features:
  * AABB's, Circle and Convex Polygons collisions.
  * Backend agnostic (Pygame and sdl2 are supported, for now).
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
      packages=['FGAme', 'FGAme.app', 'FGAme.core', 'FGAme.draw', 
                'FGAme.extra', 'FGAme.math', 'FGAme.physics', 'FGAme.util'],

      cmdclass={"build_ext": build_ext},
      requires=[],

      ext_modules=[
          Extension("linalg_fast",
                    ["src/FGAme/math/linalg_fast.pyx"],
                    libraries=["m"],
                    include_dirs=['src/FGAme']),
      ],

)

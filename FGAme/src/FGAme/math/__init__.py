try:
    from .linalg_fast import *
except ImportError:
    from .linalg import *
    
from .util import *
from .vertices import *
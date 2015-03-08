import os

if __name__ == '__main__':
    for file in ['aabb_friction', 'adamp', 'gas_aabbs', 'embolo', 
                       'poly_simple', 'poly_simple2', 'gas_polys']:
        
        if os.system('python %s.py' % file) != 0:
            break
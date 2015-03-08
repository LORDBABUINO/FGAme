import os

if __name__ == '__main__':
    for file in ['raw_circles', 'raw_shapes']:
        
        if os.system('python %s.py' % file) != 0:
            break
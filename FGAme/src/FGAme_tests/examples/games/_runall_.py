import os

if __name__ == '__main__':
    for file in ['pong']:
        
        if os.system('python %s.py' % file) != 0:
            break
import os

if __name__ == '__main__':
    for dir in ['drawing', 'simulations', 'games']:
        os.chdir(dir)
        if os.system('python _runall_.py') != 0:
            break
        os.chdir('..')
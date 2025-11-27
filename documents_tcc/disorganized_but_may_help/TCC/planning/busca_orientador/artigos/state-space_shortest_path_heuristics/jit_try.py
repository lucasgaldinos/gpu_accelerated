import numba as nb
import numpy as np

k=0


class myClass(object):
    def __init__(self):
        self.k = 3

    def complicated(self,x):                 
        
        @nb.jit
        def _complicated(x, k):
            for a in x:
                b = a**2.+a**3.+k
            

                         
        y = _complicated(x, self.k)
        return y

if __name__ == '__main__':
    x = np.array([1,5,8])
    m = myClass()
    print(m.complicated(x))
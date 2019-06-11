class A:
    #def __init__(self):
     #   pass
    params = ('a', 'b', 'c')

class B(A):
    #def __init__(self, *args, **kwargs):
     #   A.__init__(self, *args, **kwargs)

    params = A.params + ('d', 'e',)

if __name__ == '__main__':
    x = A()
    y = B()
    print(x.params, y.params)

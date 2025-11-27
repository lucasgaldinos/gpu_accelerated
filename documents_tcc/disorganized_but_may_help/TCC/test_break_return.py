def fun(x):
    for i in range(1, 100):
        print(i)
        if i == x:
            break
    
    return i
    
t = fun(3)
print(t)
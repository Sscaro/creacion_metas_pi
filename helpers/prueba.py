import numpy as np

lista1 = [1,2,3,4,5,6]
lista2 = [0,1,2,3,5,8]
lista3 = [1,3,6,10,15,21]

array_2D = np.array([lista1,lista2,lista3])
print(array_2D[:,0:6:3])
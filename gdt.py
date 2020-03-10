'''
Module - gdt	version: 5.0
-----------------------------
Module for computation of chamfer distance transform of an image from a starting point
Default method considers periodic boundaries

Use: gdt.dist(array_input, seed, dist_type)
Where:
	- array_input: numpy binary array representing image (1 - foreground; 0 - background)
	- seed: tuple ((z), y, x) representing coordinates used as starting point for transformation
	- dist_type: distance metric used
		"city" = cityblock
		"chess" = chessboard
		"borges" = borgefors
		"quasi" = quasi-euclidean

Output: array where values represent distance (may be infinite)

----------------------------

Other functions from this module (see corresponding docstrings):
	gdt.form3d(): quick import of 3D images into required format
	gdt.optim(): used for restricting computation to the minimum region containing a list of points

For more information see docstrings for each function

'''

import numpy as np
from PIL import Image


def dist (array_input, seed, dist_type, periodic_boundaries = True):
	'''
	Returns distance transform of array_input using seed as starting point and using dist_type distance metric
	Periodic boundaries considered by default

	Input:
		- array_input: numpy binary array representing image (1 - foreground; 0 - background)
		- seed: tuple ((z), y, x) representing coordinates used as starting point for transformation")
		- dist_type: distance metric used:
			- "city" = cityblock
			- "chess" = chessboard
			- "borges" = borgefors
			- "quasi" = quasi-euclidean
	Output: array where values represent distance (may be infinite)
	'''
	if array_input.ndim == 2:
		return dist2d(array_input, seed, dist_type, periodic_boundaries)
	elif array_input.ndim == 3:
		return dist3d(array_input, seed, dist_type, periodic_boundaries)
	else:
		raise Exception ("Error: Incorrect array dimensions (only 2D or 3D)")

#end dist()



def dist2d (array_input, seed, dist_type, periodic_boundaries):

	array = np.where(array_input > 0, -1, -2)
	if array[seed] != -1:
		raise Exception ("Error: Chosen seed is not part of foreground")
	else:
		array[seed] = 0
		seed += (0,)
		lista_fuentes = [seed]

	while lista_fuentes != []:
		next_lista_fuentes = []
		if dist_type in ["borges", "quasi"]:
			order(lista_fuentes, 2)

		for fuente in lista_fuentes:
			if dist_type in ["chess", "borges", "quasi"]:
				lista_adyacentes = ady2d(fuente, array, ady=8)
			else:
				lista_adyacentes = ady2d(fuente, array)

			for index, casilla in enumerate(lista_adyacentes):
				if array[casilla] == -1:
					if dist_type in ["city", "chess"]:
						array[casilla] = fuente[2]+1
					elif dist_type == "borges":
						array[casilla] = fuente[2]+3+(index//4)
					elif dist_type == "quasi":
						array[casilla] = fuente[2]+5+(index//4)*2
					else:
						raise Exception ("Error: "+dist_type+" calculation method does not exist")
					next_lista_fuentes.append(casilla + (array[casilla],))

		lista_fuentes = next_lista_fuentes

	array = np.where(array == -1, np.inf, array)
	array = np.where(array == -2, np.inf, array)

	return array

#end dist2d()



def ady2d (position, array, ady=4):
	'''
	Returns list of adyacent positions to input position
		- ady: number of adyacency (4 or 8 adyacency)
	'''
	SY, SX = array.shape
	y, x, value = position
	lista_adyacentes = []
	lista_adyacentes.append(((y-1)%SY,(x)%SX))
	lista_adyacentes.append(((y+1)%SY,(x)%SX))
	lista_adyacentes.append(((y)%SY,(x-1)%SX))
	lista_adyacentes.append(((y)%SY,(x+1)%SX))

	if ady == 8:
		lista_adyacentes.append(((y-1)%SY,(x-1)%SX))
		lista_adyacentes.append(((y-1)%SY,(x+1)%SX))
		lista_adyacentes.append(((y+1)%SY,(x-1)%SX))
		lista_adyacentes.append(((y+1)%SY,(x+1)%SX))

	return lista_adyacentes

#end ady2d()



def optim2d (array_input, lista_posiciones):
	'''
	Returns array reduced to exactly fit list of coordinates
	Also modifies input lista_posiciones to contain corresponding coordinates for new array

	Input:
		- array_input: numpy int array representing image. Value 1 = foreground; 0 = background
		- lista_coordenadas: list containing lists of (y,x) coordinates
	'''
	ymax = max([posicion[0] for posicion in lista_posiciones])
	ymin = min([posicion[0] for posicion in lista_posiciones])
	xmax = max([posicion[1] for posicion in lista_posiciones])
	xmin = min([posicion[1] for posicion in lista_posiciones])

	nueva_lista_posiciones = []
	for posicion in lista_posiciones:
		nueva_lista_posiciones.append((posicion[0]-ymin, posicion[1]-xmin))
	lista_posiciones[:] = nueva_lista_posiciones

	return array_input[ymin:ymax+1, xmin:xmax+1]

#end optim2d



def order (lista,dim):
	lista.sort(key=lambda x: x[dim])
	return lista

#end order



def dist3d (array_input, seed, dist_type, periodic_boundaries):

	array = np.where(array_input > 0, -1, -2)
	if array[seed] != -1:
		raise Exception ("Error: Chosen seed is not part of foreground")
	else:
		array[seed] = 0
		seed += (0,)
		lista_fuentes = [seed]

	while lista_fuentes != []:
		next_lista_fuentes = []
		if dist_type in ["borges", "quasi"]:
			order(lista_fuentes, 3)

		for fuente in lista_fuentes:
			if dist_type in ["chess", "borges", "quasi"]:
				lista_adyacentes = ady3d(fuente, array, ady=26)
			else:
				lista_adyacentes = ady3d(fuente, array)

			for index, casilla in enumerate(lista_adyacentes):
				if array[casilla] == -1:

					if dist_type in ["city", "chess"]:
						array[casilla] = fuente[3]+1

					elif dist_type == "borges":
						if index < 6:
							array[casilla] = fuente[3]+3
						elif index < 18:
							array[casilla] = fuente[3]+4
						else:
							array[casilla] = fuente[3]+5

					elif dist_type == "quasi":
						if index < 6:
							array[casilla] = fuente[3]+10
						elif index < 18:
							array[casilla] = fuente[3]+14
						else:
							array[casilla] = fuente[3]+17

					else:
						raise Exception ("Error: "+dist_type+" calculation method does not exist")

					next_lista_fuentes.append(casilla + (array[casilla],))

		lista_fuentes = next_lista_fuentes

	array = np.where(array == -1, np.inf, array)
	array = np.where(array == -2, np.inf, array)

	return array

#end dist3d()



def ady3d (position, array, ady=6):
	'''
	Returns list of adyacent positions to input position
		- ady: number of adyacency (6 or 26 adyacency)
	'''
	SZ, SY, SX = array.shape
	z, y, x, value = position
	lista_adyacentes = []
	lista_adyacentes.append(((z-1)%SZ,(y)%SY,(x)%SX))
	lista_adyacentes.append(((z+1)%SZ,(y)%SY,(x)%SX))
	lista_adyacentes.append(((z)%SZ,(y-1)%SY,(x)%SX))
	lista_adyacentes.append(((z)%SZ,(y+1)%SY,(x)%SX))
	lista_adyacentes.append(((z)%SZ,(y)%SY,(x-1)%SX))
	lista_adyacentes.append(((z)%SZ,(y)%SY,(x+1)%SX))

	if ady == 26:

		lista_adyacentes.append(((z-1)%SZ,(y-1)%SY,(x)%SX))
		lista_adyacentes.append(((z-1)%SZ,(y+1)%SY,(x)%SX))
		lista_adyacentes.append(((z+1)%SZ,(y-1)%SY,(x)%SX))
		lista_adyacentes.append(((z+1)%SZ,(y+1)%SY,(x)%SX))
		lista_adyacentes.append(((z-1)%SZ,(y)%SY,(x-1)%SX))
		lista_adyacentes.append(((z-1)%SZ,(y)%SY,(x+1)%SX))
		lista_adyacentes.append(((z+1)%SZ,(y)%SY,(x-1)%SX))
		lista_adyacentes.append(((z+1)%SZ,(y)%SY,(x+1)%SX))
		lista_adyacentes.append(((z)%SZ,(y-1)%SY,(x-1)%SX))
		lista_adyacentes.append(((z)%SZ,(y-1)%SY,(x+1)%SX))
		lista_adyacentes.append(((z)%SZ,(y+1)%SY,(x-1)%SX))
		lista_adyacentes.append(((z)%SZ,(y+1)%SY,(x+1)%SX))

		lista_adyacentes.append(((z-1)%SZ,(y-1)%SY,(x-1)%SX))
		lista_adyacentes.append(((z-1)%SZ,(y-1)%SY,(x+1)%SX))
		lista_adyacentes.append(((z+1)%SZ,(y-1)%SY,(x+1)%SX))
		lista_adyacentes.append(((z+1)%SZ,(y-1)%SY,(x-1)%SX))
		lista_adyacentes.append(((z-1)%SZ,(y+1)%SY,(x+1)%SX))
		lista_adyacentes.append(((z-1)%SZ,(y+1)%SY,(x-1)%SX))
		lista_adyacentes.append(((z-1)%SZ,(y-1)%SY,(x+1)%SX))
		lista_adyacentes.append(((z-1)%SZ,(y-1)%SY,(x-1)%SX))

	return lista_adyacentes

#end ady2d()



def optim3d (array_input, lista_posiciones):
	'''
	Returns array reduced to exactly fit list of coordinates
	Also modifies input lista_posiciones to contain corresponding coordinates for new array

	Input:
		- array_input: numpy int array representing image. Value 1 = foreground; 0 = background
		- lista_coordenadas: list containing lists of (z,y,x) coordinates
	'''
	zmax = max([posicion[0] for posicion in lista_posiciones])
	zmin = min([posicion[0] for posicion in lista_posiciones])
	ymax = max([posicion[1] for posicion in lista_posiciones])
	ymin = min([posicion[1] for posicion in lista_posiciones])
	xmax = max([posicion[2] for posicion in lista_posiciones])
	xmin = min([posicion[2] for posicion in lista_posiciones])

	nueva_lista_posiciones = []
	for posicion in lista_posiciones:
		nueva_lista_posiciones.append((posicion[0]-zmin, posicion[1]-ymin, posicion[2]-xmin))
	lista_posiciones[:] = nueva_lista_posiciones

	return array_input[zmin:zmax+1, ymin:ymax+1, xmin:xmax+1]

#end optim2d



def form3d (numero, formato):
	'''
	Imports a pack of 2D images composing a 3D image and converts to required format for gdt.dist()

	Images need to be in the same directory and be called '0.png'...'n.png'
	They will be imported from 0 -> numero-1
	Input:
		- numero: number of z slices of image
		- formato: string of format name; e.g. '.png'
	//input call for path: path of directory where images are stored
	Output: Numpy array with required format for gdt.dist()
	'''
	ruta = input("Ruta de las imagenes: ")
	array = []
	for i in range(numero):
		imagen_temp = Image.open(ruta+"/"+str(i)+str(formato))
		imagen_temp = np.asarray(imagen_temp)
		imagen_temp = np.where(imagen_temp > 0, 0, 1)
		array.append(imagen_temp)
	return np.array(array)

#end form3d

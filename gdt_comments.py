'''
Module - gdt	version: 5.0
-----------------------------
Module for computation of chamfer distance transform of an array from a starting point (origin)
Default method considers periodic boundaries

Use: dist(array_input, origin, dist_type)
Where:
	- array_input: numpy binary array (1 - foreground; 0 - background)
	- origin: tuple (x, y, (z))) representing coordinates used as starting point for transformation
	- dist_type: distance metric used
		"city" = cityblock
		"chess" = chessboard
		"borges" = borgefors
		"quasi" = quasi-euclidean

Output: array where values represent distance (may be infinite)

----------------------------

Other functions from this module (see corresponding docstrings):
	form3d(): quick import of 3D images into required format
	optim(): used for restricting computation to the minimum region containing a list of points

For more information see docstrings for each function

'''

import numpy as np
from PIL import Image


def dist (array_input, origin, dist_type, periodic_boundaries = True):
	'''
	Returns distance transform of array_input using origin as starting point and using dist_type distance metric
	Periodic boundaries considered by default

	Input:
		- array_input: numpy binary array (1 - foreground; 0 - background)
		- origin: tuple (x, y, (z)) representing coordinates used as starting point for transformation")
		- dist_type: distance metric used:
			- "city" = cityblock
			- "chess" = chessboard
			- "borges" = borgefors
			- "quasi" = quasi-euclidean
	Output: array where values represent distance (may be infinite)
	'''
	if array_input.ndim == 2:
		return _dist2d(array_input, origin, dist_type, periodic_boundaries)
	elif array_input.ndim == 3:
		return _dist3d(array_input, origin, dist_type, periodic_boundaries)
	else:
		raise Exception ("Error: Incorrect array dimensions (only 2D or 3D)")

#end dist()



def _dist2d (array_input, origin, dist_type, periodic_boundaries):
	'''
	gdt works with an array where values:
		-1: unactualized foreground
		-2: background
	An origin must be foreground, and only foreground actualizable values (-1) will be modified
	Once a value is modified with its corresponding distance (which is > -1) its value won't change
	'''
	array = np.where(array_input > 0, -1, -2)
	if array[origin] != -1:
		raise Exception ("Error: Chosen origin is not part of foreground")
	else:
		array[origin] = 0
		origin += (0,)
		lista_fuentes = [origin]
	'''
	Fuente: (x, y, value) element of the array whose distance is expanded to adyacent elements in an iterative process
	Fuentes are stored in a list and iterations stop once list is empty
	'''
	while lista_fuentes != []:
		next_lista_fuentes = []
		if dist_type in ["borges", "quasi"]:
			_order(lista_fuentes, 2)	#These dist_types require sorting the list according to their distance value

		for fuente in lista_fuentes:
			if dist_type == "city":
				lista_adyacentes = _ady2d(fuente, array)
			else:
				lista_adyacentes = _ady2d(fuente, array, ady=8)
			#Only cityblock uses 4-adyacent expansion, all other methods use 8-adyacent

			for index, casilla in enumerate(lista_adyacentes):
				if array[casilla] == -1:
					if dist_type in ["city", "chess"]:
						array[casilla] = fuente[2]+1
					elif dist_type == "borges":
						array[casilla] = fuente[2]+3+(index//4)	#3 is added to the four 1st ady elements (4-adyacents), while 4 is added to four last (8-adyacents exclusive points)
					elif dist_type == "quasi":
						array[casilla] = fuente[2]+5+(index//4)*2 #Idem but +5 and +7
					else:
						raise Exception ("Error: "+dist_type+" calculation method does not exist")
					next_lista_fuentes.append(casilla + (array[casilla],))	#Values whose distance have been updated are added as next fuentes (including coordinates + distance_value)

		lista_fuentes = next_lista_fuentes

	array = np.where(array == -1, np.inf, array)
	array = np.where(array == -2, np.inf, array)
	#Values that have not been reached return inf distance, as well as background values

	return array

#end dist2d()



def _ady2d (position, array, ady=4):
	'''
	Returns list of adyacent positions to input position
		- ady: number of adyacency (4 or 8 adyacency)
	'''
	SX, SY = array.shape
	x, y, value = position
	lista_adyacentes = []
	lista_adyacentes.append(((x-1)%SX,(y)%SY))
	lista_adyacentes.append(((x+1)%SX,(y)%SY))
	lista_adyacentes.append(((x)%SX,(y-1)%SY))
	lista_adyacentes.append(((x)%SX,(y+1)%SY))
	#First 4 values added correspond to 4-adyacents

	if ady == 8:
		lista_adyacentes.append(((x-1)%SX,(y-1)%SY))
		lista_adyacentes.append(((x-1)%SX,(y+1)%SY))
		lista_adyacentes.append(((x+1)%SX,(y-1)%SY))
		lista_adyacentes.append(((x+1)%SX,(y+1)%SY))
		#Second 4 values added correspond to the extra 4 found in 8-adyacents

	return lista_adyacentes

#end ady2d()



def optim2d (array_input, lista_posiciones):
	'''
	Returns array reduced to exactly fit list of coordinates
	Also modifies input lista_posiciones to contain corresponding coordinates for new array

	Input:
		- array_input: numpy binary array (1 - foreground; 0 - background)
		- lista_coordenadas: list containing lists of (x,y) coordinates
	'''
	xmax = max([posicion[0] for posicion in lista_posiciones])
	xmin = min([posicion[0] for posicion in lista_posiciones])
	ymax = max([posicion[1] for posicion in lista_posiciones])
	ymin = min([posicion[1] for posicion in lista_posiciones])
	#maximum and minimum values for each coordinate

	nueva_lista_posiciones = []
	for posicion in lista_posiciones:
		nueva_lista_posiciones.append((posicion[0]-xmin, posicion[1]-ymin))
		#new coordinates in the reduced array correspond to previous coordinates - its minimum value
	lista_posiciones[:] = nueva_lista_posiciones
	#input list is modified in place -> replaced by new list

	return array_input[xmin:xmax+1, ymin:ymax+1]

#end optim2d



def _order (lista,dim):
	'''
	Function that orders a list by its dimth element
	'''
	lista.sort(key=lambda x: x[dim])
	return lista

#end order



def _dist3d (array_input, origin, dist_type, periodic_boundaries):

	#See comments for 2D method, most code is analogous
	array = np.where(array_input > 0, -1, -2)
	if array[origin] != -1:
		raise Exception ("Error: Chosen origin is not part of foreground")
	else:
		array[origin] = 0
		origin += (0,)
		lista_fuentes = [origin]

	while lista_fuentes != []:
		next_lista_fuentes = []
		if dist_type in ["borges", "quasi"]:
			_order(lista_fuentes, 3)

		for fuente in lista_fuentes:
			if dist_type in ["chess", "borges", "quasi"]:
				lista_adyacentes = _ady3d(fuente, array, ady=26)
			else:
				lista_adyacentes = _ady3d(fuente, array)

			for index, casilla in enumerate(lista_adyacentes):
				if array[casilla] == -1:

					if dist_type in ["city", "chess"]:
						array[casilla] = fuente[3]+1

					elif dist_type == "borges":
						'''
						In 3D borges and quasi different values are assigned to:
							1st-6th elements (single-displacement)
							7th-18th elements (double-displacement)
							19th - 26th elements (triple-displacement)
						'''
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



def _ady3d (position, array, ady=6):
	'''
	Returns list of adyacent positions to input position
		- ady: number of adyacency (6 or 26 adyacency)
	'''
	SX, SY, SZ = array.shape
	x, y, z, value = position
	lista_adyacentes = []
	lista_adyacentes.append(((x-1)%SX,(y)%SY,(z)%SZ))
	lista_adyacentes.append(((x+1)%SX,(y)%SY,(z)%SZ))
	lista_adyacentes.append(((x)%SX,(y-1)%SY,(z)%SZ))
	lista_adyacentes.append(((x)%SX,(y+1)%SY,(z)%SZ))
	lista_adyacentes.append(((x)%SX,(y)%SY,(z-1)%SZ))
	lista_adyacentes.append(((x)%SX,(y)%SY,(z+1)%SZ))
	#1st-6th elements: single-displacement

	if ady == 26:

		lista_adyacentes.append(((x-1)%SX,(y-1)%SY,(z)%SZ))
		lista_adyacentes.append(((x-1)%SX,(y+1)%SY,(z)%SZ))
		lista_adyacentes.append(((x+1)%SX,(y-1)%SY,(z)%SZ))
		lista_adyacentes.append(((x+1)%SX,(y+1)%SY,(z)%SZ))
		lista_adyacentes.append(((x-1)%SX,(y)%SY,(z-1)%SZ))
		lista_adyacentes.append(((x-1)%SX,(y)%SY,(z+1)%SZ))
		lista_adyacentes.append(((x+1)%SX,(y)%SY,(z-1)%SZ))
		lista_adyacentes.append(((x+1)%SX,(y)%SY,(z+1)%SZ))
		lista_adyacentes.append(((x)%SX,(y-1)%SY,(z-1)%SZ))
		lista_adyacentes.append(((x)%SX,(y-1)%SY,(z+1)%SZ))
		lista_adyacentes.append(((x)%SX,(y+1)%SY,(z-1)%SZ))
		lista_adyacentes.append(((x)%SX,(y+1)%SY,(z+1)%SZ))
		#6th-18th elements: double-displacement

		lista_adyacentes.append(((x-1)%SX,(y-1)%SY,(z-1)%SZ))
		lista_adyacentes.append(((x-1)%SX,(y-1)%SY,(z+1)%SZ))
		lista_adyacentes.append(((x+1)%SX,(y-1)%SY,(z+1)%SZ))
		lista_adyacentes.append(((x+1)%SX,(y-1)%SY,(z-1)%SZ))
		lista_adyacentes.append(((x-1)%SX,(y+1)%SY,(z+1)%SZ))
		lista_adyacentes.append(((x-1)%SX,(y+1)%SY,(z-1)%SZ))
		lista_adyacentes.append(((x-1)%SX,(y-1)%SY,(z+1)%SZ))
		lista_adyacentes.append(((x-1)%SX,(y-1)%SY,(z-1)%SZ))
		#18th-26th elements: triple-displacement

	return lista_adyacentes

#end ady3d()



def optim3d (array_input, lista_posiciones):
	'''
	Returns array reduced to exactly fit list of coordinates
	Also modifies input lista_posiciones to contain corresponding coordinates for new array

	Input:
		- array_input: numpy int array with values 1 = foreground; 0 = background
		- lista_coordenadas: list containing lists of (x,y,z) coordinates
	'''
	#See coments for optim2d(), analogous code
	xmax = max([posicion[0] for posicion in lista_posiciones])
	xmin = min([posicion[0] for posicion in lista_posiciones])
	ymax = max([posicion[1] for posicion in lista_posiciones])
	ymin = min([posicion[1] for posicion in lista_posiciones])
	zmax = max([posicion[2] for posicion in lista_posiciones])
	zmin = min([posicion[2] for posicion in lista_posiciones])

	nueva_lista_posiciones = []
	for posicion in lista_posiciones:
		nueva_lista_posiciones.append((posicion[0]-xmin, posicion[1]-ymin, posicion[2]-zmin))
	lista_posiciones[:] = nueva_lista_posiciones

	return array_input[xmin:xmax+1, ymin:ymax+1, zmin:zmax+1]

#end optim3d



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

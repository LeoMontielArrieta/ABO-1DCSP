"""
Dentro de esta versión se conforma a un nuevo bgmax antes de reiniciar la manada mediante la selección de los
mejores patrones de corte de la manada actual
"""
from timeit import timeit
from random import shuffle, random
import math
import matplotlib.pyplot as plt
import numpy as np
import heapq
from timeit import default_timer as timer
import pandas as pd


def obtenerlistacompletaitems(dict_items):
    """
    Función que permite obtener una lista ordenada con todos los ítems ordenados de menor a mayor
    :param dict_items:
    :return:
    """
    lista_items = []
    for clave in dict_items:
        for i in range(dict_items[clave]):
            lista_items.append(clave)
    return lista_items


def generacion_bufalos(num_bufalos, lista_items_completa, longitud_objeto):
    """
    Función que permite genera los búfalos
    :param num_bufalos:
    :param lista_items_completa:
    :param longitud_objeto:
    :return:
    """
    dict_bufalos = {}
    for i in range(num_bufalos):
        shuffle(lista_items_completa)
        copia_lista_items = lista_items_completa.copy()
        dict_bufalos.setdefault(i, [copia_lista_items, copia_lista_items, copia_lista_items])  #se establecen mb, wb y bpmax con la lista de ítems reordenada
        lista_arreglo_objetos, desper_total, obj_con_desper = obtenerdatosbufalo(dict_bufalos[i][1].copy(), longitud_objeto)  #Función que me obtiene los datos de cada búfalo
        dict_bufalos[i].append(len(lista_arreglo_objetos))  #agrega el número de objetos con base en el tamaño de la lista
        dict_bufalos[i].append(desper_total)
        dict_bufalos[i].append(obj_con_desper)
        dict_bufalos[i].append(lista_arreglo_objetos)
    return dict_bufalos


def buscar_bgmax(dict_bufalos):
    """
    Función que obtiene el bgmax de inicio que tenga menos desperdicio
    :param dict_bufalos:
    :return: bgmax
    """
    bgmax = dict_bufalos[0]
    for clave in dict_bufalos:
        if dict_bufalos[clave][4] < bgmax[4]:
            bgmax = dict_bufalos[clave].copy()
    return bgmax


def obtener_nuevo_mb_discretizado(mb_actual, wb_actual, bpmax,bgmax, lp1, lp2, lista_items_completa):
    """
    Función que obtiene el mb_nuevo de cada búfalo aplicando el ROV
    :param mb_actual:
    :param wb_actual:
    :param bpmax:
    :param bgmax:
    :param lp1:
    :param lp2:
    :return:
    """
    mb_nuevo = []
    for i in range(len(mb_actual)):
        mb_nuevo.append(mb_actual[i] + lp1 * (bgmax[i] - wb_actual[i]) + lp2 * (bpmax[i] - wb_actual[i]))
    mb_nuevo_ordenado = mb_nuevo.copy()
    mb_nuevo_entero = mb_nuevo.copy()
    mb_nuevo_ordenado.sort()
    lista_items_completa.sort()
    for i in range(len(mb_nuevo_ordenado)):
        index = mb_nuevo.index(mb_nuevo_ordenado[i])
        mb_nuevo[index] = "*"
        mb_nuevo_entero[index] = int(0)
        mb_nuevo_entero[index] = lista_items_completa[i]
    for elemento in mb_nuevo_entero:
        if elemento == 0:
            print("encontro")
    return mb_nuevo_entero


def obtener_nuevo_wb(wb_actual, mb_actual, lista_items_completa, landa):
    """
    Función que obtiene el nuevo wb de cada búfalo
    :param wb_actual:
    :param mb_actual:
    :param lista_items_completa:
    :param landa:
    :return: wb_nuevo
    """
    wb_nuevo = []
    for i in range(len(wb_actual)):
        wb_nuevo.append((wb_actual[i] + mb_actual[i]) / landa)
    wb_nuevo_ordenado = wb_nuevo.copy()
    wb_nuevo_entero = wb_nuevo.copy()
    wb_nuevo_ordenado.sort()
    lista_items_completa.sort()
    for i in range(len(wb_nuevo_ordenado)):
        index = wb_nuevo.index(wb_nuevo_ordenado[i])
        wb_nuevo[index] = "*"
        wb_nuevo_entero[index] = int(0)
        wb_nuevo_entero[index] = lista_items_completa[i]
    for elemento in wb_nuevo_entero:
        if elemento == 0:
            print("encontro")
    return wb_nuevo_entero


def buscar_mejor_bgmax(mejores_bgmax):
    """
    Función que se encarga de buscar aquel bgmax que tenga el menor arreglo de objetos
    :param mejores_bgmax:
    :return:
    """
    if len(mejores_bgmax) == 0:
        print("esta vacío mejores_bgmax")
    mejor_bgmax = mejores_bgmax[0]  #se establece que el mejor búfalo es el primero
    for i in range(len(mejores_bgmax)):
        if mejores_bgmax[i][4] < mejor_bgmax[4]:
            mejor_bgmax = mejores_bgmax[i]
    return mejor_bgmax

def obtener_subpatron(lista_items, long_objeto, index_inicio):
    """
    Función que obtiene un nuevo subpatron de acuerdo a la lista de ítems que se tiene para ver si este puede ser
    un mejor candidato
    :param lista_items:
    :param long_objeto:
    :param index_inicio:
    :return:
    """
    index_ultimo = index_inicio
    long_acumulado = 0
    list_items_subpatron = []
    subpatron = []
    for item in lista_items:  #recorre la lista de ítems para obtener el siguiene subpatron a enviar
        if long_acumulado + item <= long_objeto:  #si el siguiente item se puede incorporar
            long_acumulado += item
            list_items_subpatron.append(item)
            index_ultimo += 1
        else:
            break
    subpatron.append(list_items_subpatron)  #0-> lista de ítems
    subpatron.append(long_objeto - long_acumulado)  #1-> es el desperdicio obtenido
    subpatron.append(index_inicio)  #2-> index_inicio
    subpatron.append(index_ultimo - 1)  #3-> index_ultimo
    return subpatron


def obtener_mejor_subpatron(lista_items, long_objeto):
    """
    Función que obtiene el mejor subpatron de la lista que va quedando
    :param lista_items:
    :param long_objeto:
    :return:
    """
    mejor_subpatron = obtener_subpatron(lista_items, long_objeto, 0)  #se establece que el primer subpatron es el mejor
    i = 1
    while i < len(lista_items):
        nuevo_subpatron = obtener_subpatron(lista_items[i:].copy(), long_objeto, i)
        if nuevo_subpatron[1] < mejor_subpatron[1]:  #veriica si el nuevo subpatron obtiene un menor desperdicio
            mejor_subpatron = nuevo_subpatron
        i += 1
        """
        if mejor_subpatron[1] == 0:  #quiere decir que el mejor subpatron obtenido no tiene desperdicio
            break
        """
    return mejor_subpatron


def obtener_dict_clave_obj(dict_buf):
    """
    Función que obtiene la clave y el desperdicio obtenido de cada búfalo
    :param dict_buf:
    :return:
    """
    dict_buf_clave_desper = {}
    for clave in dict_buf:
        dict_buf_clave_desper.setdefault(clave, dict_buf[clave][4])
    return dict_buf_clave_desper

def ordenamiento_subpatrones_buf(list_subpa, long_obj):
    """
    Función que va ordenar los supatrones de acuerdo al desperdicio
    :param list_subpa:
    :param long_obj:
    :return:
    """
    lista_sup_ordenada = []  #contiene la lista de subpatrones ordenados
    dict_clave_desper = {} #lista que guardará la clave y el desperdicio generado de cada subpatrón
    lista_desper = []
    k = 0  #lleva el contador de la lista
    for i in range(len(list_subpa)):
        subpa = list_subpa[i].copy()
        total_acum = 0
        valor = isinstance(subpa, int)
        if valor:
            print("s")
        for j in range(len(subpa)):
            total_acum += subpa[j]
        desper_gen = long_obj - total_acum
        dict_clave_desper.setdefault(k, desper_gen)
        k += 1
    tupla_ordenada = sorted(dict_clave_desper.items(), key=lambda x: x[1])  #se ordena la tupla
    for i in range(len(list_subpa)):
        lista_sup_ordenada.append(list_subpa[tupla_ordenada[i][0]])
    for i in range(len(tupla_ordenada)):
        lista_desper.append(tupla_ordenada[i][1])
    return lista_sup_ordenada, lista_desper

def ordenamiento_bufalos(dict_buf, long_obj):
    """
    Función que ordena los búfalos de acuerdo al desperdicio total de sus patrones
    :param dict_buf:
    :return:
    """
    dict_buf_ord = {}
    dict_buf_clave_desper = obtener_dict_clave_obj(dict_buf.copy())  #se obtiene la clave y el num de objetos
    tupla_ordenada = sorted(dict_buf_clave_desper.items(), key=lambda x: x[1])  #se ordena la tupla de acuerdo
    for i in range(len(dict_buf)):
        dict_buf_ord.setdefault(i, dict_buf[tupla_ordenada[i][0]].copy())  #se van guardando los bufalos de manera ordenada
    for clave in dict_buf_ord:  #ordenamiento de los subpatrones de corte de cada búfalo
        subp_ord, desper_subp = ordenamiento_subpatrones_buf(dict_buf_ord[clave][6].copy(), long_obj)  #se manda la lista de subpatrones
        if len(dict_buf_ord[clave]) == 8:  #si tiene un elemento de más el búfalo se elimina
            dict_buf_ord[clave][7] = subp_ord
            dict_buf_ord[clave].append(desper_subp)
        else:  #si no es así
            dict_buf_ord[clave].append(subp_ord)
            dict_buf_ord[clave].append(desper_subp)
        if len(dict_buf_ord[clave]) == 10:
            print("tiene 10 elementos")
    return dict_buf_ord

def generar_bgmax(dict_buf, lista_items):
    """
    Función que genera el bgmax a partir de los mejores subpatrones de los búfalos
    :param dict_buf:
    :param lista_items:
    :return:
    """
    bgmax = []
    copia_lista_items = lista_items.copy()  #sirve para comprobar si se emplearon
    clave_buf = 0
    while len(lista_items) > 0:
        valor = isinstance(dict_buf[clave_buf][7], int)
        if valor:
            print("ss")
        while len(dict_buf[clave_buf][7]) == 0:  #en caso de que detecte un bufalo donde sus subpatrones ya hayan sido tomados en cuenta
            clave_buf += 1
        subp = dict_buf[clave_buf][7][0].copy()
        busqueda = True
        j = 0
        lista_items_busq = lista_items.copy()
        while busqueda and j < len(subp):  #proceso de busqueda de los items del subp en la lista de ítems
            if subp[j] in lista_items_busq:
                busqueda = True
                lista_items_busq.remove(subp[j])  #se remueve para no comprobar que esten los elementos de subp
                j += 1
            else:
                busqueda = False
        if busqueda:  #si busqueda es verdadero
            while len(subp) > 0:
                lista_items.remove(subp[0])
                bgmax.append(subp[0])  #añado al bgmax el elemento del sub
                del subp[0]
        del dict_buf[clave_buf][7][0]  #se elimina el subpatrón del búfalo debido a que se ha considerado
        del dict_buf[clave_buf][8][0]  #se elimina el desperdicio del subpatrón
        if len(dict_buf[clave_buf][7]) > 0:  #si todavía hay subpatrones
            if dict_buf[clave_buf][8][0] != 0:  #si el nuevosubpatron es diferente de cero se salta al siguiente búfalo para dar oportunidad a los otros subpatrones
                clave_buf += 1
        else:  #si ya no hay subpatrones se pasa al siguiente bufalo
            clave_buf += 1
        if clave_buf == len(dict_buf):  #si ya se recorrieron todos los búfalos se reinicializa la busqueda
            clave_buf = 0
        if (len(dict_buf[len(dict_buf)-1][7]) == 0) and (len(lista_items) > 0):  #si ya se recorrieron todos los búfalos y no se han seleccionado todos los items
            #print("Se recorrieron todos los búfalos y faltaron items")
            for i in range(len(lista_items)):
                bgmax.append(lista_items[i])
            lista_items.clear()
    return bgmax


def abo(landa, longitud_objeto, lp1, lp2, num_iteraciones, num_bufalos, dict_items, num_iter_rein):
    """
    Función que obtieen el mejor búfalo
    :return:
    """
    reinicio_manada = False
    mejores_bgmax = []
    vect_bgmax = []  #almacena en cada iteración el valor que vaya teniendo el bgmax
    lista_items_completa = obtenerlistacompletaitems(dict_items.copy())
    copia_lista_items_completa = lista_items_completa.copy()
    dict_bufalos = generacion_bufalos(num_bufalos, copia_lista_items_completa, longitud_objeto)
    copia_lista_items_completa.sort()  #se vuelve a reordenar de manera ascendete la copia de la lista de ítems
    bgmax = buscar_bgmax(dict_bufalos.copy())
    bgmax.append(1)  #se agrega 1 para establecer que en la primera iteracion se encontro al mejor bgmax
    bgmax_parcial = bgmax.copy()  #sirve para almacenar un posible cambio en el bgmax
    cambio_bgmax = False
    i = 1
    landa_enviar = landa
    contador_bgmax_construidos = 0  #sirve para llevar el conteo de los bgmax construidos realizados
    while i <= num_iteraciones:
        if i % 2 == 0:  #si i es par lambda el primer valor de lambda comienza negativo
            ini_lambda = -1
        else:
            ini_lambda = 1
        landa_enviar = landa_enviar * ini_lambda
        for clave in dict_bufalos:
            mb_nuevo = obtener_nuevo_mb_discretizado(dict_bufalos[clave][0].copy(), dict_bufalos[clave][1].copy(),
                                                     dict_bufalos[clave][2].copy(),
                                                     bgmax[1].copy(), lp1, lp2, lista_items_completa.copy())
            wb_nuevo = obtener_nuevo_wb(dict_bufalos[clave][1].copy(), dict_bufalos[clave][0].copy(), copia_lista_items_completa, landa_enviar)
            landa_enviar = landa_enviar * -1
            dict_bufalos[clave][0] = mb_nuevo.copy()
            dict_bufalos[clave][1] = wb_nuevo.copy()
            lista_arreglo_objetos, desper_total, obj_con_desper = obtenerdatosbufalo(dict_bufalos[clave][0].copy(), longitud_objeto)  #se obtienen los datos del
            if desper_total < dict_bufalos[clave][4]:  #en caso de que el wb_nuevo tenga menos desperdicio se actualiza el bpmax
                dict_bufalos[clave][2] = mb_nuevo.copy()  #el wb_nuevo es asignado al bpmax
                dict_bufalos[clave][3] = len(lista_arreglo_objetos)
                dict_bufalos[clave][4] = desper_total
                dict_bufalos[clave][5] = obj_con_desper
                dict_bufalos[clave][6] = lista_arreglo_objetos.copy()
                if desper_total < bgmax_parcial[4]:  #en caso de que los nuevos valores del búfalo sean mejores que bgmax
                    bgmax_parcial = dict_bufalos[clave].copy()
                    bgmax_parcial.append(i)
        if bgmax_parcial[4] < bgmax[4]:  #en caso de que sea mejor bgmax_parcial que el bgmax
            bgmax = bgmax_parcial.copy()
            i += 1
            if (i > num_iter_rein) and (i % num_iter_rein == 1):  #en caso de que se inicie una nueva decena de iteraciones
                cambio_bgmax = False
            else:  #si hubo un cambio en el bgmax pero no se inicio una nueva decena de iteraciones
                cambio_bgmax = True
        else:  #si no se actualizo el bgmax despues de recorrer todos los búfalos
            if (cambio_bgmax == False) and (i % num_iter_rein == 0):
                contador_bgmax_construidos += 1
                reinicio_manada = True
                mejores_bgmax.append(bgmax.copy())
                dict_buf_ord = ordenamiento_bufalos(dict_bufalos.copy(), longitud_objeto)  #se obtienen los búfalos ordenados
                lista_item_bgmax_generado = generar_bgmax(dict_buf_ord.copy(), lista_items_completa.copy())
                lista_arreglo_objetos, desper_total, obj_con_desper = obtenerdatosbufalo(lista_item_bgmax_generado.copy(),
                                                                                         longitud_objeto)  #se obtienen los datos de la
                dict_bufalos.clear()
                dict_bufalos = generacion_bufalos(num_bufalos, copia_lista_items_completa, longitud_objeto)
                copia_lista_items_completa.sort()

                # Es para no hacer la comparación del bgmax construido y el bgmax encontrado en la nueva manada
                bgmax[0] = lista_item_bgmax_generado.copy()
                bgmax[1] = lista_item_bgmax_generado.copy()
                bgmax[2] = lista_item_bgmax_generado.copy()
                bgmax[3] = len(lista_arreglo_objetos)
                bgmax[4] = desper_total
                bgmax[5] = obj_con_desper
                bgmax[6] = lista_arreglo_objetos.copy()
                bgmax[7] = i
                dict_buf_ord.clear()
                bgmax_parcial = bgmax.copy()  #sirve para almacenar un posible cambio en el bgmax
                cambio_bgmax = False
                i += 1
            else:
                i += 1
                if (i > num_iter_rein) and (i % num_iter_rein == 1):
                    cambio_bgmax = False
        vect_bgmax.append(bgmax[3])

    if reinicio_manada == False:
        print("No se reinicio la manada")
        mejores_bgmax.append(bgmax.copy())
    mejor_bgmax = buscar_mejor_bgmax(mejores_bgmax.copy())
    return mejor_bgmax

def obtenerdatosbufalo(lista_items, longitud_objeto):
    """
    Función que permite obtener el arreglo de ítems, desperdicio total y los objetos con desperdicio
    :param lista_items:
    :param longitud_objeto:
    :return:
    """
    lista_arreglo_objetos = []  #guardará todas las listas de objetos
    desper_total = 0  #guardara el desperdicio total
    obj_con_desper = 0  #guardara los objetos con desperdicio
    long_arr_items = 0  #variable que permitirá sumar la longitud de cada ítem
    lista_items_obj = []  #contendrá la lista de los ítems por objeto
    desper_obj = 0  #acumula el desperdicio por objeto
    for i in range(len(lista_items)):
        if long_arr_items + lista_items[i] <= longitud_objeto:  #si se puede sumar el item en el arreglo actual
            long_arr_items += lista_items[i]
            lista_items_obj.append(lista_items[i])
        else:
            lista_arreglo_objetos.append(lista_items_obj.copy())  #se agrega la copia de la lista de ítems por objeto
            desper_obj = longitud_objeto - long_arr_items  #se calcula el desperdicio por objeto
            desper_total += desper_obj  #se suma el desperdicio por objeto al total
            if desper_obj > 0:  #si hubo desperdicio en el objeto se le suma
                obj_con_desper += 1
            long_arr_items = lista_items[i]  #inicializa la longitud
            lista_items_obj.clear()
            lista_items_obj.append(lista_items[i])  #se agrega el item al nuevo objeto
            desper_obj = 0  #se inicializa el desper_obj en cero
            if i == len(lista_items) - 1:  #en caso de que haya llegado al último elemento se tiene que contar
                lista_arreglo_objetos.append(lista_items_obj.copy())
                desper_obj = longitud_objeto - long_arr_items
                desper_total += desper_obj
                if desper_obj > 0:
                    obj_con_desper += 1
                long_arr_items = 0  #se inicializa en 0 para asegurar que ya se contabilizaron todos los arreglos
    if long_arr_items != 0:  #en caso de que no se haya contabilizado el último arreglo
        lista_arreglo_objetos.append(lista_items_obj.copy())
        desper_obj = longitud_objeto - long_arr_items
        desper_total += desper_obj
        if desper_obj > 0:
            obj_con_desper += 1
    return lista_arreglo_objetos, desper_total, obj_con_desper


def calcularpromedios(dict_mejores_bufalos, num_ejecuciones):
    """
    Función que calcula los promedios de las mejores ejecuciones
    :param dict_mejores_bufalos:
    :param num_ejecuciones:
    :return:
    """
    acum_obj = 0  #acumula los totales de objetos de los búfalos
    acum_desper = 0  #acumula el desperdicio de todos los bufalos
    acum_obj_desper = 0  #acumula los obj con desperdicio de todos los búfalos
    acum_tiempo = 0  #acumula todos el tiempo promedio calculado
    acum_iter = 0  #acumula el número de iteraciones en el que se encontro el mejor búfalo
    for clave in dict_mejores_bufalos:
        acum_obj += dict_mejores_bufalos[clave][3]
        acum_desper += dict_mejores_bufalos[clave][4]
        acum_obj_desper += dict_mejores_bufalos[clave][5]
        acum_tiempo += dict_mejores_bufalos[clave][8]
        acum_iter += dict_mejores_bufalos[clave][7]
    prom_obj = acum_obj / num_ejecuciones
    prom_desper = acum_desper / num_ejecuciones
    prom_obj_desper = acum_obj_desper / num_ejecuciones
    prom_tiempo = acum_tiempo / num_ejecuciones
    prom_iter = acum_iter / num_ejecuciones
    return prom_obj, prom_desper, prom_obj_desper, prom_tiempo, prom_iter


if __name__ == "__main__":
    """Funció Principal"""
    informacion = {  #Diccionario que guardara los datos de cada prueba
        'Num_ejecuciones': [],
        'Num_iteraciones': [],
        'Lp1': [],
        'Lp2': [],
        'Lambda': [],
        'Num_bufalos': [],
        'Prom_objetos': [],
        'Prom_desperdicio': [],
        'Prom_obj_con_desperdicio': [],
        'Prom_tiempo': [],
        'Prom_iteracion': [],
        'Iteraciones_reinicio_manada': []
    }
    num_pruebas = 1  #es el número de pruebas que se van a realizar por cada tipo de landa
    num_ejecuciones = 50
    num_rein_iter = 10 #es el número de iteraciones necesarias para reinicializar la manada
    nombre_instancia = "2a"
    dict_mejores_bufalos = {}
    longitud_objeto = 15
    lp1 = 0.3
    lp2 = 0.6
    lista_landas = [1]
    lista_num_iteraciones = [50]
    lista_num_bufalos = [50]
    dict_items = {
        3: 4,
        4: 8,
        5: 5,
        6: 7,
        7: 8,
        8: 5,
        9: 5,
        10: 8




    }
    print("Comenzo con la prueba de la instancia: {}".format(nombre_instancia))
    for landa in lista_landas:
        print("Comenzo con lambda: {} ************************++".format(landa))
        for num_iteraciones in lista_num_iteraciones:
            print("Comenzo con numero de iteraciones: {}".format(num_iteraciones))
            for num_bufalos in lista_num_bufalos:
                print("Comenzo con numero de búfalos: {}".format(num_bufalos))
                for j in range(num_pruebas):
                    print("Esta en la prueba: {}".format(j))
                    for i in range(num_ejecuciones):
                        inicio = timer()
                        mejor_bufalo = abo(landa, longitud_objeto, lp1, lp2, num_iteraciones, num_bufalos, dict_items,
                                           num_rein_iter)
                        fin = timer()
                        tiempo_ejecucion = fin - inicio
                        mejor_bufalo.append(tiempo_ejecucion)
                        dict_mejores_bufalos.setdefault(i, mejor_bufalo.copy())
                        mejor_bufalo.clear()
                    prom_obj, prom_desper, prom_obj_desper, prom_tiempo, prom_iter = calcularpromedios(dict_mejores_bufalos.copy(), num_ejecuciones)
                    dict_mejores_bufalos.clear()
                    informacion["Num_ejecuciones"].append(num_ejecuciones)
                    informacion["Num_iteraciones"].append(num_iteraciones)
                    informacion["Lp1"].append(lp1)
                    informacion["Lp2"].append(lp2)
                    informacion["Lambda"].append(landa)
                    informacion["Num_bufalos"].append(num_bufalos)
                    informacion["Prom_objetos"].append(prom_obj)
                    informacion["Prom_desperdicio"].append(prom_desper)
                    informacion["Prom_obj_con_desperdicio"].append(prom_obj_desper)
                    informacion["Prom_tiempo"].append(prom_tiempo)
                    informacion["Prom_iteracion"].append(prom_iter)
                    informacion["Iteraciones_reinicio_manada"].append(num_rein_iter)

    df = pd.DataFrame(informacion, columns=informacion.keys())  #pasa el diccionario de todas las pruebas en un dataframe
    df.to_csv('prueba_'+nombre_instancia+'.csv', header=True, index=True)
    """
                    print("Lambda: {}".format(landa))
                    print("Número de Iteraciones: {}".format(num_iteraciones))
                    print("Número de Búfalos: {}".format(num_bufalos))
                    print("El número de objetos promedio fue de: {} ".format(prom_obj))
                    print("El desperdicio promedio fue de: {} ".format(prom_desper))
                    print("El número de objetos con desperdicio fue de: {} ".format(prom_obj_desper))
                    print("El tiempo promedio fue de: {} ".format(prom_tiempo))
                    print("El promedio de iteraciones en el que encontro el mejor búfalo fue de: {}".format(prom_iter))
                    """
    print("Termino")


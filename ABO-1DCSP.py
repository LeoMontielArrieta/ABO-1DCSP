"""
Developed in Python Version 3.7
Author and programmer: Leonardo Javier Montiel Arrieta

 email:   mo450519@uaeh.edu.mx

 The initial parameters that you need are:
    num_tests =   number of tests
    num_executions = number of executions
    num_rein_iter = number of iterations to restart the herd
    name_instance = name of the instance
    object_length = longitud del objeto
    lp1 = learning factor of African Buffalo Optimization algorithm
    lp2 = learning factor of African Buffalo Optimization algorithm
    lambda_list = list of lambdas
    list_num_iterations = list of number of iterations
    list_num_buffalos = list of number of buffaloes


"""
from timeit import timeit
from random import shuffle, random
import math
import matplotlib.pyplot as plt
import numpy as np
import heapq
from timeit import default_timer as timer
import pandas as pd


def obtainfulllistitems(dict_items):
    """
    Function that allows obtaining an ordered list with all the items ordered from smallest to largest
    :param dict_items:
    :return:
    """
    list_items = []
    for key in dict_items:
        for i in range(dict_items[key]):
            list_items.append(key)
    return list_items


def generationbuffaloes(num_buffalos, full_list_items, object_length):
    """
    Function that allows you to generate buffaloes
    :param num_buffalos:
    :param full_list_items:
    :param object_length:
    :return:
    """
    dict_buffalos = {}
    for i in range(num_buffalos):
        shuffle(full_list_items)
        copy_list_items = full_list_items.copy()
        dict_buffalos.setdefault(i, [copy_list_items, copy_list_items, copy_list_items])  #mb, wb and bpmax are set with the list of items reordered
        list_array_objects, total_waste, obj_with_waste = getdatabuffaloe(dict_buffalos[i][1].copy(), object_length)
        dict_buffalos[i].append(len(list_array_objects))  #the number of objects is added based on the size of the list
        dict_buffalos[i].append(total_waste)
        dict_buffalos[i].append(obj_with_waste)
        dict_buffalos[i].append(list_array_objects)
    return dict_buffalos


def search_bgmax(dict_buffalos):
    """
    Function that gets the best buffalo of the herd
    :param dict_buffalos:
    :return: bgmax
    """
    bgmax = dict_buffalos[0]
    for key in dict_buffalos:
        if dict_buffalos[key][4] < bgmax[4]:
            bgmax = dict_buffalos[key].copy()
    return bgmax


def get_new_mb_discretized(current_mb, current_wb, bpmax, bgmax, lp1, lp2, full_list_items):
    """
    Function that obtains the new mb of each buffalo applying the ROV
    :param current_mb:
    :param current_wb:
    :param bpmax:
    :param bgmax:
    :param lp1:
    :param lp2:
    :return:
    """
    new_mb = []
    for i in range(len(current_mb)):
        new_mb.append(current_mb[i] + lp1 * (bgmax[i] - current_wb[i]) + lp2 * (bpmax[i] - current_wb[i]))
    mb_new_sort = new_mb.copy()
    mb_new_int = new_mb.copy()
    mb_new_sort.sort()
    full_list_items.sort()
    for i in range(len(mb_new_sort)):
        index = new_mb.index(mb_new_sort[i])
        new_mb[index] = "*"
        mb_new_int[index] = int(0)
        mb_new_int[index] = full_list_items[i]
    for element in mb_new_int:
        if element == 0:
            print("Found")
    return mb_new_int


def get_new_wb(current_wb, current_mb, full_list_items, landa):
    """
    Function that gets the new wb of each buffalo
    :param current_wb:
    :param current_mb:
    :param full_list_items:
    :param landa:
    :return: wb_nuevo
    """
    new_wb = []
    for i in range(len(current_wb)):
        new_wb.append((current_wb[i] + current_mb[i]) / landa)
    wb_new_sort = new_wb.copy()
    wb_new_int = new_wb.copy()
    wb_new_sort.sort()
    full_list_items.sort()
    for i in range(len(wb_new_sort)):
        index = new_wb.index(wb_new_sort[i])
        new_wb[index] = "*"
        wb_new_int[index] = int(0)
        wb_new_int[index] = full_list_items[i]
    for element in wb_new_int:
        if element == 0:
            print("Found")
    return wb_new_int


def search_best_bgmax(list_best_bgmax):
    """
    Function that looks for the best global bgmax
    :param list_best_bgmax:
    :return:
    """
    if len(list_best_bgmax) == 0:
        print("The list is empty")
    best_bgmax = list_best_bgmax[0]
    for i in range(len(list_best_bgmax)):
        if list_best_bgmax[i][4] < best_bgmax[4]:
            best_bgmax = list_best_bgmax[i]
    return best_bgmax

def get_subpattern(list_items, object_length, index_start):
    """
    Function that obtains a new subpattern according to the list of items that it has
    :param list_items:
    :param object_length:
    :param index_start:
    :return:
    """
    index_last = index_start
    length_accumulated = 0
    list_items_subpattern = []
    subpattern = []
    for item in list_items:
        if length_accumulated + item <= object_length:  #if the following item can be incorporated
            length_accumulated += item
            list_items_subpattern.append(item)
            index_last += 1
        else:
            break
    subpattern.append(list_items_subpattern)  #0-> Items list
    subpattern.append(object_length - length_accumulated)  #1-> is the waste obtained
    subpattern.append(index_start)  #2-> start index
    subpattern.append(index_last - 1)  #3-> last index
    return subpattern


def get_best_subpattern(list_items, object_length):
    """
    Function that obtains the best subpattern of the remaining items
    :param list_items:
    :param object_length:
    :return:
    """
    best_subpattern = get_subpattern(list_items, object_length, 0)  #the first subpattern is established to be the best
    i = 1
    while i < len(list_items):
        new_subpatter = get_subpattern(list_items[i:].copy(), object_length, i)
        if new_subpatter[1] < best_subpattern[1]:  #check if the new sub pattern gets less waste
            best_subpattern = new_subpatter
        i += 1
    return best_subpattern


def get_key_dict_obj(dict_buffaloes):
    """
    Function that gets the key and the waste obtained from each buffalo
    :param dict_buffaloes:
    :return:
    """
    dict_buf_key_waste = {}
    for clave in dict_buffaloes:
        dict_buf_key_waste.setdefault(clave, dict_buffaloes[clave][4])
    return dict_buf_key_waste

def ordering_subpatterns_buffaloe(list_subpatterns, object_length):
    """
    Function that will order the subpatterns of each buffalo according to waste
    :param list_subpatterns:
    :param object_length:
    :return:
    """
    list_subpatterns_ordered = []  #contains the list of ordered subpatterns
    dict_key_waste = {} #list that stores the key and waste generated from each subpattern
    list_waste = []
    k = 0  #keep track of the list
    for i in range(len(list_subpatterns)):
        subpattern = list_subpatterns[i].copy()
        total_acum = 0
        value = isinstance(subpattern, int)
        if value:
            print("It is a integer type")
        for j in range(len(subpattern)):
            total_acum += subpattern[j]
        waste_generated = object_length - total_acum
        dict_key_waste.setdefault(k, waste_generated)
        k += 1
    ordered_tuple = sorted(dict_key_waste.items(), key=lambda x: x[1])  #the tuple is sorted
    for i in range(len(list_subpatterns)):
        list_subpatterns_ordered.append(list_subpatterns[ordered_tuple[i][0]])
    for i in range(len(ordered_tuple)):
        list_waste.append(ordered_tuple[i][1])
    return list_subpatterns_ordered, list_waste

def buffalo_sorting(dict_buffaloes, object_length):
    """
    Function that orders the buffaloes according to the total waste of their subpatterns
    :param dict_buffaloes:
    :return:
    """
    dict_buf_sort = {}
    dict_buf_key_waste = get_key_dict_obj(dict_buffaloes.copy())  #the key and the number of objects of each buffalo are obtained
    ordered_tuple = sorted(dict_buf_key_waste.items(), key=lambda x: x[1])  #the tuple is sorted
    for i in range(len(dict_buffaloes)):
        dict_buf_sort.setdefault(i, dict_buffaloes[ordered_tuple[i][0]].copy())  #the buffaloes are kept in an orderly manner
    for clave in dict_buf_sort:  #ordering of the cutting subpatterns of each buffalo
        subpatterm_sort, waste_subpattern = ordering_subpatterns_buffaloe(dict_buf_sort[clave][6].copy(), object_length)  #the list of subpatterns is sent
        if len(dict_buf_sort[clave]) == 8:  #if it has one more element, the buffalo is eliminated
            dict_buf_sort[clave][7] = subpatterm_sort
            dict_buf_sort[clave].append(waste_subpattern)
        else:
            dict_buf_sort[clave].append(subpatterm_sort)
            dict_buf_sort[clave].append(waste_subpattern)
        if len(dict_buf_sort[clave]) == 10:
            print("It has 10 elements")
    return dict_buf_sort

def generate_bgmax(dict_buffaloes, list_items):
    """
    Function that generates the bgmax from the best subpatterns of the buffaloes in the current herd
    :param dict_buffaloes:
    :param list_items:
    :return:
    """
    bgmax = []
    copy_list_items = list_items.copy()  #It is used to check if all the items have been used.
    key_buffaloe = 0
    while len(list_items) > 0:
        value = isinstance(dict_buffaloes[key_buffaloe][7], int)
        if value:
            print("ss")
        while len(dict_buffaloes[key_buffaloe][7]) == 0:  #in case you detect a buffalo where its subpatterns have already been taken into account
            key_buffaloe += 1
        subp = dict_buffaloes[key_buffaloe][7][0].copy()
        search = True
        j = 0
        list_items_search = list_items.copy()
        while search and j < len(subp):  #search process for subpattern items in the item list
            if subp[j] in list_items_search:
                search = True
                list_items_search.remove(subp[j])  #remove each item from the item list
                j += 1
            else:
                search = False
        if search:
            while len(subp) > 0:
                list_items.remove(subp[0])
                bgmax.append(subp[0])  #each subpattern element is added to bgmax
                del subp[0]
        del dict_buffaloes[key_buffaloe][7][0]  #the buffalo subpattern is removed because it has been considered
        del dict_buffaloes[key_buffaloe][8][0]  #the waste of subpattern
        if len(dict_buffaloes[key_buffaloe][7]) > 0:  #if there are still subpatterns
            if dict_buffaloes[key_buffaloe][8][0] != 0:  #if the new subpattern is different from zero it skips to the next buffalo to give other buffaloes a chance
                key_buffaloe += 1
        else:  #if there are no subpatterns, it goes to the next buffalo
            key_buffaloe += 1
        if key_buffaloe == len(dict_buffaloes):  #If all the buffaloes have already been searched, the search is reinitialized
            key_buffaloe = 0
        if (len(dict_buffaloes[len(dict_buffaloes) - 1][7]) == 0) and (len(list_items) > 0):  #if all the buffaloes have already been covered and not all the items have been selected
            for i in range(len(list_items)):
                bgmax.append(list_items[i])
            list_items.clear()
    return bgmax


def abo(landa, object_length, lp1, lp2, num_iterations, num_buffalos, dict_items, num_iter_restart):
    """
    Function to get the best solution
    :return:
    """
    restart_herd = False
    best_bgmax = []
    complete_item_list = obtainfulllistitems(dict_items.copy())
    copy_complete_item_list = complete_item_list.copy()
    dict_buffalos = generationbuffaloes(num_buffalos, copy_complete_item_list, object_length)
    copy_complete_item_list.sort()
    bgmax = search_bgmax(dict_buffalos.copy())
    bgmax.append(1)  #1 is added to establish that in the first iteration the best bgmax was found
    bgmax_partial = bgmax.copy()  #It is used to store a possible change in the bgmax
    change_bgmax = False
    i = 1
    landa_send = landa
    bgmax_counter_built = 0  #It is used to keep track of the built bgmax made
    while i <= num_iterations:
        if i % 2 == 0:  #if i is even lambda the first value of lambda starts negative
            ini_lambda = -1
        else:
            ini_lambda = 1
        landa_send = landa_send * ini_lambda
        for clave in dict_buffalos:
            mb_new = get_new_mb_discretized(dict_buffalos[clave][0].copy(), dict_buffalos[clave][1].copy(),
                                            dict_buffalos[clave][2].copy(),
                                            bgmax[1].copy(), lp1, lp2, complete_item_list.copy())
            wb_new = get_new_wb(dict_buffalos[clave][1].copy(), dict_buffalos[clave][0].copy(), copy_complete_item_list, landa_send)
            landa_send = landa_send * -1
            dict_buffalos[clave][0] = mb_new.copy()
            dict_buffalos[clave][1] = wb_new.copy()
            list_array_objects, total_waste, obj_with_waste = getdatabuffaloe(dict_buffalos[clave][0].copy(), object_length)  #buffalo data is obtained
            if total_waste < dict_buffalos[clave][4]:  #in case the new_wb has less waste, the bpmax is updated
                dict_buffalos[clave][2] = mb_new.copy()
                dict_buffalos[clave][3] = len(list_array_objects)
                dict_buffalos[clave][4] = total_waste
                dict_buffalos[clave][5] = obj_with_waste
                dict_buffalos[clave][6] = list_array_objects.copy()
                if total_waste < bgmax_partial[4]:  #in case the new buffalo values are better than bgmax
                    bgmax_partial = dict_buffalos[clave].copy()
                    bgmax_partial.append(i)
        if bgmax_partial[4] < bgmax[4]:  #in case bgmax_partial is better than the bgmax
            bgmax = bgmax_partial.copy()
            i += 1
            if (i > num_iter_restart) and (i % num_iter_restart == 1):  #in case a new iteration cycle is started
                change_bgmax = False
            else:  #if there was a change in the bgmax but a new iteration cycle was not started
                change_bgmax = True
        else:  #If the bgmax was not updated after going through all the buffaloes
            if (change_bgmax == False) and (i % num_iter_restart == 0):
                bgmax_counter_built += 1
                restart_herd = True
                best_bgmax.append(bgmax.copy())
                dict_buf_sort = buffalo_sorting(dict_buffalos.copy(), object_length)  #ordered buffaloes are obtained
                list_item_bgmax_built = generate_bgmax(dict_buf_sort.copy(), complete_item_list.copy())
                list_array_objects, total_waste, obj_with_waste = getdatabuffaloe(list_item_bgmax_built.copy(),
                                                                                  object_length)
                dict_buffalos.clear()
                dict_buffalos = generationbuffaloes(num_buffalos, copy_complete_item_list, object_length)
                copy_complete_item_list.sort()
                bgmax[0] = list_item_bgmax_built.copy()
                bgmax[1] = list_item_bgmax_built.copy()
                bgmax[2] = list_item_bgmax_built.copy()
                bgmax[3] = len(list_array_objects)
                bgmax[4] = total_waste
                bgmax[5] = obj_with_waste
                bgmax[6] = list_array_objects.copy()
                bgmax[7] = i
                dict_buf_sort.clear()
                bgmax_partial = bgmax.copy()
                change_bgmax = False
                i += 1
            else:
                i += 1
                if (i > num_iter_restart) and (i % num_iter_restart == 1):
                    change_bgmax = False
    if restart_herd == False:
        print("The herd did not restart")
        best_bgmax.append(bgmax.copy())
    best_global_bgmax = search_best_bgmax(best_bgmax.copy())
    return best_global_bgmax

def getdatabuffaloe(list_items, object_length):
    """
    Function that allows obtaining the arrangement of items, total waste and objects with waste from each buffalo
    :param list_items:
    :param object_length:
    :return:
    """
    list_array_objects = []  #will save all object lists
    total_waste = 0  #will save the total waste
    obj_with_waste = 0  #will keep the objects with waste
    long_arr_items = 0  #variable that allows adding the length of each item
    list_items_object = []  #will contain the list of items per object
    waste_object = 0  #accumulate waste by object
    for i in range(len(list_items)):
        if long_arr_items + list_items[i] <= object_length:
            long_arr_items += list_items[i]
            list_items_object.append(list_items[i])
        else:
            list_array_objects.append(list_items_object.copy())
            waste_object = object_length - long_arr_items
            total_waste += waste_object
            if waste_object > 0:
                obj_with_waste += 1
            long_arr_items = list_items[i]
            list_items_object.clear()
            list_items_object.append(list_items[i])
            waste_object = 0
            if i == len(list_items) - 1:  #in case you have reached the last element you have to count
                list_array_objects.append(list_items_object.copy())
                waste_object = object_length - long_arr_items
                total_waste += waste_object
                if waste_object > 0:
                    obj_with_waste += 1
                long_arr_items = 0  #is initialized to 0 to ensure that all arrays have already been accounted for
    if long_arr_items != 0:  #in case the last array has not been counted
        list_array_objects.append(list_items_object.copy())
        waste_object = object_length - long_arr_items
        total_waste += waste_object
        if waste_object > 0:
            obj_with_waste += 1
    return list_array_objects, total_waste, obj_with_waste


def calculateaverages(dict_best_buffaloes, num_executions):
    """
    Function that calculates the waste averages, used objects and objects with waste
    :param dict_best_buffaloes:
    :param num_executions:
    :return:
    """
    acum_obj = 0  #accumulates the stocks of the buffaloes
    acum_waste = 0  #accumulate the waste of all the buffaloes
    acum_obj_waste = 0  #accumulates the objects or stocks with waste of all the buffaloes
    acum_time = 0  #Accumulate time to get the best solutions
    acum_iter = 0  #accumulates the number of iterations in which the best buffalo was found
    for clave in dict_best_buffaloes:
        acum_obj += dict_best_buffaloes[clave][3]
        acum_waste += dict_best_buffaloes[clave][4]
        acum_obj_waste += dict_best_buffaloes[clave][5]
        acum_time += dict_best_buffaloes[clave][8]
        acum_iter += dict_best_buffaloes[clave][7]
    prom_obj = acum_obj / num_executions
    prom_desper = acum_waste / num_executions
    prom_obj_desper = acum_obj_waste / num_executions
    prom_tiempo = acum_time / num_executions
    prom_iter = acum_iter / num_executions
    return prom_obj, prom_desper, prom_obj_desper, prom_tiempo, prom_iter


if __name__ == "__main__":
    """Main Function"""
    information = {  #Dictionary that will save the data of each test
        'Num_executions': [],
        'Num_iterations': [],
        'Lp1': [],
        'Lp2': [],
        'Lambda': [],
        'Num_buffalos': [],
        'Avg_objects': [],
        'Avg_waste': [],
        'Avg_obj_with_waste': [],
        'Avg_time': [],
        'Avg_iteration': [],
        'Iterations_restart_herd': []
    }
    num_tests = 1
    num_executions = 50
    num_rein_iter = 10
    name_instance = "2a"
    dict_best_buffalos = {}
    object_length = 15
    lp1 = 0.3
    lp2 = 0.6
    lambda_list = [1]
    list_num_iterations = [50]
    list_num_buffalos = [50]
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
    print(" Started with the test of the instance: {}".format(name_instance))
    for landa in lambda_list:
        print("Started with lambda: {} ************************++".format(landa))
        for num_iterations in list_num_iterations:
            print("Started with the number of iterations: {}".format(num_iterations))
            for num_buffalos in list_num_buffalos:
                print("Started with the number of buffaloes: {}".format(num_buffalos))
                for j in range(num_tests):
                    print("It is on the test: {}".format(j))
                    for i in range(num_executions):
                        start = timer()
                        best_buffalo = abo(landa, object_length, lp1, lp2, num_iterations, num_buffalos, dict_items,
                                           num_rein_iter)
                        end = timer()
                        execution_time = end - start
                        best_buffalo.append(execution_time)
                        dict_best_buffalos.setdefault(i, best_buffalo.copy())
                        best_buffalo.clear()
                    prom_obj, prom_desper, prom_obj_desper, prom_tiempo, prom_iter = calculateaverages(dict_best_buffalos.copy(), num_executions)
                    dict_best_buffalos.clear()
                    information["Num_executions"].append(num_executions)
                    information["Num_iterations"].append(num_iterations)
                    information["Lp1"].append(lp1)
                    information["Lp2"].append(lp2)
                    information["Lambda"].append(landa)
                    information["Num_buffalos"].append(num_buffalos)
                    information["Avg_objects"].append(prom_obj)
                    information["Avg_waste"].append(prom_desper)
                    information["Avg_obj_with_waste"].append(prom_obj_desper)
                    information["Avg_time"].append(prom_tiempo)
                    information["Avg_iteration"].append(prom_iter)
                    information["Iterations_restart_herd"].append(num_rein_iter)

    df = pd.DataFrame(information, columns=information.keys()) 
    df.to_csv('test_' + name_instance + '.csv', header=True, index=True)
    print("Finished")


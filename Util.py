#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 18 01:15:03 2020
​
@author: apple
"""
import random 
from collections import deque
import time 
import uuid
class Map:
    def query(self, store_loc, customer_loc, transport):
        dist = sum([abs(store_loc[i] - customer_loc[i]) for i in range(2)])
        if transport == 1:
            trans_time = dist/(5*random.uniform(0,1))
        elif transport == 2:
            trans_time = dist/1
        return dist, trans_time
class Store:
    def __init__(self, location, store_ID, inventory, menu, worker = 6 , speed = 10):
        self.loc = location
        self.speed = speed
        self.queue = deque()
        self.in_process = deque()
        self.ID = store_ID
        self.waiting_time = 0
        self.inventory = inventory
        self.recipe = {}
        self.menu = menu
    def take_order(self,order_ID, order):
        self.queue.append((order_ID, order))
        self.waiting_time += self.speed
        return (order_ID, 2)
    def start_order(self):
        order_ID, order = self.queue.popleft()
        self.in_process.append(order_ID)
        return (order_ID, 3)
    def finish_order(self, order_ID):
        self.in_process.remove(order_ID)
        self.waiting_time -= self.speed
        return (order_ID, 4)
    
class Order:
    def __init__(self, order_ID, order, order_loc, dest, order_constraint):
        self.ID = order_ID
        self.order = order
        self.dest = dest
        self.t = time.time()
        self.status = 0
        self.loc = order_loc
        self.time_limit = order_constraint['time']
        self.dist_limit = order_constraint['distance']
    def change_status(self, status):
        '''
        0 : pending query
        1 : pending confirmation
        2 : order taken
        3 : order start
        4 : order complete
        5 : query expired
        -1 : quary failed
        '''
        self.status = status
    def add_store_list(self, store_list):
        self.store_list = store_list
        self.change_status(1)
    def order_taken(self):
        self.change_status(2)
    def order_start(self):
        self.change_status(3)  
    def order_complete(self):
        self.change_status(4)  
    def query_expired(self):
        self.change_status(5)  
    def query_failed(self):
        self.change_status(-1)
    def update_failed(self):
        self.change_status(-2)

class Agent:
    def __init__(self):
        self.store_list = {}
        self.pending_request = {}
        self.pending_confirm = deque()
        self.in_process = deque()
    def open_store(self, store_loc, menu, inventory):
        print('open store good')
        store_ID = str(uuid.uuid4())
        self.store_list[store_ID] = Store(store_loc, store_ID, inventory, menu)
        print(self.store_list)
        return store_ID,'store opened'
    def close_store(self, store_ID):
        print(self.store_list)
        del self.store_list[store_ID]
        return store_ID, 'store closed'
    def new_query(self, order_list, order_loc, order_dest, order_constraint):
        new_order = Order(str(uuid.uuid4()), order_list, order_loc, order_dest,order_constraint)
        choices = self.query(new_order)
        if choices != -1:
            print('successfully queried order')
            new_order.add_store_list(choices)
            self.pending_request[new_order.ID] = new_order
            return new_order.ID, new_order.status, choices
        else:
            print('No available choices')
            new_order.query_failed()
            return new_order.ID, new_order.status, choices
    def query(self, order):
        choices = {}
        for store in self.store_list.values():
            dist, travel_time = Map().query(store.loc, order.loc, 1) 
            if dist <= order.dist_limit and travel_time <= order.time_limit:
                todest, todest_time = Map().query(store.loc, order.dest,  1)
                dist += todest
                travel_time += todest_time
                if dist <= order.dist_limit and travel_time <= order.time_limit:
                    travel_time += store.waiting_time + store.speed
                    if dist <= order.dist_limit and travel_time <= order.time_limit:
                        choices[store.ID] = (dist, travel_time)
        if len(choices) > 1:
            choices = sorted(choices.items(), key = lambda x : x[1])     
            return choices
        elif len(choices) == 1:
            return choices
        return -1
    def comfirm_w_store(self, order_ID, choice_ID):
        order = self.pending_request[order_ID]
        (store, (dist, time)) = order.store_list[choice_ID]
        updated_choices = self.query(order)
        if updated_choices != -1:
            if dict(updated_choices)[store][1] <= time*1.2:
                message = self.store_list[store].take_order(order_ID, order.order)
                if message[1] == 2:
                    order.order_taken()
                    self.in_process.append(order_ID, order)
                    return order.ID, order.status, message
            else:
                order.query_expired() 
                return order.ID, order.status,message 
        else:
            order.update_failed()
            return order.ID, order.status, updated_choices
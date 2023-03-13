# -*- coding: utf-8 -*-
"""
Created on Sat Mar  4 22:40:07 2023

@author: Sam
"""

import hashlib







partition_list = {'0':0,'1':1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'a':10,'b':11,'c':12,'d':13,'e':14,'f':15}


active_list=['a','b','c']


def hash_partition(key='k1'):
    hashed_key= hashlib.md5(key.encode()).hexdigest()



    
    return partition_list[hashed_key[0].lower()]


def route_partition_node(number_active_node=1,partition_number=0):
    
    return partition_number%number_active_node


    
 


 
list_key=['a','12adcd','bcdaaaaaaa','bbbbbbbbaab','aaa','bbbbbbbbb','bboabbbb']    


for key in list_key:
   part_number=hash_partition(key=key)
   print(part_number)
   print(key, " Belong to partion ",part_number+1)
   print("Belong to node: ",active_list[route_partition_node(number_active_node=len(active_list),partition_number=part_number)])





#print(hashed_key, " Belong to partion ",partition_list[hashed_key[0].lower()]+1)





#print(hashed_key2, " Belong to partion ",partition_list[hashed_key2[0].lower()]+1)
#print((int)hashed_key%16)
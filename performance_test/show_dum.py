# -*- coding: utf-8 -*-
"""
Created on Sat Feb  4 19:09:53 2023

@author: Sam
"""

import requests 
import random

list_text=['a','12adcd','bcdaaaaaaa','bbbbbbbbaab','aaa','bbbbbbbbb','bboabbbb'] 
list_pic=['a.png','12adcd.png','bcdaaaaaaa.png','bbbbbbbbaab.png','aaa.png','bbbbbbbbb.png','bboabbbb.png'] 


index=random.randint(0,6)


text={'text':list_text[index]}



#file = {'my_image': open('uploadtest.png','rb')}

response = requests.post('http://127.0.0.1:5000/show_image', data=text) 
print(response.elapsed.total_seconds())

f = open("time.txt", "a")
#f.write("display time: "+str(response.elapsed.total_seconds())+"\n")
f.write(str(response.elapsed.total_seconds())+"\n")
f.close()

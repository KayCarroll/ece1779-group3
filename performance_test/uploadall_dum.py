# -*- coding: utf-8 -*-
"""
Created on Sat Feb  4 19:09:53 2023

@author: Sam
"""

import requests 
import random

list_text=['a','12adcd','bcdaaaaaaa','bbbbbbbbaab','aaa','bbbbbbbbb','bboabbbb'] 
list_pic=['a.png','12adcd.png','bcdaaaaaaa.png','bbbbbbbbaab.png','aaa.png','bbbbbbbbb.png','bboabbbb.png'] 


#@index=random.randint(0,6)

for i in range(0,6):
    text={'text':list_text[i]}

    file = {'my_image': open(list_pic[i],'rb')}

    response = requests.post('http://127.0.0.1:5000/upload_image', data=text,files=file) 
   # print(response.elapsed.total_seconds())

   # f = open("time.txt", "a")
#f.write("upload time: "+str(response.elapsed.total_seconds())+"\n")
   # f.write(str(response.elapsed.total_seconds())+"\n")
   # f.close()
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  4 19:09:53 2023

@author: Sam
"""

import requests 
import random

list_text=['uploadtest','uploadtest2','uploadtest3','uploadtest4','uploadtest5']
list_pic=['uploadtest.png','uploadtest2.png','uploadtest3.png','uploadtest4.png','uploadtest5.png']


index=random.randint(0,4)
text={'text':list_text[index]}

file = {'my_image': open(list_pic[index],'rb')}

response = requests.post('http://ec2-100-26-238-3.compute-1.amazonaws.com:5000/upload_image', data=text,files=file) 
print(response.elapsed.total_seconds())

f = open("time.txt", "a")
#f.write("upload time: "+str(response.elapsed.total_seconds())+"\n")
f.write(str(response.elapsed.total_seconds())+"\n")
f.close()
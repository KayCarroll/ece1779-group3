import subprocess
import time
import random
import requests 
request_list=[300]



for request in request_list:
    response = requests.post('http://127.0.0.1:5000//api/delete_all') 
    subprocess.run("python uploadall_dum.py & ", shell=True)
    total = 0
    f = open("time.txt", "w")
#f.write("Curre time: "+current_time+"\n")
    f.write(str(total)+"\n")
    f.close()
    command=""
    c_list=[]

    for i in range(0,(int)(request*0.2)):
        c_list.append(1)
    


    for i in range(0,(int)(request*0.8)):
        c_list.append(0)
  
    random.shuffle(c_list)
    print("Run request #: "+str(request))
    print(c_list)

    for c in c_list:
        if c == 0:
            command=command+"python show_dum.py & "
        elif c == 1:
            command=command+"python upload_dum.py & "

    #print(command)
    subprocess.run(command, shell=True)



    with open("time.txt") as log:
        for line in log:
            time=float(line)
            total+=time
        
    f = open("time_node2.txt", "a")
    #f.write("Curre time: "+current_time+"\n")
    f.write(str(request)+" Request Total: "+str(total)+"\n")
    f.close()        
        

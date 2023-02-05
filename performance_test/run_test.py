import subprocess
import time
import random
t = time.localtime()
current_time = time.strftime("%H:%M:%S", t)
print(current_time)
total = 0
f = open("time.txt", "w")
#f.write("Curre time: "+current_time+"\n")
f.write(str(total)+"\n")
f.close()


command=""
c_list=[]

for i in range(0,2*5):
    c_list.append(1)
    


for i in range(0,8*5):
    c_list.append(0)
  
random.shuffle(c_list)
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
        
f = open("time.txt", "a")
#f.write("Curre time: "+current_time+"\n")
f.write("Total: "+str(total)+"\n")
f.close()        
        

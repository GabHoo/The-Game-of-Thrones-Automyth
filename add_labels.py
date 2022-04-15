import re
#f = open('/Users/teresa/Desktop/Story-Generator/instance.txt')
#print(type(f))
#s = 'HERO:upset a HERO:Feelings.'
#print(re.findall(':', s))
#print(re.findall(r'(:)(.*?)', s))
myfile = open("all__instances.txt", "r")
myline = myfile.readlines()
"""f = open("mydocument.txt", mode = "a")
for line in myline:
    #print(line)

    k = line.split(" ")

    o = k[0].split(":")
    print(o)
    line2 = k[0] + " rdfs:label " + '"'+ (o[1] )+ '"'+ '.' + '\n'
    f.write(line)
    f.write(line2)

"""
#f.close()

'''with open('/Users/teresa/Desktop/Story-Generator/instance.txt') as f:
    print(f)
    for line in f:
        #print(line)

        k = line.split("")
        o = k.split(":")
        line = line + "\n" + k[0] + "rdfs:label" + "" + o[1] + ""
        print(line)'''

f=open("new_all_inst.txt",mode="a")
for line in myline:

    if "rdfs:label" in line and "_" in line:
        
        k = line.split(" ")
        k[2]=k[2].replace("_"," ")

        line2=k[0]+" "+k[1]+" "+k[2]
        f.write(line2)
    else:
        f.write(line)

f.close()
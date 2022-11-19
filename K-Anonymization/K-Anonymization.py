import random
#objects class
class record:
    def __init__(self) -> None:
        pass
    def Dim(self,k):
        if k==0:
            return self.Age
        elif k==1:
            return self.Gender
        elif k==2:
            return self.Marital
        elif k==3:
            return self.Race_Status
        elif k==4:
            return self.Birthplace
        elif k==5:
            return self.Language
        elif k==6:
            return self.Occupation
        elif k==7:
            return self.Income

    def __init__(self, Age, Gender, Marital, Race_Status, Birthplace, Language, Occupation, Income):
        self.Age=Age
        self.Gender=Gender
        self.Marital=Marital
        self.Race_Status=Race_Status
        self.Birthplace=Birthplace
        self.Language=Language
        self.Occupation=Occupation
        self.Income=Income
    def str(self):
        return "Age: {} , Gender: {} , Marital: {} , Race_Status: {} , Birthplace: {} , Language: {} , Occupation: {} , Income: {} K".format(self.Age, self.Gender, self.Marital, self.Race_Status, self.Birthplace, self.Language, self.Occupation, self.Income)
#reading list of records, from file.
path= "ipums.txt"        #change the path here
i=0
listAll= []              #list of all objects
with open(path, "r") as file:
    lines=file.readlines()
    for line in lines:
        rec=line.split()
        rec=record(int(rec[0]), int(rec[1]), int(rec[2]), int(rec[3]), int(rec[4]), int(rec[5]), int(rec[6]), int(rec[7]))
        listAll.append(rec)

#CreateQuasiList AND FindFreqSet are only two show the freqSet
def CreateQuasiList(list, Dim):
    New_List=[]
    for i in list:
        New_List.append(i.Dim(Dim))
    New_List=sorted(New_List)
    return New_List

def FindFreqSet(list):
    fs=[[],[]]
    for i in list:
        if i in fs[0]:
            fs[1][fs[0].index(i)]+=1
        else:
            fs[0].append(i)
            fs[1].append(1)
    return fs

#input:FreqSet
#output: freqSet with cumulative freq column
def FindCumulativeFreq(list):
    list2=list.copy()
    list2.append([])
    for i in list2[1]:
        if(len(list2[2])>0):
            list2[2].append(i+list2[2][-1])
        else:
            list2[2].append(list2[1][0])
    return list2

#input: freqSet with cumulative freq column, and original list of QusaiIdentifier
#output: median
def FindMedian(list, listQ):
    #last item in cumlative column is the total size of sample so we use it check for even or odd number of records.
    if(list[2][-1]%2==0):
        r=random.randint(1, 2)
        if r==1:
            return int(list[2][-1]/2)
        else:
            return int(list[2][-1]/2-1)
    else:
        return int(list[2][-1]/2-1)

#summary creation
def summary(list):
    list2=list.copy()
    list3=list.copy()
    maxlist=[]
    minlist=[]
    for i in range(7):
        listTemp=CreateQuasiList(list2, i)
        minlist.append(min(listTemp))
        maxlist.append(max(listTemp))

    for obj1 in list3:
        if(int(minlist[0])==int(maxlist[0])):
            obj1.Age="[{0}]".format(minlist[0])
        else:
            obj1.Age="[{0}-{1}]".format(minlist[0],maxlist[0])
        if(int(minlist[1])==int(maxlist[1])):
            obj1.Gender="[{0}]".format(minlist[1])
        else:
            obj1.Gender="[{0}-{1}]".format(minlist[1],maxlist[1])
        if(int(minlist[2])==int(maxlist[2])):
            obj1.Marital="[{0}]".format(minlist[2])
        else:
            obj1.Marital="[{0}-{1}]".format(minlist[2],maxlist[2])
        if(int(minlist[3])==int(maxlist[3])):
            obj1.Race_Status="[{0}]".format(minlist[3])
        else:
            obj1.Race_Status="[{0}-{1}]".format(minlist[3],maxlist[3])
        if(int(minlist[4])==int(maxlist[4])):
            obj1.Birthplace="[{0}]".format(minlist[4])
        else:
            obj1.Birthplace="[{0}-{1}]".format(minlist[4],maxlist[4])
        if(int(minlist[5])==int(maxlist[5])):
            obj1.Language="[{0}]".format(minlist[5])
        else:
            obj1.Language="[{0}-{1}]".format(minlist[5],maxlist[5])
        if(int(minlist[6])==int(maxlist[6])):
            obj1.Occupation="[{0}]".format(minlist[6])
        else:
            obj1.Occupation="[{0}-{1}]".format(minlist[6],maxlist[6])
    
    return list3

def Anonymize(list, k):
    #if cut is not allowed
    if int(len(list)/2)<k:
        list=summary(list)
        #return the partition with summary
        return list
    else:
        #if cut is allowed
        Dim=random.randint(0,6)
        list2=list.copy()
        SplitVal=FindMedian(FindCumulativeFreq(FindFreqSet(CreateQuasiList(list2, Dim))),list2)
        list = sorted(list, key=lambda record: record.Dim(Dim))
        
        #split lhs, rhs find the anonymization of it, then find the union of both lists
        Max=SplitVal
        Min=SplitVal
        Lhs=list[:Max]
        Rhs=list[Min:]
        return Anonymize(Lhs, k)+(Anonymize(Rhs,k))


#this is code will do all the work.
for i in Anonymize(listAll, 3):
    print(i.str())
import csv
from collections import defaultdict, Counter
import pandas as pd
from apyori import apriori
from itertools import combinations
from matplotlib import pyplot as plt

moviesCSV = open("movies.csv", "r", encoding="utf8")
moviesRows = []
moviesFields = []
moviesReader = csv.reader(moviesCSV)
moviesFields = next(moviesReader)
for row in moviesReader:
    moviesRows.append(row)

ratingsCSV = open("ratings.csv", "r", encoding="utf8")
ratingsRows = []
ratingsFields = []
ratingsReader = csv.reader(ratingsCSV)
ratingsFields = next(ratingsReader)
for row in ratingsReader:
    ratingsRows.append(row)
    
linksCSV = open("links.csv", "r", encoding="utf8")
linksRows = []
linksFields = []
linksReader = csv.reader(linksCSV)
linksFields = next(linksReader)
for row in linksReader:
    linksRows.append(row)

tagsCSV = open("tags.csv", "r", encoding="utf8")
tagsRows = []
tagsFields = []
tagsReader = csv.reader(tagsCSV)
tagsFields = next(tagsReader)
for row in tagsReader:
    tagsRows.append(row)
    
def idToMovieName(movieID):
    for movieRow in moviesRows:
        if movieRow[0] == movieID:
            return " ".join(movieRow[1].split(" ")[:-1])
        
ratingsTDSDict = defaultdict(list)
for rating in ratingsRows:
    if float(rating[2]) > 2:
        ratingsTDSDict[rating[0]].append(idToMovieName(rating[1]))
        
fewerThan10 = []
for key, value in ratingsTDSDict.items():
    if len(value) <= 10:
        fewerThan10.append(key)
for key in fewerThan10:
    del ratingsTDSDict[key]
    
ratingsTrainingSet = {}
ratingsTestSet = {}
for key, value in ratingsTDSDict.items():
    xrange = int(len(value) * 0.8)
    ratingsTrainingSet[key] = value[0:xrange]
    ratingsTestSet[key] = value[xrange:-1]
    
data = []
for key, value in ratingsTrainingSet.items():
    data.append([key, value])
    
init = []
for i in data:
    for q in i[1]:
        if(q not in init):
            init.append(q)
init = sorted(init)

min_support = 0.0148
support = int(min_support * len(init))

current_counter = defaultdict(int)
for i in init:
    for d in data:
        if(i in d[1]):
            current_counter[i]+=1
# print("Current 1:")
# for i in current_counter:
#     print(str([i])+": "+str(current_counter[i]))

next_counter = defaultdict(int)
for i in current_counter:
    if(current_counter[i] >= support):
        next_counter[frozenset([i])]+=current_counter[i]
print("Level (Next) 1:")
for i in next_counter:
    print(str(list(i))+": "+str(next_counter[i]))
print()

current_remaining = next_counter
final_remaining = 1

for count in range (2, 7):
    
    nc = set()
    temp = list(next_counter)
    for i in range(0,len(temp)):
        for j in range(i + 1,len(temp)):
            t = temp[i].union(temp[j])
            if(len(t) == count):
                nc.add(temp[i].union(temp[j]))
    nc = list(nc)
    
    current_counter = defaultdict(int)
    for i in nc:
        current_counter[i] = 0
        for q in data:
            temp = set(q[1])
            if(i.issubset(temp)):
                current_counter[i]+=1
    # print("Current "+str(count)+":")
    # for i in current_counter:
    #     print(str(list(i))+": "+str(current_counter[i]))
    # print()
    
    next_counter = defaultdict(int)
    for i in current_counter:
        if(current_counter[i] >= support):
            next_counter[i]+=current_counter[i]
    if(len(next_counter) == 0):
        break
    print("Level (Next) "+str(count)+":")
    for i in next_counter:
        print(str(list(i))+": "+str(next_counter[i]))
    print()
    
    current_remaining = next_counter
    final_remaining = count
    
print("Result: ")
print("Level (Next) "+str(final_remaining)+":")
for i in current_remaining:
    print(str(list(i))+": "+str(current_remaining[i]))
print()

conf_100 = []
conf_no = []
conf_all = []

for next_counter in current_remaining:
    current_counter = [frozenset(q) for q in combinations(next_counter,len(next_counter)-1)]
    mmax = 0
    for movie in current_counter:
        without_movie = next_counter-movie
        movie_counter = next_counter
        total_percentage = 0
        singular_percentage = 0
        plural_percentage = 0
        for q in data:
            temp = set(q[1])
            if(movie.issubset(temp)):
                singular_percentage+=1
            if(without_movie.issubset(temp)):
                plural_percentage+=1
            if(movie_counter.issubset(temp)):
                total_percentage+=1
        temp = total_percentage/singular_percentage*100
        if(temp > mmax):
            mmax = temp
        temp = total_percentage/plural_percentage*100
        if(temp > mmax):
            mmax = temp
#         print(str(list(movie))+" -> "+str(list(without_movie))+" = "+str(total_percentage/singular_percentage*100)+"%")
        print(str(list(without_movie))+" -> "+str(list(movie))+" = "+str(total_percentage/plural_percentage*100)+"%")
        listString = [without_movie, list(movie), total_percentage / plural_percentage * 100]
        conf_all.append(listString)
        if float(listString[-1]) > 35:
            conf_100.append(listString)
        else:
            conf_no.append(listString)
    curr = 1
#     print("choosing:", end=' ')
    for movie in current_counter:
        without_movie = next_counter-movie
        movie_counter = next_counter
        total_percentage = 0
        singular_percentage = 0
        plural_percentage = 0
        for q in data:
            temp = set(q[1])
            if(movie.issubset(temp)):
                singular_percentage += 1
            if(without_movie.issubset(temp)):
                plural_percentage += 1
            if(movie_counter.issubset(temp)):
                total_percentage += 1
        temp = total_percentage / singular_percentage * 100
#         if(temp == mmax):
#             print(curr, end = ' ')
        curr += 1
        temp = total_percentage / plural_percentage * 100
#         if(temp == mmax):
#             print(curr, end = ' ')
        curr += 1
    print("\n")
    
for key, value in ratingsTestSet.items():
    if "Matrix, The" in value:
        print(key)
        
for i in conf_100:
    i[0] = list(i[0])
setNeeded = []
for i in conf_100:
#     print(i[0][0])
#     if i[0][0] in ratingsTestSet["276"] or i[0][0] in ratingsTestSet["232"]:
#     for count in range(1, 11):
    if i[0][0] == "Star Wars: Episode V - The Empire Strikes Back":
        print(i[0][0], "->", i[1])
#         print(set(i[1]))
        setNeeded += i[1]
list(set(setNeeded))

rec1 = ['Matrix, The', 'Star Wars: Episode IV - A New Hope', 'Star Wars: Episode VI - Return of the Jedi']
rec2 = list(set(rec1 + ['Terminator 2: Judgment Day', 'Star Wars: Episode IV - A New Hope', 'Star Wars: Episode VI - Return of the Jedi']))
rec3 = list(set(rec2 + ['Pulp Fiction', 'Shawshank Redemption, The', 'Star Wars: Episode IV - A New Hope']))
rec4 = list(set(rec3 + ['Forrest Gump', 'Star Wars: Episode IV - A New Hope', 'Star Wars: Episode VI - Return of the Jedi']))
rec5 = list(set(rec4 + ['Matrix, The', 'Forrest Gump', 'Star Wars: Episode VI - Return of the Jedi']))
rec6 = list(set(rec5 + ['Pulp Fiction', 'Star Wars: Episode IV - A New Hope', 'Star Wars: Episode VI - Return of the Jedi']))
rec7 = list(set(rec6 + ['Forrest Gump', 'Star Wars: Episode IV - A New Hope', 'Raiders of the Lost Ark (Indiana Jones and the Raiders of the Lost Ark)']))
rec8 = list(set(rec7 + ['Forrest Gump', 'Star Wars: Episode IV - A New Hope', 'Matrix, The']))
rec9 = list(set(rec8 + ['Pulp Fiction', 'Star Wars: Episode IV - A New Hope', 'Matrix, The']))
rec10 = list(set(rec9 + ['Shawshank Redemption, The', 'Star Wars: Episode IV - A New Hope', 'Matrix, The']))

recList = list(set(ratingsTestSet["32"] + ratingsTestSet["276"]))

x_axis = []
count = 0
for i in rec1:
    if i in recList:
        count += 1
x_axis.append(count)
count = 0
for i in rec2:
    if i in recList:
        count += 1
x_axis.append(count)
count = 0
for i in rec3:
    if i in recList:
        count += 1
x_axis.append(count)
count = 0
for i in rec4:
    if i in recList:
        count += 1
x_axis.append(count)
count = 0
for i in rec5:
    if i in recList:
        count += 1
x_axis.append(count)
count = 0
for i in rec6:
    if i in recList:
        count += 1
x_axis.append(count)
count = 0
for i in rec7:
    if i in recList:
        count += 1
x_axis.append(count)
count = 0
for i in rec8:
    if i in recList:
        count += 1
x_axis.append(count)
for i in rec9:
    if i in recList:
        count += 1
x_axis.append(count)
x_axis.append(count)

x = [i / len(recList) for i in x_axis]

y = [i for i in range(1, 11)]
  
plt.plot(y, x)
plt.xlabel("Number of rules")
plt.ylabel("Recall")
plt.title("Recall VS Rules")
plt.show()

x = []
x.append(x_axis[0] / len(rec1))
x.append(x_axis[1] / len(rec2))
x.append(x_axis[2] / len(rec3))
x.append(x_axis[3] / len(rec4))
x.append(x_axis[4] / len(rec5))
x.append(x_axis[5] / len(rec6))
x.append(x_axis[6] / len(rec7))
x.append(x_axis[7] / len(rec8))
x.append(x_axis[8] / len(rec9))
x.append(x_axis[9] / len(rec10))

y = [i for i in range(1, 11)]
  
plt.plot(y, x)
plt.xlabel("Number of rules")
plt.ylabel("Precision")
plt.title("Precision VS Rules")
plt.show()
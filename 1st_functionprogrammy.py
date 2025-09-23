students = [
    {"name": "Alice", "age": 20, "grades": [85, 90, 88, 92]},
    {"name": "Bob", "age": 22, "grades": [78, 89, 76, 85]},
    {"name": "Charlie", "age": 21, "grades": [92, 95, 88, 94]},
    {"name": "David", "age": 19, "grades": [67, 72, 75, 68]},
    {"name": "Emma", "age": 20, "grades": [91, 87, 93, 89]},
    {"name": "Frank", "age": 23, "grades": [82, 79, 85, 88]},
    {"name": "Grace", "age": 21, "grades": [95, 96, 92, 94]},
    {"name": "Henry", "age": 20, "grades": [73, 68, 75, 70]},
    {"name": "Isabella", "age": 22, "grades": [88, 85, 90, 87]},
    {"name": "Jack", "age": 19, "grades": [79, 82, 76, 81]},
    {"name": "Katherine", "age": 21, "grades": [93, 89, 91, 95]},
    {"name": "Liam", "age": 20, "grades": [84, 87, 82, 86]},
    {"name": "Mia", "age": 22, "grades": [76, 80, 78, 82]},
    {"name": "Noah", "age": 21, "grades": [89, 92, 87, 90]},
    {"name": "Olivia", "age": 20, "grades": [94, 90, 92, 96]},
    {"name": "Peter", "age": 23, "grades": [81, 78, 84, 79]},
    {"name": "Quinn", "age": 19, "grades": [70, 75, 72, 68]},
    {"name": "Rachel", "age": 21, "grades": [86, 89, 84, 88]},
    {"name": "Samuel", "age": 20, "grades": [90, 87, 92, 89]},
    {"name": "Taylor", "age": 22, "grades": [83, 86, 80, 85]}
]

count = 20

def ageIsappropriate (arg):
    if arg["age"] >=20 and  arg["age"] <= 23:
        return arg
students_filter =[list(filter(ageIsappropriate, students))]
def averageScore(arg):
    res= sum(arg["grades"])
    return {"name": arg["name"],"averageScore" : res/4}
print(students_filter)
averageScorelist = (list(map(averageScore,students)))
print (averageScorelist)
res=0
for i in range(count):
    a=averageScorelist[i]
    res+=a["averageScore"]
res/=20
maxl=0
for i in range(count):
    a = averageScorelist[i]
    if a["averageScore"] >= maxl:
        maxl =a["averageScore"]
print("AllaverageScore :", res)
for i in range(count):
    a = averageScorelist[i]
    if a["averageScore"] == maxl:
        print("Best student :", a["name"])



def expensesScore(arg):
    res= sum(arg["expenses"])
    return {"name": arg["name"],"expensesScore" : res}

def expensesIsappropriate (arg):
    if arg["expensesScore"] >=350:
        return arg

users = [
    {"name": "Alice", "expenses": [100, 50, 75, 200]},
    {"name": "Bob", "expenses": [50, 75, 80, 100]},
    {"name": "Charlie", "expenses": [200, 300, 50, 150]},
    {"name": "David", "expenses": [100, 200, 300, 400]},
    {"name": "Emma", "expenses": [150, 80, 120, 90]},
    {"name": "Frank", "expenses": [75, 60, 45, 110]},
    {"name": "Grace", "expenses": [250, 180, 220, 190]},
    {"name": "Henry", "expenses": [95, 130, 70, 85]},
    {"name": "Isabella", "expenses": [300, 150, 200, 175]},
    {"name": "Jack", "expenses": [40, 65, 55, 75]},
    {"name": "Katherine", "expenses": [180, 220, 160, 140]},
    {"name": "Liam", "expenses": [120, 90, 110, 130]},
    {"name": "Mia", "expenses": [85, 95, 105, 115]},
    {"name": "Noah", "expenses": [210, 170, 190, 230]},
    {"name": "Olivia", "expenses": [60, 85, 70, 95]},
    {"name": "Peter", "expenses": [140, 160, 125, 145]},
    {"name": "Quinn", "expenses": [175, 195, 155, 165]},
    {"name": "Rachel", "expenses": [110, 135, 145, 120]},
    {"name": "Samuel", "expenses": [230, 205, 215, 195]},
    {"name": "Taylor", "expenses": [125, 140, 115, 130]}
]
scoreusers=list(map(expensesScore, users))
print(scoreusers)
filterusers=list(filter(expensesIsappropriate,scoreusers))
print(filterusers)
suml=0
for i in range(len(filterusers)):
    suml+=filterusers[i]["expensesScore"]
print("allsum :",suml)





orders = [
    {"order_id": 1, "customer_id": 101, "amount": 150.0},
    {"order_id": 2, "customer_id": 102, "amount": 200.0},
    {"order_id": 3, "customer_id": 101, "amount": 75.0},
    {"order_id": 4, "customer_id": 103, "amount": 100.0},
    {"order_id": 5, "customer_id": 101, "amount": 50.0},
    {"order_id": 6, "customer_id": 104, "amount": 300.0},
    {"order_id": 7, "customer_id": 102, "amount": 125.0},
    {"order_id": 8, "customer_id": 105, "amount": 80.0},
    {"order_id": 9, "customer_id": 103, "amount": 225.0},
    {"order_id": 10, "customer_id": 101, "amount": 175.0},
    {"order_id": 11, "customer_id": 106, "amount": 90.0},
    {"order_id": 12, "customer_id": 104, "amount": 140.0},
    {"order_id": 13, "customer_id": 102, "amount": 60.0},
    {"order_id": 14, "customer_id": 107, "amount": 250.0},
    {"order_id": 15, "customer_id": 105, "amount": 110.0},
    {"order_id": 16, "customer_id": 101, "amount": 195.0},
    {"order_id": 17, "customer_id": 103, "amount": 70.0},
    {"order_id": 18, "customer_id": 108, "amount": 180.0},
    {"order_id": 19, "customer_id": 106, "amount": 130.0},
    {"order_id": 20, "customer_id": 102, "amount": 210.0}
]

idd= int(input())

def filterid(arg):
    if idd==arg["customer_id"]:
        return arg["amount"]
client=list(filter(filterid,orders))
print(client)
cnt=len(client)
suuml=0
for i in range(cnt):
    suuml+=client[i]["amount"]
print("ALLamount :", suuml)
print("ALLamount :", suuml/cnt)
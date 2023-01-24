from random import randint

f1 = open("./2007_train.txt", 'w', encoding='utf-8')
with open("./2007_train1.txt", encoding='utf-8') as f:
    for line in f.readlines():
        if randint(0, 10) == 0:
            f1.write(line)

f.close()

import itertools
arl = []
x = itertools.product('TBANK', repeat=13)
for t  in x:
    i = ''.join(t)
    print(i)
    if "BB" not in i and "BA" not in i and "BN" not in i and "BK" not in i and "AB" not in i and "AA" not in i and "AN" not in i and "AK" not in i and "NB" not in i and "NK" not in i and "NN" not in i and "NA" not in i and "KB" not in i and "KN" not in i and "KK" not in i and "KA" not in i:
        arl.append(i)
print(arl)
print(len(arl))

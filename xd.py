S = []
for i, st in enumerate(open('9.txt').readlines()):
    li = list(map(int, st.split()))
    v_0 = list(filter(lambda x: li.count(x)==1, li))
    v_1 = list(filter(lambda x: li.count(x)==3, li))
    if len(v_0) == 4 and v_1 and sum(v_0)/4 <= v_1[0] and max(li)%min(li):
        S.append([sum(li), i+1])
print(sorted(S))
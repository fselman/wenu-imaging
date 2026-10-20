idx_selected = []

for i in range(1,11):
    if not (i in idx_selected or not idx_selected):
        continue
    print(i)

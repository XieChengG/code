def triangle(max):
    t, n = [1], 0
    while n < max:
        yield t
        t.append(0)
        tmp = []
        for i in range(len(t)):
            tmp.append(t[i - 1] + t[i])
        t = tmp
        n += 1
    return "Done"


tri = triangle(5)
while True:
    try:
        tr = tri.__next__()
        print(tr)
    except StopIteration as e:
        break

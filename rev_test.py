M = [i+1 for i in range(6500)]
i = 1000 # < max(M)
t = 1 # 0 <= t <= 1
r = 0 # < max(M)
w = 0.1 # 0 < w < 1

def B(t, r):
	global i, M
	
	return i+t*(max(M)-i)-r

def R(n):
    global r, w

    for i in range(n):
        b = B(t, r)
        r += b-(b*(1-w))
        print(b)

R(100)
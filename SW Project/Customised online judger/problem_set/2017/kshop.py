# Arup Guha
# 8/27/2017
# Solution to 2017 UCF Locals Problem: K Shop
# Converted to Python from C++

import math

# Constants
MOD = 997
MAX = 50000
POLYLEN = (1<<17)

# Globals.
order = [0,1]

# Just iterate building next array from previous.
while len(order) != POLYLEN:
    tmp = [0]*(len(order)<<1)
    for i in range(len(order)):
        tmp[2*i] = order[i]
        tmp[2*i+1] = order[i] + len(order)
    order = tmp;
         
# Fill out sin and cos values for fft.
cosarr = [0]*POLYLEN
for i in range(POLYLEN):
    cosarr[i] = math.cos(i*2*math.pi/POLYLEN)
sinarr = [0]*POLYLEN
for i in range(POLYLEN):
    sinarr[i] = math.sin(i*2*math.pi/POLYLEN)
	

def main():

    numCases = int(input(""))
    
    # Process each case.
    for loop in range(numCases):

        # Read in the polynomial.
        poly = [0]*POLYLEN;
        n = int(input(""))    
        for i in range(n):
            price = float(input(""))
            poly[int(100*price + .1)]+=1   
        
        # Read in exponent and number of queries.
        toks = input("").split()
        exp = int(toks[0])
        numQ = int(toks[1])
        
        # Exponentiate our polynomial.
        res = mypow(poly, exp);
        
        # Now handle the queries.
        for i in range(numQ):
            price = float(input(""))
            print(res[(int)(100*price + .1)])            
        print()

# Raises poly to the exp using our MOD and lopping off appropriate terms.
def mypow(poly, exp):
    
    # Done.    
    if exp == 1:
        return poly
    
    # Get the time savings here.
    if exp%2 == 0:
        halfway = mypow(poly, exp/2)
        res = multiply(halfway, halfway)
        return scale(res)
    
    # Slow way, never runs twice in a row.
    rest = mypow(poly, exp-1)
    res = multiply(rest, poly)
    return scale(res)

# Scales the polynomial arr - lops off terms past MAX and does MOD.
def scale(arr):
    res = [0]*POLYLEN
    for i in range(MAX+1):
        res[i] = arr[i]%MOD
    return res;    

# Here is the FFT!
def fft(real, img, invert):

    # Re-order numbers to be in fft ordering for combination.
    tmp = [0]*POLYLEN
    for i in range(POLYLEN):
        tmp[i] = real[order[i]];
    for i in range(POLYLEN):
        real[i] = tmp[i];
    
    tmp = [0]*POLYLEN
    for i in range(POLYLEN):
        tmp[i] = img[order[i]];
    for i in range(POLYLEN):
        img[i] = tmp[i];
    
    # size is the size of each grouping (when we combine up) in fft.
    size = 2
    while size <= POLYLEN:

        half = size >> 1
        skip = POLYLEN//size
        sign = 1
        if invert:
            sign = -1
            
        for i in range(0, POLYLEN, size):
            aReal = 1
            aImg = 0
            index = 0
            for j in range(half):
                fReal = real[i+j]
                fImg = img[i+j]
                sReal = real[i+j+half]*cosarr[index] - img[i+j+half]*sinarr[index]
                sImg = img[i+j+half]*cosarr[index] + real[i+j+half]*sinarr[index]
                real[i+j] = fReal + sReal
                img[i+j] = fImg + sImg
                real[i+j+half] = fReal - sReal
                img[i+j+half] = fImg - sImg
                index = (index+sign*skip+POLYLEN)%POLYLEN
        size <<= 1

    # For inverse transformation, we divide by n (my len).
    if invert:
        for i in range(POLYLEN):
            real[i] /= POLYLEN
            img[i] /= POLYLEN

def multiply(a, b):

    # Copy a.
    reala = [0]*POLYLEN
    for i in range(POLYLEN):
        reala[i] = a[i]
    imga = [0.0]*POLYLEN

    # Copy b.
    realb = [0]*POLYLEN
    for i in range(POLYLEN):
        realb[i] = b[i]
    imgb = [0.0]*POLYLEN
    
    # Transform into points.
    fft(reala, imga, False)
    fft(realb, imgb, False)

    # Store product pts here.
    realPts = [0.0]*POLYLEN
    imgPts = [0.0]*POLYLEN

    # Multiply points.
    for i in range(POLYLEN):
        realPts[i] = reala[i]*realb[i] - imga[i]*imgb[i]
        imgPts[i] = reala[i]*imgb[i] + realb[i]*imga[i]
        
    # Now, convert these points back to a polynomial.
    fft(realPts, imgPts, True)

    # Finally copy over into a result array without doubles.
    res = [0]*POLYLEN
    for i in range(POLYLEN):
        res[i] = int(realPts[i] + .5)
    return res

# Run it!
main()

/*
Problem: Multiples (UCF Local 2017)
Author: Shahidul Islam (Sumon)
*/

#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#include<math.h>

#define PRIME_RANGE 130
#define PRIME_CNT   32

#define UPPER_LIMIT (1000000000000000ull) //10^15
#define MAX_BASE_MULTIPLES_COUNT  25000000

typedef struct
{
    char primeFactorFlag;
    long long multiple;
}multipleInfo;

unsigned char primeFlag[PRIME_RANGE + 1];
int primes[PRIME_CNT];
int primeCnt = 0;

int maxPrimeStart[PRIME_CNT];
multipleInfo baseMultiples[MAX_BASE_MULTIPLES_COUNT];
multipleInfo mergedMultiples[MAX_BASE_MULTIPLES_COUNT];
int baseMultiplesCount, mergedMultiplesCount;

void findOddMultiples(int a, long long b, long long *count);
void generateBaseMultiples(void);
void mergeLists(multipleInfo listSource[], int countS, multipleInfo listDest[], int *countD);
void sieve(void);

int main(void)
{

    int i, j, a, n, startInd, endInd;
    long long b, multiples;

    //Generate primes
    sieve();
    primes[primeCnt] = PRIME_RANGE + 1;

    generateBaseMultiples();
    baseMultiples[baseMultiplesCount].multiple = UPPER_LIMIT + 1;

    //Input and Output
    scanf("%d", &n);
    for(i = 1; i <= n; i++)
    {
        scanf("%d%lld", &a, &b);

        //If b <= a, all are multiple except 1
        if(b <= a)
            printf("%lld\n",b-1);
        else
        {
            //Add all even multiples
            multiples = b / 2;
            //Add all odd multiples
            findOddMultiples(a, b, &multiples);-

            printf("%lld\n", multiples);
        }
    }
    return 0;
}

void findOddMultiples(int a, long long b, long long *count)
{
    int i, k;
    long long currentNum;

    for(k = 1; k < primeCnt && primes[k] <= a; k++)
    {
        for(i = maxPrimeStart[k]; i < maxPrimeStart[k + 1] && baseMultiples[i].multiple <= b; i++)
        {
            currentNum = b/baseMultiples[i].multiple;
            currentNum = (currentNum  + 1) >> 1; // remove even multiples
            if(baseMultiples[i].primeFactorFlag) //odd number of factors
                (*count) += currentNum;
            else
                (*count) -= currentNum;
        }
    }
}

void addTheMultiple(long long value, int primeFactorFlag)
{
    baseMultiples[baseMultiplesCount].multiple = value;
    baseMultiples[baseMultiplesCount].primeFactorFlag = primeFactorFlag;
    baseMultiplesCount++;
}

void generateBaseMultiples(void)
{
    int i, j, t, prevCount;
    long long curValue;

    addTheMultiple(3, 1);
    mergedMultiples[0] = baseMultiples[0];
    mergedMultiplesCount = 1;

    maxPrimeStart[1] = 0;
    prevCount = mergedMultiplesCount;
    for(i = 2; i < primeCnt; i++)
    {
        maxPrimeStart[i] = baseMultiplesCount;
        addTheMultiple(primes[i], 1);
        for(j = 0; j < prevCount; j++)
        {
            curValue = mergedMultiples[j].multiple * primes[i];
            if(curValue > UPPER_LIMIT)
                break;

            addTheMultiple(curValue, 1 - mergedMultiples[j].primeFactorFlag);
        }
        if(i < primeCnt - 1)
            mergeLists(&baseMultiples[prevCount], baseMultiplesCount - prevCount, mergedMultiples, &mergedMultiplesCount);

        prevCount = mergedMultiplesCount;
    }
    maxPrimeStart[primeCnt] = baseMultiplesCount;
}

void mergeLists(multipleInfo listSource[], int countS, multipleInfo listDest[], int *countD)
{
    int limit = countS + *countD;
    int i1, i2, j, k;

    //Copy one list in unused safe memory
    for(j = limit - 1, k = *countD - 1; k >= 0; j--, k--)
        listDest[j] = listDest[k];

    //Merge the lists
    for(i1 = 0, i2 = countS, k = 0; i1 < countS && i2 < limit; k++)
    {

        if(listSource[i1].multiple <= listDest[i2].multiple)
            listDest[k] = listSource[i1++];
        else
            listDest[k] = listDest[i2++];
    }

    while(i1 < countS)
        listDest[k++] = listSource[i1++];


    while(i2 < limit)
        listDest[k++] = listDest[i2++];

    *countD = k;
}

void sieve(void)
{
    int i, j, root = sqrt(PRIME_RANGE);
    primes[primeCnt++] = 2;
    for(i = 3; i <= PRIME_RANGE; i+= 2)
    {
        if(!primeFlag[i])
        {
            primes[primeCnt++] = i;
            if(root >= i)
            {
                for(j = i * i; j <= PRIME_RANGE; j += i << 1)
                    primeFlag[j] = 1;
            }
        }
    }
}

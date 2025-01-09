/*
Problem: Count the Dividing Pairs (UCF Local 2016)
Author: Shahidul Islam (Sumon)
*/

#include<stdio.h>
#include<string.h>

#define ARRAY_SZ 1000001
#define FREQ_SZ 10000001

int a[ARRAY_SZ];
int freq[FREQ_SZ];

long long bigMultiply(int a, int b)
{
    long long res = a;
    res *= b;
    return res;
}

int main(void)
{
    //freopen("divide.in", "r", stdin);
    //freopen("divide.ans", "w", stdout);
    int i, j, k, n, p;
    int limit, max;
    long long count;
    scanf("%d", &n);
    for(i = 1; i <= n; i++)
    {
        printf("Test case #%d: ", i);
        scanf("%d", &p);
        //Initialize memories
        count = max = 0;
        memset(freq, 0, FREQ_SZ * sizeof(int));

        //Take input, set frequencies and find max
        for(j = 0; j < p; j++)
        {
            scanf("%d", &a[j]);
            freq[a[j]]++;
            if(max < a[j])
                max = a[j];
        }

        //Count for (0, Aj)
        count = bigMultiply(freq[0], p - freq[0]);
        //Count for (1, Aj)
        count += bigMultiply(freq[1], p - freq[0] - freq[1]);

        //Count (Di, Aj) for Di > 1
        //Consider all numbers, and find the available multiples
        for(j = 2; j <= max/2; j++)
        {
            if(freq[j])
            {
                for(k = j + j; k <= max; k += j)
                {
                    if(freq[k])
                        count += bigMultiply(freq[j], freq[k]);
                }
            }
        }
        printf("%lld\n\n", count);
    }
    return 0;
}

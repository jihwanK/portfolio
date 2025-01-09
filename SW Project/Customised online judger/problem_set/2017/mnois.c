/*
Problem: Maximum Non-Overlapping Increasing Subsequences (UCF Local 2017)
Author: Shahidul Islam (Sumon)
*/

#include<stdio.h>
#include<stdlib.h>
#include<string.h>

#define ARRAY_SZ 101

int array[ARRAY_SZ];
int lisArray[ARRAY_SZ];
int pairwiseLIS[ARRAY_SZ][ARRAY_SZ];
int matrix[ARRAY_SZ][ARRAY_SZ][ARRAY_SZ];

int lis(int *array, int count);
void parenthesize(int array[], int count);

int main()
{
    freopen("mnois.in", "r", stdin);

    int i, j, n, m, optParenthesis;

    //Input and Output
    scanf("%d", &n);
    for(i = 1; i <= n; i++)
    {
        scanf("%d", &m);
        for(j = 0; j < m; j++)
            scanf("%d", &array[j]);

        parenthesize(array, m);

        printf("%d", matrix[0][0][m-1]);
        for(j = 1; j < m; j++)
            printf(" %d", matrix[j][0][m-1]);
        printf("\n");
    }
    return 0;
}

//Find the optimal parenthesization
void parenthesize(int array[], int count)
{
    int len, i, j, k, l, elements, lisValue;

    //Calculate LIS length for all pair of indices
    for(i = 0; i < count; i++)
        for(j = i; j < count; j++)
            pairwiseLIS[i][j] = lis(&array[i], j - i + 1);

    lisValue = pairwiseLIS[0][count - 1];

    //initialize the matrix for 1 element K > 1
    for(k = 0; k < count; k++)
        for (i = 0; i < count; i++)
            for (j = i; j < count; j++)
                matrix[k][i][j] = 0;

    //for K = 1, result is number of total elements
    matrix[0][0][count - 1] = count;

    //Generate the optimal parenthesization for all K
    for(k = 1; k < lisValue; k++)
    {
        for (i = count - 1; i >= 0; i--)
        {
            for (j = i + 1; j < count; j++)
            {
                if(pairwiseLIS[i][j] >= k + 1)
                    matrix[k][i][j] = pairwiseLIS[i][j];
                else
                    matrix[k][i][j] = 0;

                for (l = i; l < j; l++)
                {
                    elements = matrix[k][i][l] + matrix[k][l+1][j];
                    if (elements > matrix[k][i][j])
                        matrix[k][i][j] = elements;
                }
            }
        }
    }
}

//Calculate LIS length from count items in array
int lis(int *array, int count)
{
    int i, j, len = 0, lo, hi, mid;
    for(i = 0; i < count; i++)
    {
        lo = -1;
        hi = len;
        while(lo < hi - 1)
        {
            mid = (lo + hi) / 2;
            if(lisArray[mid] < array[i])
                lo = mid;
            else
                hi = mid;
        }
        lisArray[hi] = array[i];
        if(hi == len)
            len++;
    }
    return len;
}

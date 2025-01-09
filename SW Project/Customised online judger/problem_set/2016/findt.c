/*
Problem: Dot the i?s and Cross the T?s (UCF Local 2016)
Author: Shahidul Islam (Sumon)
*/

#include<stdio.h>
#include<math.h>
#include<string.h>
#include<stdlib.h>

#define ARRAY_SZ 50
#define ERR 1e-6
#define fabs(a) (a < 0 ? -(a) : a)
#define square(a) ((a) * (a))

typedef struct
{
    double x;
    double y;
}point;

point list[ARRAY_SZ];

double distance(point a, point b);
int testT(point a, point b, point m, point c);
int isEqual(double a, double b);


int main(void)
{
    //freopen("findt.in", "r", stdin);
    //freopen("findt.ans", "w", stdout);
    int n, p, count;
    int i, j, k1, k2, k3, k4;
    scanf("%d", &n);
    for(i = 1; i <= n; i++)
    {
        printf("Set #%d: ", i);
        scanf("%d", &p);

        //Take input
        for(j = 0; j < p; j++)
            scanf("%lf %lf", &list[j].x, &list[j].y);

        //Try all possible 4 points that can form a unique T
        count = 0;
        for(k1 = 0; k1 < p; k1++)
            for(k2 = k1 + 1; k2 < p; k2++)
                for(k3 = 0; k3 < p; k3++)
                    if(k1 != k3 && k2 != k3)
                        for(k4 = 0; k4 < p; k4++)
                            if(k1 != k4 && k2 != k4 && k3 != k4)
                            {
                                if(testT(list[k1], list[k2], list[k3], list[k4]))
                                    count++;
                            }


        printf("%d\n\n", count);
    }
    return 0;
}

//Calculate distance between points a and b
double distance(point a, point b)
{
    return sqrt(square(a.x - b.x) + square(a.y - b.y));
}

//Return if 2 double values are equal
int isEqual(double a, double b)
{
    if(fabs(a - b) < ERR)
        return 1;
    return 0;
}

//Test if given points A, M, B and C forms a T
int testT(point a, point b, point m, point c)
{
    double ab, am, mc, ac;
    point midAB;
    midAB.x = (a.x + b.x) / 2;
    midAB.y = (a.y + b.y) / 2;

    //Test if M is midpoint of AB
    if(isEqual(midAB.x, m.x) && isEqual(midAB.y, m.y))
    {
        ab = distance(a, b);
        mc = distance(m, c);

        //Test if CM = AB
        if(isEqual(ab, mc))
        {
            am = ab/2;
            ac = distance(a, c);

            //Test right angle using Pythagorean Theorem
            if(isEqual(square(am) + square(mc), square(ac)))
                return 1;
        }
    }
    return 0;
}

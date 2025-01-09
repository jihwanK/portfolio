#include <stdio.h>
#include <math.h>


typedef struct
{
    double x;
    double y;
}point;

void calculatePerimeters(point polycake[], int v, int y, double *perimeters1, double *perimeters2);

int main()
{
    point polycake[11];
    int n, v, y, i, t;
    double perimeters1, perimeters2;
    scanf("%d", &n);
    for(t = 1; t <= n; t++)
    {
        scanf("%d %d", &v, &y);
        for(i = 0; i < v; i++)
            scanf("%lf %lf", &polycake[i].x, &polycake[i].y);
        calculatePerimeters(polycake, v, y, &perimeters1, &perimeters2);
        if(perimeters2 > perimeters1)
            printf("%.3lf %.3lf\n", perimeters1, perimeters2);
        else
            printf("%.3lf %.3lf\n", perimeters2, perimeters1);
    }
    return 0;
}

double distance(point a, point b)
{
    return sqrt((a.x - b.x) * (a.x - b.x) + (a.y - b.y) * (a.y - b.y));
}

point intersectPoint(point a, point b, int y)
{
    point aPoint;
    double t = (y - a.y) / (b.y - a.y);
    aPoint.x = a.x + t * (b.x - a.x);
    aPoint.y = y;
    return aPoint;
}

void calculatePerimeters(point polycake[], int v, int y, double *perimeters1, double *perimeters2)
{
    int i, next, index = 0;
    point points[2];
    *perimeters1 = 0.0;
    *perimeters2 = 0.0;
    for(i = 0; i < v; i++)
    {
        next = (i + 1) % v;
        if(polycake[i].y < y && polycake[next].y < y)
            (*perimeters1) += distance(polycake[i], polycake[next]);
        else if(polycake[i].y > y && polycake[next].y > y)
            (*perimeters2) += distance(polycake[i], polycake[next]);
        else
        {
            points[index] = intersectPoint(polycake[i], polycake[next], y);
            if(polycake[i].y < y)
            {
                (*perimeters1) += distance(polycake[i], points[index]);
                (*perimeters2) += distance(polycake[next], points[index]);
            }
            else
            {
                (*perimeters2) += distance(polycake[i], points[index]);
                (*perimeters1) += distance(polycake[next], points[index]);
            }
            index++;
        }
    }

    (*perimeters1) += distance(points[0], points[1]);
    (*perimeters2) += distance(points[0], points[1]);
}

#include <stdio.h>

int a;
int a_0 = 1;
int b[10];

int scope1()
{
    a = 1;
    int a = 2;
    for (a = 3; a < 10; a++)
    {
        printf("%d\n", a); // should print 3-9
        int a = 4;
        if (1)
        {
            printf("%d\n", a); // should print 4
            int a = 5;
        }
    }
}

int main()
{
    scope1();
    a++;
    printf("%d\n", a); // should print 2
    double a = -1.02;
    a = 11.11;
    printf("%lf\n", a); // should print 11.11
}
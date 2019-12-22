#include "another.c"
#include <stdio.h>

#define A B
#define w while(1)

int main()
{
    int A = test();
    w{ break; }
    printf("%d", B);
    return 0;
}

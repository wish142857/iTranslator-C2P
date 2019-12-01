#include <stdio.h>
#include <string.h>
#include <stdlib.h>

int main(int argc, char **argv)
{
    char s[100];
    scanf("%s", s);
    int len = strlen(s);
    int mid = len / 2;
    for (int i = 0; i < len / 2; i++)
    {
        if (s[i] != s[len - 1 - i])
        {
            printf("False");
            system("pause");
            return 0;
        }
    }
    printf("True");
    system("pause");
    return 0;
}
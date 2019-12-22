#include <stdio.h>
#include <string.h>
#include <stdlib.h>

int main()
{
    printf("Please input a string:");
    char s[100];
    gets(s);
    int len = strlen(s);
    int mid = len / 2;
    for (int i = 0; i < len / 2; i++)
    {
        if (s[i] != s[len - 1 - i])
        {
            printf("Not a palindrome!");
            return 0;
        }
    }
    printf("A palindrome!");
    return 0;
}
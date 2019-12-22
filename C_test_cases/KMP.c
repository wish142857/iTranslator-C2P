#include <stdio.h>
#include <string.h>

char text[256];
char pattern[256];
int next[1024];

void getNext()
{
    int pLen = strlen(pattern);
    next[0] = -1;
    int i = 0;
    int j = -1;
    while (i < pLen - 1)
    {
        if (j == -1 || pattern[i] == pattern[j])
        {
            i++;
            j++;
            if (pattern[i] == pattern[j])
            {
                next[i] = next[j];
            }
            else
            {
                next[i] = j;
            }
        }
        else
        {
            j = next[j];
        }
    }
}

int kmp(int start)
{
    int pLen = strlen(pattern);
    int tLen = strlen(text);
    int i = start;
    int j = 0;
    while (i < tLen && j < pLen)
    {
        if (j == -1 || text[i] == pattern[j])
        {
            ++i;
            ++j;
        }
        else
        {
            j = next[j];
        }
    }
    if (j == pLen)
    {
        return i - j;
    }
    else
    {
        return -1;
    }
}

int main()
{
    printf("Please enter the text:\n");
    gets(text);
    printf("\nPlease enter the pattern:\n");
    gets(pattern);
    getNext();
    int start = 0;
    int flag = 0;
    int pos;
    int tLen = strlen(text);
    while (start < tLen)
    {
        pos = kmp(start);
        if (pos != -1)
        {
            printf("A match occurs at %d\n", pos + 1);
            start = pos + 1;
            flag = 1;
        }
        else
        {
            break;
        }
    }
    if (!flag)
    {
        printf("No match.");
    }
    printf("\n");
    return 0;
}
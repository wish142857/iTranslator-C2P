#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#define PTN_LEN 100
#define TXT_LEN 1000


void KMP_matcher(char *P, char *T, int m, int n)
{
    int pi[PTN_LEN];
    pi[1] = 0;
    int k = 0;
    for (int q = 2; q <= m; q++)
    {
        while (k > 0 && P[k + 1] != P[q])
            k = pi[k];
        if (P[k + 1] == P[q])
            k++;
        pi[q] = k;
    }
    int q = 0;
    for (int i = 1; i <= n; i++)
    {
        while (q > 0 && P[q + 1] != T[i])
            q = pi[q];
        if (P[q + 1] == T[i])
            q++;
        if (q == m)
        {
            printf("Pattern occurs with shift %d\n", i - m);
            q = pi[q];
        }
    }
}

int main(int argc, char **argv)
{
    char P[PTN_LEN];
    char T[TXT_LEN];
    int i = 1;
    char c;
    T[0] = 1;
    P[0] = 1;
    while ((c = getchar()) != '\n')
    {
        P[i] = c;
        i++;
    }
    P[i] = '\0';
    i = 1;
    while ((c = getchar()) != '\n')
    {
        T[i] = c;
        i++;
    }
    T[i] = '\0';
    int m = strlen(P) - 1;
    int n = strlen(T) - 1;
    // printf("%d %d", m, n);
    KMP_matcher(P, T, m, n);
    system("pause");
    return 0;
}
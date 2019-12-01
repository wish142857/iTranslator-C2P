int main()

{

    char s[1024];

    printf("Text:\n");

    gets(s);

    int len = strlen(s);

    if (len == 0) {

        printf("\nEmpty!\n");

        return 0;

    }

    int flag = 1;

    for (int i = 0; i < len / 2; ++i)

    {

        if (s[i] != s[len - 1 - i])

        {

            flag = 0;

            break;

        }

    }

    if (flag) {

        printf("\nResult:\nTrue\n");

    }

    else {

        printf("\nResult:\nFalse\n");

    }

    return 0;

}
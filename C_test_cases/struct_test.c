// 这个测例充分说明我们的C2Py编译器基本支持C中结构体的特性
#include <stdio.h>

// 结构体定义+变量声明
struct test2
{
    char a[10];
} a, b;

// 结构体定义中嵌套结构体
struct test1{
    int x;
    struct test2 y;
};

// 结构体数组声明
struct test1 c[100]; 

int main()
{
    // 结构体变量声明
    struct test2 q;

    // 结构体成员变量赋值等
    q.a[0] = 'c';
    c[99].y.a[0] = 'd';  
    printf("%s", c[99].y.a);
    return 0;
}

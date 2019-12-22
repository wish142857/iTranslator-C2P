#include <stdio.h>
#include <ctype.h>
#include <stdlib.h>
#include <string.h>
#include <stdlib.h>

struct Unit
{
	//定义操作单元 
	int    flag;// 1:操作数 0:操作符 -1:符号 
	char   op;//操作符 
	double num;//操作数
};

int check_flag = 0;

bool isnumber(char x)
{
	if (x == '0' || x == '1' || x == '2' || x == '3' || x == '4' || x == '5' || x == '6' || x == '7' || x == '8' || x == '9')
		return true;
	else
		return false;
}

int Isop(char ch)
{
	//判断合法字符  + - * / ( ) =
	if (ch == '+' || ch == '-' || ch == '*' || ch == '/' || ch == '(' || ch == ')' || ch == '=')
		return 1;
	return 0;
}

int Check(char Input_array[])
{
	//检查是否有非法字符，返回1表示不合法，0表示合法 
	int len = strlen(Input_array);
	int i;
	for (i = 0; i < len; i++)
	{
		if (!Isop(Input_array[i]) && Input_array[i] != '.' && !isnumber(Input_array[i]))
			return 1;
		if (isnumber(Input_array[i]))
		{
			int num_len = 0;
			int Cur_positoin = i + 1;
			while (isnumber(Input_array[Cur_positoin]) || Input_array[Cur_positoin] == '.')
			{
				num_len++;
				Cur_positoin++;
			}
			if (num_len >= 16)
				return 1;
		}
	}
	return 0;
}

int  Convert(struct Unit Unit_arry[], char Input_array[])
{
	//将字符串操作单元化 
	int len = strlen(Input_array);
	int i;
	int Unit_len = 0;
	for (i = 0; i < len; i++)
	{
		if (Isop(Input_array[i]))
		{
			Unit_arry[Unit_len].flag = 0;
			Unit_arry[Unit_len].op = Input_array[i];
			Unit_len++;
		}
		else
		{
			Unit_arry[Unit_len].flag = 1;
			char temp[100];
			int k = 0;
			for (; isnumber(Input_array[i]) || Input_array[i] == '.'; i++)
			{
				temp[k] = Input_array[i];
				k++;
			}
			i--;
			//temp[k] = '\0';
			Unit_arry[Unit_len].num = atof(temp);

			//负数 
			if (Unit_len == 1 && Unit_arry[Unit_len - 1].flag == 0
				&& Unit_arry[Unit_len - 1].op == '-')
			{
				Unit_arry[Unit_len - 1].flag = -1;
				Unit_arry[Unit_len].num *= -1;
			}// -x
			if (Unit_len >= 2 && Unit_arry[Unit_len - 1].flag == 0
				&& Unit_arry[Unit_len - 1].op == '-' && Unit_arry[Unit_len - 2].flag == 0
				&& Unit_arry[Unit_len - 2].op != ')')
			{
				Unit_arry[Unit_len - 1].flag = -1;
				Unit_arry[Unit_len].num *= -1;
			}// )-x

			//正数 
			if (Unit_len == 1 && Unit_arry[Unit_len - 1].flag == 0
				&& Unit_arry[Unit_len - 1].op == '+')
			{
				Unit_arry[Unit_len - 1].flag = -1;
			}// +x 
			if (Unit_len >= 2 && Unit_arry[Unit_len - 1].flag == 0
				&& Unit_arry[Unit_len - 1].op == '+' && Unit_arry[Unit_len - 2].flag == 0
				&& Unit_arry[Unit_len - 2].op != ')')
			{
				Unit_arry[Unit_len - 1].flag = -1;
			}// )+x
			Unit_len++;
		}
	}
	return Unit_len;
}

int  Compare(char op1, char op2)
{
	//操作符运算优先级比较
	char list[6] = "(+-*/";
	int map[25] = { 1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1,1,1,0,0,1,1,1,0,0 };
	int i;
	int j;
	for (i = 0; i < 5; i++)
		if (op1 == list[i]) break;
	for (j = 0; j < 5; j++)
		if (op2 == list[j]) break;
	return map[i * 5 + j];
}

double Compute(double x, double y, char op)
{
	//四则运算 
	if (op == '+')
		return x + y;
	if (op == '-')
		return x - y;
	if (op == '*')
		return x * y;
	if (op == '/')
		return x / y;
}

double Calculate(struct Unit Unit_arry[], int Unit_len)
{
	//利用栈计算 
	int i;
	int Num_pointer = 0;//指向操作数栈顶
	int Op_pointer = 0;//指向操作符栈顶
	double Num_stack[100] = { 0 };//操作数栈 
	char   Op_stack[100] = { 0 };//操作符栈 

	for (i = 0; i < Unit_len; i++)
	{
		if (Unit_arry[i].flag != -1)
		{
			if (Unit_arry[i].flag)//操作数 
			{
				Num_stack[Num_pointer] = Unit_arry[i].num;
				Num_pointer++;
			}
			else//操作符 
			{
				//操作符栈为空或者左括号 入栈
				if (Op_pointer == 0 || Unit_arry[i].op == '(')
				{
					Op_stack[Op_pointer] = Unit_arry[i].op;
					Op_pointer++;
				}
				else
				{
					if (Unit_arry[i].op == ')')// 右括号 将运算符一直出栈，直到遇见左括号 
					{
						Op_pointer--;
						Num_pointer--;
						while (Op_stack[Op_pointer] != '(' && Op_pointer != 0)
						{
							Num_stack[Num_pointer - 1] = Compute(Num_stack[Num_pointer - 1], Num_stack[Num_pointer],
								Op_stack[Op_pointer]);
							Op_pointer--;
							Num_pointer--;

						}
						Num_pointer++;
					}
					else
					{
						if (Compare(Unit_arry[i].op, Op_stack[Op_pointer - 1]))//和栈顶元素比较 
						{
							Op_stack[Op_pointer] = Unit_arry[i].op;
							Op_pointer++;
						}
						else//运算符出栈，再将该操作符入栈 
						{
							Op_pointer--;
							Num_pointer--;
							while (Compare(Unit_arry[i].op, Op_stack[Op_pointer]) == 0 && Op_pointer != -1)
							{
								//当前操作符比栈顶操作符优先级高 
								Num_stack[Num_pointer - 1] = Compute(Num_stack[Num_pointer - 1], Num_stack[Num_pointer],
									Op_stack[Op_pointer]);
								Op_pointer--;
								Num_pointer--;
							}
							Op_pointer++;
							Num_pointer++;
							Op_stack[Op_pointer] = Unit_arry[i].op;
							Op_pointer++;
						}
					}
				}
			}
		}
	}
	Op_pointer--;
	Num_pointer--;
	while (Op_pointer != -1)
	{
		Num_stack[Num_pointer - 1] = Compute(Num_stack[Num_pointer - 1], Num_stack[Num_pointer], Op_stack[Op_pointer]);//Op_pointer--为操作符出栈 
		Op_pointer--;
		Num_pointer--;//前一个操作数出栈 
	}

	if (Op_pointer == -1 && Num_pointer == 0)
		check_flag = 1;
	return Num_stack[0];
}

void Evaluate()
{
	//先调用Convert函数将字符串操作单元化，再调用Calculate函数计算结果并输出 
	char Input_array[100];
	struct Unit Unit_arry[100];

	printf("Please enter an expression:\n");
	gets(Input_array);
	check_flag = Check(Input_array);
	if (check_flag)
		printf("Illegal expression!\n");
	else
	{
		int Unit_len = Convert(Unit_arry, Input_array);
		double ans = Calculate(Unit_arry, Unit_len);
		if (check_flag)
		{
			printf("The result is ");
			printf("%lf\n", ans);
		}
		else
			printf("Incorrect expression!\n");
	}
}

int main()
{
	Evaluate();
	return 0;
}

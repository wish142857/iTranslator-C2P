/*
四则运算表达式求值
具体算法：
	先将字符串处理成操作单元（操作数或操作符），再利用栈根据四则运算
的运算法则进行计算，最后得出结果。
*/

#include<stdio.h>
#include<ctype.h>
#include<stdlib.h>
#include<string.h>
#include<stdlib.h>

const int max_length = 100;//表达式最大长度 
struct Unit
{
	//定义操作单元 
	int    flag;// 1:操作数 0:操作符 -1:符号 
	char   op;//操作符 
	double num;//操作数
};

int Check(char Input_array[]);
void Evaluate(); //先调用Convert操作单元化，再调用Calculate函数计算结果并输出 
int  Convert(struct Unit Unit_arry[], char Input_array[]);//将字符串处理成操作单元 
int  Isop(char ch);//判断合法字符（+ - * / ( ) =）
int  Compare(char op1, char op2);//操作符运算优先级比较 
double Calculate(struct Unit Unit_arry[], int Unit_len, int& flag);//用栈计算表达式结果 
double Compute(double x, double y, char op);//四则运算 

int main()
{
	Evaluate();
	return 0;
}

int Check(char Input_array[])
{
	//检查是否有非法字符，返回1表示不合法，0表示合法 
	int len = strlen(Input_array), i;
	for (i = 0; i < len; i++)
	{
		if (!Isop(Input_array[i]) && Input_array[i] != '.' && !isdigit(Input_array[i]))
			return 1;
		if (isdigit(Input_array[i]))
		{
			int num_len = 0, Cur_positoin = i + 1;
			while (isdigit(Input_array[Cur_positoin]) || Input_array[Cur_positoin] == '.')
			{
				num_len++;
				Cur_positoin++;
			}
			if (num_len >= 16)//15位有效数字 
				return 1;
		}
	}
	return 0;
}

void Evaluate()
{
	//先调用Convert函数将字符串操作单元化，再调用Calculate函数计算结果并输出 
	char Input_array[max_length];
	int flag = 0; 
	struct Unit Unit_arry[max_length];

	printf("请输入四则运算表达式：\n");
	gets_s(Input_array);
	flag = Check(Input_array);
	if (flag)
		printf("该表达式不合法！\n");
	else
	{
		int Unit_len = Convert(Unit_arry, Input_array);
		double        ans = Calculate(Unit_arry, Unit_len, flag);
		if (flag)
		{
			printf("计算结果为：\n");
			printf("%s%s%lf\n", Input_array,"=", ans);
		}
		else
			printf("该表达式不合法！\n");
	}
	system("pause");
}

int  Convert(struct Unit Unit_arry[], char Input_array[])
{
	//将字符串操作单元化 
	int len = strlen(Input_array);
	int i, Unit_len = 0;
	for (i = 0; i < len; i++)
	{
		if (Isop(Input_array[i]))//操作符 
		{
			Unit_arry[Unit_len].flag = 0;
			Unit_arry[Unit_len++].op = Input_array[i];
		}
		else//操作数 
		{
			Unit_arry[Unit_len].flag = 1;
			char temp[max_length];
			int k = 0;
			for (; isdigit(Input_array[i]) || Input_array[i] == '.'; i++)
			{
				temp[k++] = Input_array[i];
			}
			i--;
			temp[k] = '\0';
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

double Calculate(struct Unit Unit_arry[], int Unit_len, int& flag)
{
	//利用栈计算 
	int i, Num_pointer = 0, Op_pointer = 0;//Num_pointer指向操作数栈顶，Op_pointer指向操作符栈顶 
	double Num_stack[max_length] = { 0 };//操作数栈 
	char   Op_stack[max_length] = { 0 };//操作符栈 

	for (i = 0; i < Unit_len ; i++)
	{
		if (Unit_arry[i].flag != -1)
		{
			if (Unit_arry[i].flag)//操作数 
			{
				Num_stack[Num_pointer++] = Unit_arry[i].num;
			}
			else//操作符 
			{
				//操作符栈为空或者左括号 入栈
				if (Op_pointer == 0 || Unit_arry[i].op == '(')
				{
					Op_stack[Op_pointer++] = Unit_arry[i].op;
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
								Op_stack[Op_pointer--]);
							Num_pointer--;
							
						}
						Num_pointer++;
					}
					else if (Compare(Unit_arry[i].op, Op_stack[Op_pointer - 1]))//和栈顶元素比较 
					{
						Op_stack[Op_pointer++] = Unit_arry[i].op;
					}
					else//运算符出栈，再将该操作符入栈 
					{
						Op_pointer--;
						Num_pointer--;
						while (Compare(Unit_arry[i].op, Op_stack[Op_pointer]) == 0 && Op_pointer != -1)
						{
							//当前操作符比栈顶操作符优先级高 
							Num_stack[Num_pointer - 1] = Compute(Num_stack[Num_pointer - 1], Num_stack[Num_pointer],
								Op_stack[Op_pointer--]);
							Num_pointer--;
						}
						Op_pointer++;
						Num_pointer++;
						Op_stack[Op_pointer++] = Unit_arry[i].op;
					}
				}
			}
		}
	}
	
	Op_pointer--;//指向栈顶元素 
	Num_pointer--;//指向栈顶元素 
	while (Op_pointer != -1)
	{
		Num_stack[Num_pointer - 1] = Compute(Num_stack[Num_pointer - 1], Num_stack[Num_pointer], Op_stack[Op_pointer--]);//Op_pointer--为操作符出栈 
		Num_pointer--;//前一个操作数出栈 
	}
	
	if (Op_pointer == -1 && Num_pointer == 0)
		flag = 1;//表达式合法 
	return Num_stack[0];
}

int  Compare(char op1, char op2)
{
	//操作符运算优先级比较
	char list[] = { "(+-*/" };
	int map[5][5] = 
	{
		//行比列的运算级优先级低为0，高为1 
		//		  ( + - * /    
		/*  (  */ 1,0,0,0,0,
		/*  +  */ 1,0,0,0,0,
		/*  -  */ 1,0,0,0,0,
		/*  *  */ 1,1,1,0,0,
		/*  /  */ 1,1,1,0,0 
	};
	int i, j;
	for (i = 0; i < 5; i++)
		if (op1 == list[i]) break;
	for (j = 0; j < 5; j++)
		if (op2 == list[j]) break;
	return map[i][j];
}

double Compute(double x, double y, char op)
{
	//四则运算 
	switch (op)
	{
	case '+': return x + y;
	case '-': return x - y;
	case '*': return x * y;
	case '/': return x / y;//y不能为0 
	default: return 0;
	}
}

int  Isop(char ch)
{
	//判断合法字符  + - * / ( ) =
	if (ch == '+' || ch == '-' || ch == '*' || ch == '/' || ch == '(' || ch == ')' || ch == '=')
		return 1;
	return 0;
}


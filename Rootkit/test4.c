#include <stdio.h>
#include <syscall.h>
int main()
{
	syscall(__NR_chdir, "adrt");
	system("/bin/sh");
	
}
#include <unistd.h>     /* Symbolic Constants */
#include <sys/types.h>  /* Primitive System Data Types */ 
#include <errno.h>      /* Errors */
#include <stdio.h>      /* Input/Output */
#include <sys/wait.h>   /* Wait for Process Termination */
#include <stdlib.h>     /* General Utilities */
int main()
{
	pid_t childpid;
	
	childpid = fork();
	if (childpid >= 0) {
		if (childpid == 0) {
			printf("I am child \n");
			while(1);
		} else {
			printf("I am parent\n");
			while(1);
		}
	}
	return 0; 
}

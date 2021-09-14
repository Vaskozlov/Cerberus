#include <stdio.h>
#include <fcntl.h>
#include <stdlib.h>
#include <unistd.h>
#include <iostream>
#include <sys/types.h>

#define PATH2LOGS "/Users/vasilijkozlov/Documents/logs/"
#define AUTO_CERM_FOLDER "/Users/vasilijkozlov/Desktop/projects/AutoCerm"

int main(int argc, char *argv[])
{
    FILE* fd = fopen(PATH2LOGS"CerberousStart.log", "w");
    fprintf(fd, "Autostart pid: %d\n", getpid());
    fclose(fd);
    
    chdir(AUTO_CERM_FOLDER);
    system("unbuffer python3.9 Cerberus/bot.py &> "PATH2LOGS"Cerberous.log &");
    
    return EXIT_SUCCESS;
}

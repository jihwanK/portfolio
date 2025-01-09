

/*
   UCF 2017 (Fall) Local Programming Contest
   Problem: typing
*/

#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#define TRUE  1
#define FALSE 0

#define IDENTICAL 1
#define SIMILAR   2
#define DIFFERENT 3

/* ***
   Need to comment/uncomment the following #define
   to get (not get) additional output
#define USEFUL_INFO 1
*** */

char board[5][15]; /* the extra rows/columns are used to put a
         boarder around the keyboard so that all the letters 
         would have the same number of neighbors; this 
         avoids/simplies special cases */

char word1[25], word2[25];

/* ************************************************************ */

int main(void)
{
   int   data_set_count, k;
   void  init_board();
   int   compare_words();
   FILE  *in_fptr, *fopen();

   if ( (in_fptr = fopen("typing.in", "r")) == NULL )
     {
      printf("*** can't open input file *** \n");
      exit(0);
     }

   /* initialize the keyboard */
   init_board();

   /* process the input data sets */
   fscanf(in_fptr, "%d\n", &data_set_count);
   for ( k = 1;  k <= data_set_count;  ++k )
     {
      fscanf(in_fptr, "%s %s\n", &word1[0], &word2[0]);

#ifdef USEFUL_INFO
      printf("Case #%d: %s %s ", k, word1, word2);
#endif

      printf("%d\n", compare_words());

     }/* end for ( k ) */

   if ( fclose(in_fptr) == EOF )
     {
      printf("*** can't close input file *** \n");
      exit(0);
     }

   return(0);

}/* end main */

/* ************************************************************ */

void init_board()
{
   strcpy(board[0], "***********");
   strcpy(board[1], "*abcdefghi*");
   strcpy(board[2], "*jklmnopqr*");
   strcpy(board[3], "*stuvwxyz**");
   strcpy(board[4], "***********");

}/* end init_board */

/* ************************************************************ */

int compare_words()
{
   int index, r, c, row1, col1, ok_flag;

   if ( strcmp(word1,word2) == 0 )
      return(IDENTICAL);

   if ( strlen(word1) != strlen(word2) )
      return(DIFFERENT);

   /* the two words are not IDENTICAL but 
      they have the same length;
      compare the two words letter by leter */

   for ( index = 0;  index < strlen(word1);  ++index )
     {
      /* find the char word1[index] on keyboard */
      for ( r = 1;  r <= 3;  ++r )
         for ( c = 1;  c <= 9;  ++c )
            if ( word1[index] == board[r][c] )
              {
               row1 = r;
               col1 = c;
              }

      /* check to see if word2[index] matches word1[index] or
         if word2[index] is a neighbor of word1[index] */
      ok_flag = FALSE;
      for ( r = row1 - 1;  r <= row1 + 1;  ++r )
         for ( c = col1 - 1;  c <= col1 + 1;  ++c )
            if ( word2[index] == board[r][c] )
               ok_flag = TRUE;

      if ( !ok_flag )
         return(DIFFERENT);

     }/* end for ( index ) */

   return(SIMILAR);

}/* end compare_words */

/* ************************************************************ */


/*
   UCF 2016 (Fall) Local Programming Contest
   Problem: palind
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define TRUE  1
#define FALSE 0

#define MAX_PHONEME_COUNT 13
#define MAX_INP_STR_LEN 50

char phoneme[MAX_PHONEME_COUNT][2],
     inp_str[MAX_INP_STR_LEN + 1];
int  phoneme_count;

/* ************************************************** */

int main(void)
{
   FILE *in_fptr;
   int  data_set_count,
        inp_palind_count,
        k, j, m;
   int  check_palind();

   if ( (in_fptr = fopen("palind.in", "r")) == NULL )
   {
       printf("*** can't open input file *** \n");
       exit(-1);
   }

   fscanf(in_fptr, "%d\n", &data_set_count);

   for ( k = 1;  k <= data_set_count;  ++k )
   {
       fscanf(in_fptr, "%d\n", &phoneme_count);
       for ( j = 0; j < phoneme_count;  ++j )
       {
           fscanf(in_fptr, "%c %c\n", &phoneme[j][0], &phoneme[j][1]);
       }/* end for ( j ) */

       printf("Test case #%d:\n", k);

       fscanf(in_fptr, "%d\n", &inp_palind_count);
       for ( m = 1;  m <= inp_palind_count;  ++m )
       {
           fscanf(in_fptr, "%s\n", &inp_str[0]);
           if ( check_palind() )
              printf("%s YES\n", inp_str);
           else
              printf("%s NO\n", inp_str);
       }/* end for ( m ) */

       printf("\n");

   }/* end for ( k ) */

   if ( fclose(in_fptr) == EOF )
   {
       printf("*** can't close input file *** \n");
       exit(-1);
   }

   return(0);

}/* end main */

/* ************************************************** */

int check_palind()
{
   int  left_ind, right_ind;
   char c1, c2;
   int  check_phoneme(char, char);

   /* check the first letter in the input string against the last letter, then
      the second letter against second from the end, and so on until you get to
      the mid-point */
   left_ind = 0;
   right_ind = strlen(inp_str) - 1;

   while ( left_ind < right_ind )
   {
      c1 = inp_str[left_ind];
      c2 = inp_str[right_ind];
      if ( ( c1 == c2 ) || ( check_phoneme(c1, c2) ) )
      {/* so far, so good; move on to the next two letters */
          ++left_ind;
          --right_ind;
      }
      else
          /* ran into two letters that don't match */
          return(FALSE);

   }/* end while */

   return(TRUE);

}/* end check_palind */

/* ************************************************** */

int check_phoneme(char c1, char c2)
{
   int n;

   /* check to see if "c1 c2" are in the list of phonemes */
   for ( n = 0;  n < phoneme_count;  ++n )
   {
      if ( ( c1 == phoneme[n][0] && c2 == phoneme[n][1] ) ||
           ( c1 == phoneme[n][1] && c2 == phoneme[n][0] ) )
         return(TRUE);
   }

   return(FALSE);

}/* end check_phone_me */

/* ************************************************** */

#include <stdlib.h>
#include <stdio.h>


int main()
{
   int         testCases;
   int         curCase;
   int         numGearType;
   int         curGearType;
   int         curTry;
   int         numTries;
   int         curGear;
   int         numGears;
   int         counter;
   int *       gearDuplicities;
   double      answer;
   double *    gearTypeProb;
   double *    gearProb;
   double **   probTable;

   // Read in the number of cases
   scanf("%d", &testCases);

   // Loop through each case and find the probility of success
   for (curCase = 0; curCase < testCases; curCase++)
   {
      // Read in the number of types of gears
      scanf("%d", &numGearType);

      // Allocate room for the gears
      gearDuplicities = (int *) malloc(sizeof(int) * numGearType);
      gearTypeProb = (double *) malloc(sizeof(double) * numGearType);

      // Initialize the number of gears as zero
      numGears = 0;

      // Read in the descriptions of the gears
      for (curGearType = 0; curGearType < numGearType; curGearType++)
      {
         // Read in the count then the probability
         scanf("%d", &gearDuplicities[curGearType]);
         scanf("%lf", &gearTypeProb[curGearType]);

         // Update the total number of gears
         numGears += gearDuplicities[curGearType];
      }

      // Make a list of probabilities for each gear
      gearProb = (double *) malloc(sizeof(double) * numGears);

      // Fill the list of probabilities for each gear
      curGear = 0;
      for (curGearType = 0; curGearType < numGearType; curGearType++)
      {
         for (counter = 0; counter < gearDuplicities[curGearType]; counter++)
         {
            gearProb[curGear] = gearTypeProb[curGearType];
            curGear++;
         }
      }

      // Read in the total number of tries
      scanf("%d", &numTries);

      // Allocate room in the probability table whose [i-th, j-th] element will
      // contain the probability of acquiring up to the i-th gear by the j-th
      // day. Note that the indexing starts at 1 for both gears and days
      probTable = (double **) malloc(sizeof(double *) * (numGears + 1));
      for (curGear = 0; curGear <= numGears; curGear++)
      {
         probTable[curGear] = 
            (double *) malloc(sizeof(double) * (numTries + 1));
         
         // Fill the row with zeros
         for (curTry = 0; curTry <= numTries; curTry++)
         {
            probTable[curGear][curTry] = 0.0;
         }
      }

      // Set the default probability
      probTable[0][0] = 1.0;

      // Populate the probability table
      for (curGear = 0; curGear < numGears; curGear++)
      {
         for (curTry = 0; curTry < numTries; curTry++)
         {
            // Propogate the Probability based on success or failure
            // Success: use the orignal probability
            probTable[curGear + 1][curTry + 1] +=
               probTable[curGear][curTry] * gearProb[curGear];
      
            // Failure: use the compliment probability
            probTable[curGear][curTry + 1] +=
               probTable[curGear][curTry] * (1 - gearProb[curGear]);
         }
      }

      // Sum up the total probability
      // Note: that the last row was not propogated across, which is why this
      // step is necessary
      answer = 0;
      for (int curTry = 0; curTry <= numTries; curTry++)
      {
         answer += probTable[numGears][curTry];
      }

      // Print the answer
      printf("%.03lf\n", answer);

      // Free the table memory
      for (curGear = 0; curGear <= numGears; curGear++)
      {
         free(probTable[curGear]);
         probTable[curGear] = 0;
      }
      free(probTable);
      probTable = 0;

      // Free the memory for the gear types
      free(gearDuplicities);
      gearDuplicities = 0;
      free(gearTypeProb);
      gearTypeProb = 0;
      
      // Free the probability for each individual gear
      free(gearProb);
      gearProb = 0;
   }
}


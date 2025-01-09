#
# editor.py
# Solution for "Editor Navigation"
# 2017 UCF Local Programming Contest
# C Gouge
#

# define a very large number to initialize distance values
oo = int(1e9)

# get only valid neighbor positions based on arrow keys;
# at most 4 and possibly less than 4 depending on the row.
def valid_neighbors(f, s, ra, ca):
   n = []

   # left neighbor:
   # back one char on same line, except before first char (and
   # not on first line) neighbor is end of previous line
   if ca > 0:
      n.append( (ra, ca - 1) )
   else:
      if ra > 1:
         n.append( (ra - 1, s[ra - 1]) );

   # right neighbor:
   # forward one char on same line, except after last char (and
   # not on last line) neighbor is beginning of next line
   if ca < s[ra]:
      n.append( (ra, ca + 1) )
   else:
      if ra < f:
         n.append( (ra + 1, 0) )

   # up neighbor:
   # on the first line, no neighbor; otherwise previous line,
   # either the same position or the line length
   if ra > 1:
      if ca > s[ra - 1]:
         n.append( (ra - 1, s[ra - 1]) )
      else:
         n.append( (ra - 1, ca) )

   # down neighbor:
   # on the last line, no neighbor; otherwise next line,
   # either the same position or the line length
   if ra < f:
      if ca > s[ra + 1]:
         n.append( (ra + 1, s[ra + 1]) )
      else:
         n.append( (ra + 1, ca) )

   return n


# get the number of scenarios in the input
nscenarios = int(input())

for t in range(nscenarios):
   # read all the input for a scenario
   f = int(input())
   # we want s index to be the line number which is 1-based,
   # so insert a dummy element at beginning of the list
   s = [0]
   s.extend(list(map(int, input().split())))
   rc, cc = map(int, (input().split()))
   rm, cm = map(int, (input().split()))
   # horizontal positions can be 0 through s[i] inclusive, so
   # we'll need to allocate 1 more than max s[i] value
   smax = 1 + max(s)

   # bfs setup
   visited = [[False for c in range(smax + 1)] for r in range(f + 1)]
   distance = [[oo for c in range(smax + 1)] for r in range(f + 1)]

   # queue for bfs (breadth-first search algorithm)
   q = []

   # start bfs
   visited[rc][cc] = True
   q.append( (rc, cc) )
   distance[rc][cc] = 0

   while q:
      (ra, ca) = q.pop(0)
      if (ra, ca) == (rm, cm):
         break
      for (rn, cn) in valid_neighbors(f, s, ra, ca):
         if not visited[rn][cn]:
            visited[rn][cn] = True
            q.append((rn, cn))
            distance[rn][cn] = 1 + distance[ra][ca]

   # output distance (number of keypresses)
   print(distance[rm][cm])


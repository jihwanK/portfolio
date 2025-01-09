
EPS = 1e-9



class Point:
   x = 0
   y = 0

   def __init__(self, x, y):
      self.x = x;
      self.y = y;


   def dot(self, p):
      return self.x * p.x + self.y * p.y


   def sub(self, p):
      return Point(self.x - p.x, self.y - p.y)


   def length(self):
      return sqrt(dot(self))


   def equals(self, p):
      return sub(p).length() < EPS



class Polycake:
   v = 0
   y = 0
   points = []


   def __init__(self):
      numCases = int(input())
      for t in range(0, numCases):
         self.v, self.y = map(int, input().split())

         del self.points[:]
         for _ in range(0, self.v):
            i, j = map(int, input().split())
            self.points.append(Point(i, j))

         self.runCase()


   def runCase(self):
      lower = []
      upper = []

      for i in range(0, self.v):
         a = self.points[i]
         b = self.points[(i + 1) % self.v]

         if a.y < self.y and b.y < self.y:
            lower.append(a)
         elif a.y > self.y and b.y > self.y:
            upper.append(a)
         elif a.y < self.y:
            lower.append(a)
            t = (self.y - a.y) / (b.y - a.y)
            newX = a.x + t * (b.x - a.x)
            lower.append(Point(newX, self.y))
            upper.append(Point(newX, self.y))
         else:
            upper.append(a)
            t = (self.y - a.y) / (b.y - a.y)
            newX = a.x + t * (b.x - a.x)
            upper.append(Point(newX, self.y))
            lower.append(Point(newX, self.y))

      totalLower = 0.0
      for i in range(0, len(lower)):
         a = lower[i]
         b = lower[(i + 1) % len(lower)]
         totalLower = totalLower + ((b.x - a.x) ** 2 + (b.y - a.y) ** 2) ** 0.5

      totalUpper = 0.0
      for i in range(0, len(upper)):
         a = upper[i]
         b = upper[(i + 1) % len(upper)]
         totalUpper = totalUpper + ((b.x - a.x) ** 2 + (b.y - a.y) ** 2) ** 0.5

      if (totalLower < totalUpper):
         print("%.3f %.3f" % (totalLower, totalUpper))
      else:
         print("%.3f %.3f" % (totalUpper, totalLower))



Polycake()


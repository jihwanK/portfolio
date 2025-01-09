#include <iostream>
#include <map>
#include <algorithm>
#include <queue>
#include <string>

using namespace std;

const int INFINITY = 1000000000;
const int MAX_NODES = 4 * 400;
int adj[MAX_NODES][MAX_NODES];
int dist[MAX_NODES];
map<string, int> cityNames;

class Compare
{
public:
    bool operator() (pair<int, int> a, pair<int, int> b)
    {
        return a.second > b.second;
    }
};

int main()
{
    map<string, int> transportTypes({{"AIR", 0}, {"SEA", 1}, {"RAIL", 2}, {"TRUCK", 3}});

    int n;
    cin >> n;
    for(int i = 0; i < n; i++)
    {
        int c;
        cin >> c;

        // We construct a graph with 4 nodes for each city, one for each mode of transport.
        cityNames.clear();
        fill(&adj[0][0], &adj[0][0] + MAX_NODES * MAX_NODES, INFINITY);
        for(int j = 0; j < c; j++)
        {
            string name;
            int cost;
            cin >> name >> cost;

            cityNames.insert({name, j});

            // Add an edge for each pair of nodes for the city, representing to cost of changing
            // transport mode.
            for(int a = 0; a < 4; a++)
            {
                for(int b = 0; b < 4; b++)
                {
                    adj[4 * j + a][4 * j + b] = cost;
                }
            }
        }

        int r;
        cin >> r;
        for(int j = 0; j < r; j++)
        {
            string start, end, type;
            int cost;
            cin >> start >> end >> type >> cost;

            // Add a bidirectional edge for the two cities on this route, but only between the
            // nodes corresponding to the correct transportation mode.
            int s = cityNames[start];
            int e = cityNames[end];
            int t = transportTypes[type];
            adj[4 * s + t][4 * e + t] = cost;
            adj[4 * e + t][4 * s + t] = cost;
        }

        string start, end;
        cin >> start >> end;
        int s = cityNames[start];
        int e = cityNames[end];

        // We can start at any of the 4 nodes of the starting city.
        fill(dist, dist + MAX_NODES, INFINITY);
        priority_queue<pair<int, int>, vector<pair<int, int>>, Compare> pq;
        for(int j = 0; j < 4; j++)
        {
            dist[4 * s + j] = 0;
            pq.push(pair<int, int>(4 * s + j, 0));
        }

        // Run Dijkstra's shortest path
        while(!pq.empty())
        {
            pair<int, int> node = pq.top();
            pq.pop();
            if(dist[node.first] == node.second)
            {
                for(int j = 0; j < 4 * c; j++)
                {
                    int newDist = node.second + adj[node.first][j];
                    if(newDist < dist[j])
                    {
                        dist[j] = newDist;
                        pq.push(pair<int, int>(j, newDist));
                    }
                }
            }
        }

        // We can end at any of the 4 nodes of the ending city.
        int result = dist[4 * e];
        for(int j = 1; j < 4; j++)
        {
            result = min(result, dist[4 * e + j]);
        }

        cout << result << endl;
    }
}

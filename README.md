# bestRouteFinder

Welcome to the best route finder github. This project is for the sole purpose of building an election tool to determine which route to take for el holidays. A bunch of people vote for a bunch of routes. Let's find the most wanted / least unwanted route.

We use instant runoff voting, which is a hierarchy based election method. Each voter ranks the routes/choices/candidates from 1 to n. The rank 1 candidate can be seen as their current vote. First we check if a route has a majority of votes from the get go. If so, we have found a winner. If not, we eliminate the route with the least rank 1 votes from the election. Then, if that route had any votes, we redistribute those votes by instead voting on the rank 2 option of the corresponding voters. We repeat this process of eliminating the bottom candidate and redistributing the votes until there is a route with the majority of votes.

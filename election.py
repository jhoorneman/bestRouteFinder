from typing import Optional, Dict, Set

import copy

import csv


def election_result_from_file(filename: str):
    with open(filename, newline='') as csvFile:
        data_list = list(csv.DictReader(csvFile))

    # simplify the route names
    old_headers = list(data_list[0].keys())
    new_headers = old_headers.copy()
    for i, header in enumerate(new_headers):
        new_headers[i] = header.replace('Which route would you prefer? Pick an order in which you prefer routes. '
                                        'MAKE SURE THAT YOU RANK ALL ROUTES AT DIFFERENT PRIORITIES. ', '')

    routes = new_headers[2:]
    # update all headers for the enquete answers heeeeeeeee
    for row in data_list:
        for i in range(len(new_headers)):
            data_list[new_headers[i]] = data_list.pop(old_headers[i])
    voters = None  # TODO: somehow fetch voters from csv
    return ElectionResult(routes, voters)


class ElectionResult:
    # does instant runoff election

    def __init__(self, routes: list, voters: list):
        self.routes = routes
        self.voters = voters

    def get_winner(self) -> Optional[str]:
        ranking = self.rank_routes()
        highest_score = max(ranking.values())
        if highest_score <= len(self.voters) / 2:
            # no majority is present
            return None
        top_scorers = [route for route, score in ranking.items() if score == highest_score]
        if len(top_scorers) != 1:
            raise ValueError('Something strange is going on with {}'.format(self.routes))
        return top_scorers[0]

    def rank_routes(self) -> dict:
        # counts the votes for each route
        prel_result = {route: 0 for route in self.routes}
        for voter in self.voters:
            prel_result[voter.ranking[0]] += 1

        return prel_result

    def find_last_place(self) -> str:
        # finds out which route is the least voted on (and handles last place ties)
        prel_result = self.rank_routes()
        least_votes = len(self.voters) + 1
        last_places = []
        for route in prel_result:
            if prel_result[route] < least_votes:
                last_places = [route]
                least_votes = prel_result[route]
            elif prel_result[route] == least_votes:
                last_places += [route]

        if len(last_places) > 1:
            # Try to break ties by comparing copeland scores https://electowiki.org/wiki/Copeland%27s_method
            scores = self.get_copeland_score()
            last_place_scores = {route: scores[route] for route in last_places}
            min_score = min(last_place_scores.values())
            last_places = [route for route, score in last_place_scores.items() if score == min_score]

        if len(last_places) > 1:
            # Failed to break ties; announce and complain
            print('WRONGLY returning alphabetically last {} from tied last place between {}'.format(
                sorted(last_places)[-1],
                last_places
            ))
            last_place = sorted(last_places)[-1]
        else:
            last_place = last_places[0]

        return last_place

    def without_route(self, route: str) -> 'ElectionResult':
        # returns an ElectionResult with given route removed, and voter rankings adjusted accordingly
        new_routes = self.routes.copy()
        new_routes.remove(route)
        new_voters = copy.deepcopy(self.voters)
        for voter in new_voters:
            if route in voter.ranking:
                voter.ranking.remove(route)

        return ElectionResult(new_routes, new_voters)

    def get_interim_score(self) -> str:
        # TODO: improve this
        return str(self.rank_routes())

    def get_pairwise_votes(self) -> Dict[str, Dict[str, int]]:
        # returns a dict r, for which r[route1][route2] = number of voters voting for route 1 in a match against route2
        return {route1: {
            route2: len([voter for voter in self.voters if voter.prefers_over(route1, route2)])
            for route2 in self.routes
        } for route1 in self.routes}

    def get_copeland_score(self) -> Dict[str, int]:
        votes = self.get_pairwise_votes()
        return {
            r1: len([r2 for r2 in self.routes if votes[r1][r2] > votes[r2][r1]]) -
                len([r2 for r2 in self.routes if votes[r1][r2] < votes[r2][r1]]) for r1 in self.routes
        }


def find_irv_winner(election: ElectionResult) -> str:
    # finds winning route by using instant run-off voting
    print('Finding winning route.. starting score:\n{}'.format(election.get_interim_score()))
    while election.get_winner() is None:
        print('No majority was found! ')
        last_place = election.find_last_place()
        print("Eliminating route '{}'".format(last_place))
        election = election.without_route(last_place)  # returns new ElectionResult, does not modify in place
        print('New interim score:\n{}'.format(election.get_interim_score()))
        # TODO: add os.sleep(10) here..?

    print('FOUND WINNING ROUTE!')
    winner = election.get_winner()
    print(winner + ' got the most votes!')

    return winner


def get_smith_set(election: ElectionResult) -> Set[str]:
    votes = election.get_pairwise_votes()
    smith_relation = {
        r1: {r2: r1 != r2 and votes[r1][r2] >= votes[r2][r1] for r2 in election.routes}
        for r1 in election.routes
    }
    smith_closure = get_transitive_closure(smith_relation)
    # now smith_closure[route1][route2] is true if there is a sequence of routes r, such that
    # for each two subsequent elements r1, r2 of [route1] ++ r ++ [route2], r1 beats or ties with r2

    # now extract the maximal elements from this
    return {
        r1 for r1 in election.routes if (
            all([(r1 == r2 or smith_closure[r1][r2] or not smith_closure[r2][r1]) for r2 in election.routes])
        )  # r1 is maximal if for all other r2, either r1 >= r2, or not (r2 >= r1)
    }


def get_transitive_closure(twod_dict: Dict[str, Dict[str, int]]) -> Dict[str, Dict[str, int]]:
    # implements boolean Floyd-Warshall algorithm
    keys = twod_dict.keys()
    tc = copy.deepcopy(twod_dict)
    for key1 in keys:
        for key2 in keys:
            for key3 in keys:
                tc[key1][key2] |= tc[key1][key3] and tc[key3][key2]
    return tc


def find_tideman_winner(election: ElectionResult) -> str:
    # finds winning route by using https://en.wikipedia.org/wiki/Tideman_alternative_method
    print('Finding winning route.. starting score:\n{}'.format(election.get_interim_score()))
    winner = None
    while winner is None:
        smith_set = get_smith_set(election)
        if len(smith_set) == 1:
            winner = next(iter(smith_set))
            print('Most voters prefer one route over the others...')
            continue
        # eliminate all routes outside smith set
        for route in election.routes:
            if route not in smith_set:
                print("Eliminating route '{}'".format(route))
                election = election.without_route(route)
        last_place = election.find_last_place()
        print("Eliminating route '{}'".format(last_place))
        election = election.without_route(last_place)  # returns new ElectionResult, does not modify in place
        print('New interim score:\n{}'.format(election.get_interim_score()))
        # TODO: add os.sleep(10) here..?

    print('FOUND WINNING ROUTE!')
    print(winner + ' got the most votes!')

    return winner

from typing import Optional

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
        least_votes = len(self.voters)+1
        last_places = []
        for route in prel_result:
            if prel_result[route] < least_votes:
                last_places = [route]
                least_votes = prel_result[route]
            elif prel_result[route] == least_votes:
                last_places += [route]

        if len(last_places) > 1:
            # TODO: THIS IS FLAWED
            print('WRONGLY returning alphabetically last {} from tied last place between {}'.format(
                last_places[-1],
                last_places
            ))
            last_place = last_places[-1]
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


def find_winner(election: ElectionResult) -> str:
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

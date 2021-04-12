from unittest import TestCase
from random import choices, sample
import string

from election import ElectionResult, find_winner
from voter import Voter


def get_random_voter_on(routes):
    random_name = ''.join(choices(string.ascii_uppercase + string.digits, k=7))
    return Voter(random_name, sample(routes, k=5))


class TestElectionResult(TestCase):
    def setUp(self) -> None:
        num_routes = 7
        routes = ['r{}'.format(i) for i in range(1, num_routes + 1)]
        self.test_election = ElectionResult(
            routes, [
                Voter('Ike', ['r1', 'r6', 'r2', 'r3', 'r5']),
                Voter('Jochem', ['r3', 'r4', 'r6', 'r1', 'r2']),
                Voter('Jesse', ['r2', 'r1', 'r5', 'r3', 'r4']),
                Voter('Piotr', ['r3', 'r5', 'r2', 'r4', 'r7']),
                Voter('Melina', ['r4', 'r1', 'r5', 'r6', 'r3']),
            ]
        )

    def test_get_winner(self):
        self.assertIsNone(self.test_election.get_winner())
        self.assertIsNone(self.test_election.without_route('r2').get_winner())
        self.assertEquals(self.test_election.without_route('r2').without_route('r4').get_winner(), 'r1')

    def test_rank_routes(self):
        self.assertDictEqual(self.test_election.rank_routes(), {
            'r1': 1, 'r2': 1, 'r3': 2, 'r4': 1, 'r5': 0, 'r6': 0, 'r7': 0
        })

    def test_find_last_place(self):
        # TODO: add support for tie in last place
        print(self.test_election.get_interim_score())
        self.assertIn(self.test_election.find_last_place(), ['r5', 'r6', 'r7'])

    def test_without_route(self):
        election_without = self.test_election.without_route('r2')
        self.assertDictEqual(election_without.rank_routes(), {
            'r1': 2, 'r3': 2, 'r4': 1, 'r5': 0, 'r6': 0, 'r7': 0
        })
        # check that test_election is unchanged
        self.test_rank_routes()
        # check that voter rankings are changed correctly : original votes, with r2 removed
        self.assertListEqual(election_without.voters[3].ranking, ['r3', 'r5', 'r4', 'r7'])

    def test_find_winner(self):
        self.assertEquals(find_winner(self.test_election), 'r1')

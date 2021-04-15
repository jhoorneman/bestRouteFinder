from election import *
import os
import time

input('Press any key to start')

results: ElectionResult = election_result_from_file('poll_data.csv')
# results.voters = results.voters[:3]
print_results_slowly(results)
time.sleep(5)
find_tideman_winner(results)

input('Press any key to close')
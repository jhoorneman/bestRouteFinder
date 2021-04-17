from election import *
import os
import time

input('Press any key to start')

results: ElectionResult = election_result_from_file('poll_data.csv')
print_results_slowly(results, 0)
time.sleep(2)
find_tideman_winner(results)

input('\nPress any key to close')
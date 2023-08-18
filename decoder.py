import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--value-policy')
parser.add_argument('--states')
args = parser.parse_args()

values = args.value_policy
states_file = args.states
with open(values, 'r') as f:
    optimal_values = f.readlines()

value_eval = [optimal_values[i].split() for i in range(len(optimal_values))]

with open(states_file, 'r') as f:
    states_raw = f.readlines()

states = [states_raw[i].strip() for i in range(len(states_raw))]

runs = {0:0, 1:1, 2:2, 3:4, 4:6}

for i in range(len(states)):
    print(states[i], runs[int(value_eval[i][1])], value_eval[i][0])
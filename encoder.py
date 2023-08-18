import argparse
from symbol import parameters
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("--states")
parser.add_argument("--parameters")
parser.add_argument("--q")
args = parser.parse_args()

states_file = args.states
parameters_file = args.parameters
q = float(args.q)

with open(states_file,'r') as f:
    content = f.readlines()

total_balls = int(content[0][0:2])
total_runs = int(content[0][2:])

def read_parameters(path):
    probabilities = {}
    with open(path, 'r') as f:
        contents = f.readlines()
        for line in contents[1:]:
            split_line = line.strip().split()
            action = int(split_line[0])
            probabilities[action] = {}
            probabilities[action][-1] = float(split_line[1])
            probabilities[action][0] = float(split_line[2])
            probabilities[action][1] = float(split_line[3])
            probabilities[action][2] = float(split_line[4])
            probabilities[action][3] = float(split_line[5])
            probabilities[action][4] = float(split_line[6])
            probabilities[action][6] = float(split_line[7])

    return probabilities

parameters = read_parameters(parameters_file)

def state_map(balls, runs, strike, result):
    state = 0
    if result == "Win":
        return 2*total_balls*total_runs
    elif result == "Lose":
        return 2*total_balls*total_runs+1
    else:
        if strike == 'A':
            state = (total_balls*total_runs) - (balls*total_runs) + (total_runs-runs)
            return state    

        if strike == 'B':
            state = (2*total_balls*total_runs) - (balls*total_runs) + (total_runs-runs)
            return state    


def action_map(ac):
    action = {0: 0, 1: 1, 2: 2, 4: 3, 6: 4}
    return action[ac]

transitions = {}
rewards = {}

actions = [0, 1, 2, 4, 6]
outcomes = [-1, 0, 1, 2, 3, 4, 6]

for b in range(1, total_balls+1):
    for r in range(1, total_runs+1):
        # Player A on strike
        state = (b, r, 'A')
        for ac in actions:
            for runs in outcomes:
                if runs == -1: # Game over
                    next_state = "Lose"

                    if (state, ac, next_state) not in transitions:
                        transitions[(state, ac, next_state)] = parameters[ac][runs]
                        rewards[(state, ac, next_state)] = 0
                    else:
                        transitions[(state, ac, next_state)] += parameters[ac][runs]   

                else:
                    if (r - runs <= 0): # Target chased
                        next_state = "Win"
                        if (state, ac, next_state) not in transitions:
                            transitions[(state, ac, next_state)] = parameters[ac][runs]
                            rewards[(state, ac, next_state)] = 1
                        else:
                            transitions[(state, ac, next_state)] += parameters[ac][runs]   
                      
                    else: # Target not chased
                        if (runs % 2 == 0): # A scores an even number of runs
                            if (b % 6 == 1): # End of over
                                next_state = (b - 1, r - runs, 'B')
                                if b - 1 == 0 and r - runs > 0:
                                     next_state = "Lose"

                            else: # Not the end of over
                                next_state = (b - 1, r - runs, 'A')
                                if b- 1 == 0 and r - runs > 0:
                                     next_state = "Lose"

                        else: # A scores an odd number of runs
                            if (b% 6 == 1): # End of over
                                next_state = (b - 1, r - runs, 'A')
                                if b - 1 == 0 and r - runs > 0:
                                     next_state = "Lose"
                            else: # Not the end of over
                                next_state = (b - 1, r - runs, 'B')
                                if b - 1 == 0 and r - runs > 0:
                                     next_state = "Lose"

                        if (state, ac, next_state) not in transitions:
                            transitions[(state, ac, next_state)] = parameters[ac][runs]
                            rewards[(state, ac, next_state)] = 0
                        else:
                            transitions[(state, ac, next_state)] += parameters[ac][runs]           

                    

        # Player B on strike
        state = (b, r, 'B')
        for runs in [-1,0,1]:
            if runs == -1: # Game over
                    next_state = "Lose"
                    if (state, 1, next_state) not in transitions:
                        transitions[(state, 1, next_state)] = q
                        rewards[(state, 1, next_state)] = 0
                    else:
                        transitions[(state, 1, next_state)] += q
                  
            else:
                if (r - runs <= 0): # Target chased
                    next_state = "Win"
                    
                    if (state, 1, next_state) not in transitions:
                        transitions[(state, 1, next_state)] = (1-q)/2
                        rewards[(state, 1, next_state)] = 1
                    else:
                        transitions[(state, 1, next_state)] += (1-q)/2  

                else: # Target not chased
                    if (runs % 2 == 0): # B scores an even number of runs
                        if (b% 6 == 1): # End of over
                            next_state = (b - 1, r - runs, 'A')
                            if b - 1 == 0 and r - runs > 0:
                                     next_state = "Lose"

                        else: # Not the end of over
                            next_state = (b - 1, r - runs, 'B')
                            if b - 1 == 0 and r - runs > 0:
                                     next_state = "Lose"

                    else: # B scores an odd number of runs
                        if (b% 6 == 1): # End of over
                            next_state = (b - 1, r - runs, 'B')
                            if b - 1 == 0 and r - runs > 0:
                                     next_state = "Lose"
                        else: # Not the end of over
                            next_state = (b - 1, r - runs, 'A')
                            if b - 1 == 0 and r - runs > 0:
                                     next_state = "Lose"

                    if (state, 1, next_state) not in transitions:
                        transitions[(state, 1, next_state)] = (1-q)/2
                        rewards[(state, 1, next_state)] = 0
                    else:
                        transitions[(state, 1, next_state)] += (1-q) /2         

                    
print("numStates", 2*(total_balls*total_runs + 1))
print("numActions", 5)
print("end", 2*total_balls*total_runs, 2*total_balls*total_runs+1)

for i in transitions.keys():
    current_state = state_map(i[0][0],i[0][1],i[0][2],i[0])
    next_state = state_map(i[2][0],i[2][1],i[2][2],i[2])
    action = action_map(i[1])
    print('transition'+ " " + str(current_state) + " " + str(action) + " " + str(next_state) + " " + str(rewards[i]) + " " +str(transitions[i]))

print("mdptype episodic")
print("discount 1.0")


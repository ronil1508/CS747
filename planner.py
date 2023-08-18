import numpy as np
import pulp
import math
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("--mdp")
parser.add_argument("--algorithm", default= 'hpi')
parser.add_argument("--policy",default= "")
args = parser.parse_args()

file = args.mdp
policy = args.algorithm
pol_file = args.policy

with open(file) as f:
    content = f.readlines()
file = [content[i][:-1].split() for i in range(len(content))]   

given_policy = []
if pol_file != "":
    with open(pol_file) as p:
        pol_content = p.readlines()
    pol_file = [pol_content[i][:-1].split() for i in range(len(pol_content))]   

    for i in range(len(pol_file)):
        given_policy.append(int(pol_file[i][0]))

mdp ={}
mdp['numStates'] = int(file[0][1])
mdp['numActions'] = int(file[1][1])

mdp['end'] = []
for i in range(1,len(file[2])):
    mdp['end'].append(int(file[2][i]))

mdp['transition'] = [[[] for i in range(mdp['numActions'])] for j in range(mdp['numStates'])]

for i in range(3,len(file)-2):
    m = int(file[i][1])
    n = int(file[i][2])
    mdp['transition'][m][n].append((int(file[i][3]), float(file[i][4]), float(file[i][5])))

mdp['discount'] = float(file[-1][1])

def valueEvaluation(policy, numStates, numActions, transition, gamma, end_states):
    v0 = np.zeros(numStates)
    v1 = np.zeros(numStates)
    max_error = 1e-12
    
    while(True):
        for i in range(numStates):
            if i in end_states:
                continue
            v1[i] = 0
            for k in transition[i][int(policy[i])]:
                v1[i] += k[2]*(k[1] + (gamma*v0[k[0]]))

        if np.max(np.abs(np.subtract(v0,v1))) < max_error:
            break

        v0 = np.copy(v1)

    return v1    


def valueIteration(numStates, numActions, transition, gamma, end_states):
    v0 = np.zeros(numStates)
    v1 = np.zeros(numStates)
    policy = np.zeros(numStates)
    max_error = 1e-12
    
    while(True):
        for i in range(numStates):
            v_optimal = 0
            if i in end_states:
                continue
            for j in range(numActions):
                v1[i] = 0 
                for k in transition[i][j]:
                    v1[i] += k[2]*(k[1] + (gamma*v0[k[0]]))
                if v1[i] > v_optimal:
                    v_optimal = v1[i]
                    policy[i] = j
            v1[i] = v_optimal  

        if np.max(np.abs(np.subtract(v0,v1))) < max_error:
            break

        v0 = np.copy(v1)

    return v1, policy  

def lp(numStates, numActions, transition, gamma, end_states):
    prob = pulp.LpProblem("value_function", pulp.LpMinimize)

    v = []
    for i in range(numStates):
        v.append(pulp.LpVariable('v'+str(i)))
    total_sum = 0
    for i in range(numStates):    
        total_sum += v[i]
    prob += total_sum

    for i in range(numStates):
        for j in range(numActions): 
            prob += ( v[i] >= pulp.lpSum([s[2]*(s[1] + gamma*v[s[0]]) for s in transition[i][j]]))
    prob.writeLP("Assignment2.lp")      
    prob.solve(pulp.PULP_CBC_CMD(msg=0))

    v0 = np.zeros(numStates)
    for i in range(numStates):
        v0[i] = pulp.value(v[i])

    policy = np.zeros(numStates)   

    for i in range(numStates):
        best_action = math.inf
        for j in range(numActions):
            action_value = 0
            for k in transition[i][j]:
                action_value += k[2]*(k[1] + gamma*v0[k[0]])
            if abs(action_value - v0[i]) <= best_action:
                policy[i] = j
                best_action = abs(action_value - v0[i])    

    return v0, policy

def HpolicyIteration(numStates, numActions, transition, gamma, end_states):
    
    v = np.zeros(numStates)
    policy = np.zeros(numStates)
    improvement_possible = True

    while(improvement_possible):
        v0 = valueEvaluation(policy, numStates, numActions, transition, gamma, end_states)
        improving_actions = 0
        for i in range(numStates):
            for j in range(numActions):
                action_value = 0
                for k in transition[i][j]:
                    action_value += k[2]*(k[1] + gamma*v0[k[0]])
                if action_value > v0[i] + 1e-6:
                    improving_actions += 1
                    policy[i] = j
     

        if improving_actions == 0:
            improvement_possible = False

    return v0, policy       

numStates  = mdp['numStates']
numActions = mdp['numActions']
transition = mdp['transition']
gamma      = mdp['discount']
end_states = mdp['end']


if args.policy != "":
    V0 = valueEvaluation(given_policy, numStates, numActions, transition, gamma, end_states)
    for i in range(len(V0)):
        print('{:.6f}'.format(round(V0[i], 6)) + "\t" + str(int(given_policy[i])))
    
else:
    if (policy == 'vi'):
        V0, pi = valueIteration(numStates, numActions, transition, gamma, end_states)
    elif (policy == 'lp'):
        V0, pi = lp(numStates, numActions, transition, gamma, end_states)  
    elif (policy == 'hpi'):
        V0, pi = HpolicyIteration(numStates, numActions, transition, gamma, end_states) 

    for i in range(len(V0)):
        print('{:.6f}'.format(round(V0[i], 6)) + "\t" + str(int(pi[i])))





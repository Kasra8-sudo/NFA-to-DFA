import re
import pandas as pd
import string
from visual_automata.fa.dfa import VisualDFA

lst = []
with open('./input.txt', 'r') as file:
    for line in file:
        lst.append(line.strip())

filtered_list = [item for item in lst if item != '' and not item.startswith('#')]

initial_state = 0
user_input_string = ''
final_state = None
for item in filtered_list:
    if item.startswith('initial_state'):
        initial_state = item.split('=')[1]
    if item.startswith('user_input_string'):
        user_input_string = item.split('=')[1]
    if item.startswith('final_state='):
        final_state = set([(char) for char in item.split('=')[1] if char.isdigit()])

result_tuples = []
alpha = set()
states = set()

for item in filtered_list:
    if item.startswith('final_state=') or item.startswith('initial_state=') or item.startswith('user_input_string='):
        continue
    else:
        splited_item = item.replace(" ", "").split("=")
        tuple_elements = tuple(splited_item[0][1:-1].split(","))

        next_state_t = (splited_item[1])
        result_tuple = tuple_elements + (next_state_t,)
        result_tuples.append(result_tuple)

s = sorted(list(states))
separated_data = {}
a = set()
for item in result_tuples:
    a.add(item[0])
    a.add(item[2])

states = sorted(sorted(a))
paths = sorted(set(item[1] for item in result_tuples))
transition_table = {state: {path: [] for path in paths} for state in states}

for state, path, next_state in result_tuples:
    transition_table[state][path].append(next_state)


def epsilon_closure(state, nfa):
    closure = set()
    stack = [state]
    while stack:
        current_state = stack.pop()
        closure.add(current_state)
        for next_state in nfa[current_state]['lambda']:
            if next_state not in closure:
                stack.append(next_state)
    return closure


def move(states, symbol, nfa):
    result = set()
    for state in states:
        result.update(nfa.get(state, {}).get(symbol, []))
    return result


def nfa_to_dfa(nfa):
    dfa = {}
    queue = []
    alphabet = set(symbol for state in nfa.values() for symbol in state.keys() if symbol != 'lambda')
    q0 = epsilon_closure('0', nfa)
    queue.append(q0)
    dfa[tuple(sorted(q0))] = {}

    while queue:
        current_states = queue.pop(0)
        for symbol in alphabet:
            next_states = set()
            for state in current_states:
                next_states.update(move(state, symbol, nfa))
            for state in next_states.copy():
                next_states.update(epsilon_closure(state, nfa))
            next_states = tuple(sorted(next_states))
            if next_states not in dfa:
                dfa[next_states] = {}
                queue.append(next_states)

            dfa[tuple(sorted(current_states))][symbol] = next_states
    return dfa


dfa = nfa_to_dfa(transition_table)
dfa_1 = dfa.copy()
m = len(dfa.keys())
alphabett = string.ascii_uppercase
statee = list(alphabett)[:m]
updated_data = {}
aa = list(dfa_1.values())
bb = list(dfa_1.keys())
for i, key in enumerate(dfa_1.keys()):
    updated_data[statee[i]] = dfa_1[key]

for d in aa:
    for i in d.keys():
        for k in bb:
            if d[i] == k:
                d[i] = statee[bb.index(k)]

finalll = []
for i in dfa_1.keys():
    for o in i:
        if o in final_state:
            finalll.append(statee[bb.index(i)])

paths.remove('lambda')

user_input_string = user_input_string.strip('"')


def is_accepted(string, dfa, current_state, final):
    if not string:
        return current_state in final

    next_input = string[0]

    if next_input not in dfa[current_state]:
        return False

    next_state = dfa[current_state][next_input]

    return is_accepted(string[1:], dfa, next_state, final)


if is_accepted(user_input_string, updated_data, statee[0], final=finalll):
    print("رشته قابل قبول است.")
    result = 'accepted'
else:
    print("رشته قابل قبول نیست.")
    result = 'rejected'


def save_dfa_to_txt(dfa, filename):
    with open(filename, 'w') as f:
        for state, transitions in dfa.items():
            for symbol, next_state in transitions.items():
                f.write(f"{state} {symbol} {next_state}\n")
        f.write(f'result is : {result}')


filename = "dfa.txt"
save_dfa_to_txt(updated_data, filename)

dfa = VisualDFA(
    states=set(statee),
    input_symbols=set(paths),
    transitions=updated_data,
    initial_state=statee[0],
    final_states=set(finalll),
)

print(dfa.table)
pdd = pd.DataFrame(updated_data)
dfa.show_diagram(view=True, path='./')

import plotly.graph_objects as go
import re

def calculate_costs(plan_text, problem_pddl_text):
    # Initialize total costs
    total_cost_robot = 0
    total_cost_human = 0
    total_time = 0

    # Extract the makespan (total time) from the plan
    makespan_match = re.search(r'; Makespan: ([\d\.]+)', plan_text)
    if makespan_match:
        total_time = float(makespan_match.group(1))
    else:
        print("Makespan not found in plan.")
        return

    # Extract action costs from problem.pddl
    action_costs = {'robot': {}, 'human': {}}
    cost_pattern = re.compile(r'\(=\(action_cost (\w+) (\w+)\) (\d+)\)')
    for line in problem_pddl_text.splitlines():
        match = cost_pattern.search(line)
        if match:
            agent, action, cost = match.groups()
            action_costs[agent][action] = int(cost)

    # Define actions that increase total cost
    cost_increasing_actions = {
        'execute_action',
        'execute_dynamic_action',
        'execute_action_with_tool',
        'execute_dynamic_action_with_tool'
    }

    # Parse the plan
    action_pattern = re.compile(r'\d+\.\d+: \((\w+)(?: ([^\)]+))?\) \[\d+\.\d+\]')
    for line in plan_text.splitlines():
        action_match = action_pattern.match(line.strip())
        if action_match:
            action_name, params = action_match.groups()
            if action_name in cost_increasing_actions:
                params_list = params.split()
                if action_name == 'execute_action':
                    action, agent, loc = params_list
                elif action_name == 'execute_dynamic_action':
                    action, agent, init_loc, end_loc = params_list
                elif action_name == 'execute_action_with_tool':
                    action, agent, loc, tool = params_list
                elif action_name == 'execute_dynamic_action_with_tool':
                    action, agent, init_loc, end_loc, tool = params_list
                else:
                    continue  # Skip if action is not recognized

                # Get the cost and add to the appropriate agent's total cost
                agent = agent.strip()
                action = action.strip()
                cost = action_costs.get(agent, {}).get(action, 0)
                if agent == 'robot':
                    total_cost_robot += cost
                elif agent == 'human':
                    total_cost_human += cost

    # Calculate total metric
    total_metric = total_cost_robot + total_cost_human + total_time

    # Output the results
    print(f"Total cost for robot: {total_cost_robot}")
    print(f"Total cost for human: {total_cost_human}")
    print(f"Total time (makespan): {total_time}")
    print(f"Total metric: {total_metric}")

    # Return the costs as a dictionary
    return {
        'total_cost_robot': total_cost_robot,
        'total_cost_human': total_cost_human,
        'total_time': total_time,
        'total_metric': total_metric
    }

# Example usage with your provided plan and problem.pddl:
# Read file problem_simple.plan

experiment = input("Enter the experiment number: ")
if experiment == '1':
    experiment = ''
    

with open(f'pddl/problem_simple{experiment}.plan', 'r') as file:
    plan_text = file.read()

# REad file problem_simple.pddl
with open(f'pddl/problem_simple{experiment}.pddl', 'r') as file:
    problem_pddl_text = file.read()
# Call the function
costs = calculate_costs(plan_text, problem_pddl_text)

# Sample data
total_cost_robot = costs['total_cost_robot']
total_cost_human = costs['total_cost_human']
total_time = costs['total_time']

# Create the 3D scatter plot
fig = go.Figure(data=[go.Scatter3d(
    x=[total_cost_robot],
    y=[total_cost_human],
    z=[total_time],
    mode='markers',
    marker=dict(
        size=10,
        color='red',
        opacity=0.8
    )
)])

# Set axis titles
fig.update_layout(
    scene=dict(
        xaxis_title='Total Cost (Robot)',
        yaxis_title='Total Cost (Human)',
        zaxis_title='Total Time (Makespan)',
    ),
    title="3D Interactive Plot of Cost and Time Components"
)

# Show the interactive plot
fig.show()

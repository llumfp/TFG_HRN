import json
import os
import re
from llm_agent_to_action import LLMAgentToActionAllocationReasoner

def read_json(file):
    with open(file) as f:
        return json.load(f)


class Agent:
    def __init__(self, agent_type, goals, goals_data, conditions, conditions_data) -> None:
        self.agent_type = agent_type
        self.conditions = conditions
        self.conditions_data = conditions_data
        self.goals = goals
        self.goals_data = goals_data
        self.subgoals = self.get_subgoals(goals, goals_data)
        self.predicted_subgoals = None
        
    def get_subgoals(self, goals, goals_data):
        subgoals = []
        for g in goals:
            for s in goals_data[g][f'subgoals_{self.agent_type}']:
                subgoals.append(s['task'])
        return subgoals
    
    def get_goals_from_subgoals(self, subgoal_disfavour):
        goals_final = []
        for g in self.goals:
            subgoals_g = [i['task'] for i in self.goals_data[g][f'subgoals_{self.agent_type}']]
            if set(subgoals_g).intersection(set(subgoal_disfavour)) != set():
                goals_final.append(g)
        return goals_final
    
    def get_goals_disfavour(self):
        subgoal_disfavour = []
        for ide in self.conditions:
            condi = self.conditions_data[ide]
            if self.agent_type in condi['condition']:
                subgoal_disfavour.extend(condi['disfavour'])
        print(subgoal_disfavour)
        subgoal_disfavour = [i for i in subgoal_disfavour if i in self.subgoals]
        goals_disfavour = self.get_goals_from_subgoals(subgoal_disfavour)
        return goals_disfavour
    
    def predict_goals_disfavour(self, llm_agent, condition = None):
        if self.predicted_subgoals == None and condition == None:
            if condition == None:
                condition = ''
                for i in self.conditions:
                    cond = self.conditions_data[i]['condition']
                    if self.agent_type in cond:
                        condition += cond
                        condition+= ' '
            subgoals = '\n'.join(self.subgoals)
            agent, subgoals_disfavour, subgoals_favour, pddl_costs = llm_agent.llm_pddl_action_costs_for_agent_condition(subgoals, condition)
            self.predicted_subgoals = subgoals_disfavour
        goals_disfavour = self.get_goals_from_subgoals(self.predicted_subgoals)
        return goals_disfavour



class PlanProblem:
    def __init__(self, goals: list, conditions: list) -> None:
        self.goals = goals
        self.conditions = conditions
        self.conditions_data = read_json('eval_scenarios/conditions.json')
        self.goals_data = read_json('eval_scenarios/goals_duration.json')   
        self.llm_agent = LLMAgentToActionAllocationReasoner(prompt_dir='prompts')
        self.robot = Agent('robot', goals, self.goals_data,self.conditions, self.conditions_data)
        self.human = Agent('human',goals, self.goals_data,self.conditions, self.conditions_data)

    def first_phase(self, condition = None):
        disfavour_robot = self.robot.get_goals_disfavour()
        disfavour_human = self.human.predict_goals_disfavour(self.llm_agent, condition)

    def create_pddl_problem(self, condition = None):
        # Inicializar estructuras de datos
        actions = set()
        action_duration = {'human': {}, 'robot': {}}
        action_cost = {'human': {}, 'robot': {}}
        action_loc = {}
        action_end_loc = {}
        locations = set()

        # Obtener los objetivos y recopilar datos necesarios
        for goal_id in self.goals:
            goal_data = self.goals_data[goal_id]
            goal_code = goal_data['goal_code']
            actions.add(goal_code)

            # Extraer loc y end_loc directamente desde el JSON
            loc = goal_data['loc'] if goal_data['loc'] else 'loc_default'  # Asignar loc desde JSON o valor por defecto
            end_loc = goal_data['end_loc']

            action_loc[goal_code] = loc
            action_end_loc[goal_code] = end_loc

            # Añadir ubicaciones a la lista de ubicaciones
            locations.add(loc)
            locations.add(end_loc)

            # Asignar duraciones por agente
            action_duration['human'][goal_code] = goal_data.get('total_duration_human', 0)
            action_duration['robot'][goal_code] = goal_data.get('total_duration_robot', 0)
        
        print(actions)

        # Obtener objetivos desfavorecidos para cada agente
        disfavour_robot_goals = self.robot.get_goals_disfavour()
        disfavour_human_goals = self.human.predict_goals_disfavour(self.llm_agent,condition)

        # Asignar costos a las acciones según si están desfavorecidas
        for action, goal_id in zip(actions, self.goals):
            # Asignar costo para el robot
            if goal_id in disfavour_robot_goals:
                action_cost['robot'][action] = 20
            else:
                action_cost['robot'][action] = 0

            # Asignar costo para el humano
            if goal_id in disfavour_human_goals:
                action_cost['human'][action] = 20
            else:
                action_cost['human'][action] = 0

        # Generar el problema PDDL
        problem_pddl = "(define (problem problem_basic_duration)\n"
        problem_pddl += "(:domain domain_basic_duration)\n\n"

        # Definir objetos
        problem_pddl += "(:objects\n"
        problem_pddl += "    human robot - agent\n"
        problem_pddl += "    " + " ".join(sorted(locations)) + " - loc\n"
        problem_pddl += "    " + " ".join([action.replace(' ', '__') for action in actions]) + " - action\n"
        problem_pddl += ")\n\n"

        # Definir condiciones iniciales
        problem_pddl += "(:init\n"
        problem_pddl += "    (agent_not_busy robot)\n"
        problem_pddl += "    (agent_not_busy human)\n\n"
        # Ubicación inicial de los agentes (puedes ajustar según tus necesidades)
        problem_pddl += "    (is_at human loc1)\n"  # Ubicación inicial del humano
        problem_pddl += "    (is_at robot loc2)\n\n"  # Ubicación inicial del robot

        # Definir ubicaciones de acciones
        for action in actions:
            action_concat = action.replace(' ', '__')
            loc = action_loc.get(action, 'loc_default')
            end_loc = action_end_loc.get(action, 'loc_default_end')  # Puedes definir un valor por defecto para end_loc si es necesario
            problem_pddl += f"    (action_loc {action_concat} {loc})\n"
            problem_pddl += f"    (action_end_loc {action_concat} {end_loc})\n"
        problem_pddl += "\n"

        # Definir duraciones de acciones
        for agent in ['human', 'robot']:
            for action in actions:
                duration = action_duration[agent].get(action)
                if duration is not None:
                    action_concat = action.replace(' ', '__')
                    problem_pddl += f"    (=(action_duration {agent} {action_concat}) {duration})\n"
        problem_pddl += "\n"

        # Definir costos de acciones
        for agent in ['human', 'robot']:
            for action in actions:
                cost = action_cost[agent].get(action, 0)
                action_concat = action.replace(' ', '__')
                problem_pddl += f"    (=(action_cost {agent} {action_concat}) {cost})\n"
        problem_pddl += "\n"

        # Inicializar costos totales
        problem_pddl += "    (= (total-cost robot) 0)\n"
        problem_pddl += "    (= (total-cost human) 0)\n"
        problem_pddl += ")\n"

        # Definir metas
        problem_pddl += "(:goal (and\n"
        for action in actions:
            action_concat = action.replace(' ', '__')
            problem_pddl += f"    (action_done {action_concat})\n"
        problem_pddl += "    ))\n"

        # Definir métrica
        problem_pddl += "(:metric minimize (+ (* 1 (total-cost robot)) (* 1 (total-cost human)) (* 1 (total-time))))\n"
        problem_pddl += ")\n"

        # Guardar el problema en un archivo
        with open('problem_basic_duration_generated.pddl', 'w') as f:
            f.write(problem_pddl)
        print("PDDL problem generated successfully.")

goals = ['2', '3', '4', '6']
conditions = ['2', '4', '5', '8']


problem = PlanProblem(goals, conditions)

problem.create_pddl_problem()
   
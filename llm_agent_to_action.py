from pydantic import BaseModel
import openai
import re
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)  # for exponential backoff

# class Action:
#     object: str
#     verb: str
#     location: str

# class DisfavourFavour(BaseModel):
#     favourable_robot: list[Action]
#     favourable_human: list[Action]
#     disfavourable_robot: list[Action]
#     disfavourable_human: list[Action]
#     explanation: str

class LLMAgentToActionAllocationReasoner:

    def __init__(self, prompt_dir):
        self.prompt_dir = prompt_dir
        self.cost_preference = 100
        self.cost_state = 100

    def llm_get_action_costs_for_agent(self, subgoals, state, preference, agent):

        pddl_costs_prefs = []
        pddl_costs_state = []
        subgoals_avoid_pref_list = []
        subgoals_avoid_pref_list = []

        # TODO: poner lo repetido de abajo en una sola funcion
        print(subgoals)
        # query llm for subgoals to avoid due to agent preferences and state
        if preference:
            preference_prompt = self.create_preference_state_prompt(subgoals, preference)
            subgoals_to_avoid_pref = self.query_llm(preference_prompt)
            subgoals_to_avoid_pref = subgoals_to_avoid_pref.split("\n")
            if subgoals_to_avoid_pref:
                subgoals_avoid_pref_list = self.filter_subgoals(subgoals_to_avoid_pref, subgoals)
                if subgoals_avoid_pref_list:
                    print(subgoals_to_avoid_pref)
                    # translate to corresponding action costs (predicate_cost agent object location)
                    pddl_costs_prefs = [self.action_cost_from_subgoal(subgoal, self.cost_preference, agent) for subgoal in subgoals_avoid_pref_list]
                    print(pddl_costs_prefs)
        if state:
            state_prompt = self.create_preference_state_prompt(subgoals, state)
            subgoals_to_avoid_state = self.query_llm(state_prompt)
            subgoals_to_avoid_state = subgoals_to_avoid_state.split("\n")
            if subgoals_to_avoid_state:
                subgoals_avoid_state_list = self.filter_subgoals(subgoals_to_avoid_state, subgoals)
                if subgoals_avoid_state_list:
                    print(subgoals_avoid_pref_list)
                    # translate to corresponding action costs (predicate_cost agent object location)
                    pddl_costs_state = [self.action_cost_from_subgoal(subgoal, self.cost_state, agent) for subgoal in subgoals_avoid_state_list]
                    print(pddl_costs_state)

        subgoals_to_avoid = subgoals_avoid_pref_list + subgoals_avoid_pref_list #TODO: remove duplicates

        pddl_costs = pddl_costs_prefs + pddl_costs_state #TODO: remove duplicates

        return subgoals_to_avoid, pddl_costs

    def llm_pddl_action_costs_for_agent_condition(self, subgoals, condition):

        subgoals_favour_filtered, subgoals_disfavour_filtered, pddl_costs_disfavour, pddl_costs_favour = [], [], [], []

        if 'robot' in condition:
            agent = 'robot'
            other_agent = 'human'
            condition = condition.replace('robot', 'agent')
        elif 'human' in condition:
            agent = 'human'
            other_agent = 'robot'
            condition = condition.replace('human', 'agent')
        else: return False # TODO: handle this error

        prompt = self.create_favour_disfavour_prompt(subgoals, condition)
        llm_response = self.query_llm(prompt)
        # disfavour = re.search('disfavour these tasks:\n(.*)\n\nThe agent should', llm_response)
        # subgoals_disfavour = disfavour.group(1)
        # favour = re.search('favour the tasks:\n(.*)', llm_response)
        # subgoals_favour = favour.group(1)
        print(llm_response)
        subgoals_disfavour = self.extract_disfavour_subgoals(llm_response)
        subgoals_favour = self.extract_favour_subgoals(llm_response)

        if subgoals_disfavour != 'None' and subgoals_disfavour:
            subgoals_disfavour_list = subgoals_disfavour.split('\n')
            subgoals_disfavour_filtered = self.filter_subgoals(subgoals_disfavour_list, subgoals)
            pddl_costs_disfavour = [self.action_cost_from_subgoal(subgoal, self.cost_state, agent) for subgoal in subgoals_disfavour_filtered]
        if subgoals_favour != 'None' and subgoals_favour:
            subgoals_favour_list = subgoals_favour.split('\n')
            subgoals_favour_filtered = self.filter_subgoals(subgoals_favour_list, subgoals)
            pddl_costs_favour = [self.action_cost_from_subgoal(subgoal, self.cost_state, other_agent) for subgoal in subgoals_favour_filtered]

        pddl_costs = pddl_costs_disfavour + pddl_costs_favour

        return agent, subgoals_disfavour_filtered, subgoals_favour_filtered, pddl_costs
    
    def llm_pddl_action_costs_for_subgoals(self, agent, subgoals_disfavour, subgoals_favour):

        pddl_costs_disfavour, pddl_costs_favour = [], [], [], []

        if agent == 'robot':
            other_agent = 'human'
        elif agent == 'human':
            other_agent = 'robot'
        else: return False # TODO: handle this error

        if subgoals_disfavour != []:
            pddl_costs_disfavour = [self.action_cost_from_subgoal(subgoal, self.cost_state, agent) for subgoal in subgoals_disfavour]
        if subgoals_favour != []:
            pddl_costs_favour = [self.action_cost_from_subgoal(subgoal, self.cost_state, other_agent) for subgoal in subgoals_favour]

        pddl_costs = pddl_costs_disfavour + pddl_costs_favour

        return pddl_costs
    
    def llm_subgoals_for_agent_condition(self, subgoals, condition):

        subgoals_favour_filtered, subgoals_disfavour_filtered = [], [], [], []

        if 'robot' in condition:
            agent = 'robot'
            condition = condition.replace('robot', 'agent')
        elif 'human' in condition:
            agent = 'human'
            condition = condition.replace('human', 'agent')
        else: return False # TODO: handle this error

        prompt = self.create_favour_disfavour_prompt(subgoals, condition)
        llm_response = self.query_llm(prompt)
        # disfavour = re.search('disfavour these tasks:\n(.*)\n\nThe agent should', llm_response)
        # subgoals_disfavour = disfavour.group(1)
        # favour = re.search('favour the tasks:\n(.*)', llm_response)
        # subgoals_favour = favour.group(1)
        subgoals_disfavour = self.extract_disfavour_subgoals(llm_response)
        subgoals_favour = self.extract_favour_subgoals(llm_response)

        if subgoals_disfavour != 'None' and subgoals_disfavour:
            subgoals_disfavour_list = subgoals_disfavour.split('\n')
            subgoals_disfavour_filtered = self.filter_subgoals(subgoals_disfavour_list, subgoals)
        if subgoals_favour != 'None' and subgoals_favour:
            subgoals_favour_list = subgoals_favour.split('\n')
            subgoals_favour_filtered = self.filter_subgoals(subgoals_favour_list, subgoals)

        return agent, subgoals_disfavour_filtered, subgoals_favour_filtered

    def extract_disfavour_subgoals(self, llm_response):
        idx1 = llm_response.index("disfavour these tasks:\n")
        idx2 = llm_response.index("\n\nThe agent should favour")
        l = len("disfavour these tasks:\n")
        subgoals = llm_response[idx1 + l: idx2]
        return subgoals

    def extract_favour_subgoals(self, llm_response):
        idx1 = llm_response.index("favour the tasks:\n")
        l = len("favour the tasks:\n")
        subgoals = llm_response[idx1 + l:]
        subgoals = subgoals.rstrip("\n\n")
        return subgoals
    
    def filter_subgoals(self, subgoals_llm_list, subgoals_list):
        subgoals_llm_list = [subgoal for subgoal in subgoals_llm_list if subgoal in subgoals_list]
        print(subgoals_llm_list)
        return subgoals_llm_list
    
    def action_cost_from_subgoal(self, subgoal, value, agent):
        subgoal_split = subgoal.split(", ")
        print(subgoal_split)
        if len(subgoal_split)>1:
            pddl_action_cost = {"attribute": subgoal_split[1] + "_cost", "agent": agent, "obj": subgoal_split[0], "loc": subgoal_split[2], "value": value}
            print(pddl_action_cost)
            return pddl_action_cost
        else:
            return {}

    def get_predicate_from_subgoal(self, subgoal):
        subgoal_predicate = subgoal[subgoal.index(", ")+2:]
        subgoal_predicate = subgoal_predicate[:subgoal_predicate.index(",")]
        subgoal_predicate = subgoal_predicate.replace(" ", "_")
        return subgoal_predicate

    def create_preference_state_prompt(self, subgoals, agent_preference_or_state):
        prompt_file = self.prompt_dir + "/agent_event_prompt.txt"
        with open(prompt_file) as file:
            prompt_examples = file.read()
        prompt = prompt_examples + "I have the following goals:\n\n" + '\n'.join(subgoals) + "\n\n" + agent_preference_or_state + " Which goals, if any, should this person avoid?"
        print (prompt)
        return prompt

    def create_avoid_prompt(self, subgoals, agent_condition):
        prompt = "A human and a robot are collaborating together to achieve some goals. Each goal is assigned to one of the two agents.\n\nI have the following goals:\n\nmop, used to clean, floor \ncloth, used to clean, floor \nknife, tidied up, table \nnapkin, tidied up, table\nsalmon, cooked, hob \n\nThe person is distracted.\
            Which goals, if any, should this agent avoid?\n\nsalmon, cooked, hob\nknife, tidied up, table \n\nI have the following goals:\n\nmop, used to clean, floor \ncloth, used to clean, floor \nknife, tidied up, table \
                \nnapkin, tidied up, table \nsalmon, cooked, hob\n\nThe human has back problems. Which goals, if any, should this agent avoid?\n\nmop, used to clean, floor \ncloth, used to clean, floor\n\n\
                    I have the following goals:\n\nspoon, tidied up, drawer \n\n The human is distracted. The human has back problems. Which goals, if any, should this agent avoid?\n\nNone\n\n\
                    I have the following goals:\n\nfork, tidied up, drawer \n\n The robot has low dexterity. Which goals, if any, should this agent avoid?\n\nNone\n\n\
                        I have the following goals:\n\n" + '\n'.join(subgoals) + "\n\n" + agent_condition + " Which goals, if any, should this agent avoid?"
        return prompt
    
    def create_favour_disfavour_prompt(self, subgoals, agent_condition):
        prompt_file = self.prompt_dir + "/agent_disfavour_favour_prompt.txt"
        with open(prompt_file) as file:
            prompt_examples = file.read()
        prompt = prompt_examples + "\n\nI have the following tasks:\n" + subgoals + "\n\n" + agent_condition
        return prompt

    def create_favour_prompt(self, subgoals, agent_condition):
        prompt_file = self.prompt_dir + "/agent_favour_prompt.txt"
        with open(prompt_file) as file:
            prompt_examples = file.read()
        prompt = prompt_examples + "\n\nTest:\nI have the following goals:\n\n" + subgoals + "\n\n" + agent_condition + " Which goals, if any, should be assigned to this agent?"
        return prompt

    def create_disfavour_prompt(self, subgoals, agent_condition):
        prompt_file = self.prompt_dir + "/agent_disfavour_prompt.txt"
        with open(prompt_file) as file:
            prompt_examples = file.read()
        prompt = prompt_examples + "\n\nTest:\nI have the following goals:\n\n" + subgoals + "\n\n" + agent_condition + " Which goals, if any, should not be assigned to this agent?"
        return prompt

    def query_llm(self, prompt):

        client = openai.OpenAI()

        # Función de reintento con backoff exponencial
        @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(100))
        def completion_with_backoff(**kwargs):
            # return client.beta.chat.completions.parse(**kwargs)
            return client.chat.completions.create(**kwargs)

        # Definimos los mensajes en formato de chat
        messages = [
            {"role": "system", "content": "You are a helpful assistant that will have to select if and agent has to favour or disfavour some tasks. Follow very strictly the format from the given examples."},
            {"role": "user", "content": prompt}
        ]

        # Llamada al modelo GPT-4o-mini
        response = completion_with_backoff(
            model="gpt-4o-mini",
            messages=messages,
            # response_format=DisfavourFavour,
            temperature=0,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        message = response.choices[0].message.content.lstrip("\n")

        if response == "None":
            response = ""

        return message
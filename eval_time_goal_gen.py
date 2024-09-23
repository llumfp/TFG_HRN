from llm_env_to_goal import LLMEnvToGoalReasoner
from llm_agent_to_action import LLMAgentToActionAllocationReasoner
import pandas as pd
import openai
import time
import os

from dotenv import load_dotenv

class EvalGoalGen:
    def __init__(self, csv_gt_scenarios):
        self.csv_gt_scenarios = csv_gt_scenarios
        self.timestr = time.strftime("%Y%m%d-%H%M%S")
        self.csv_output = "outputs/eval_time_goal_gen" + self.timestr + ".csv"
        self.log_data = []
        self.runs_per_goal = 5

        self.llm_env_to_goal = LLMEnvToGoalReasoner("prompts")
        self.llm_agent_to_action = LLMAgentToActionAllocationReasoner("prompts")

        self.pddl_predicates = ["used_to_clean", "stored", "cooked", "served", "placed"]

        self.objects = ['tea', 'pepsi', 'chicken', 'grapefruit drink', 'coffee cup', 'mop', 'coke', 'water bottle', 'napkin', 'cleaning cloth', 'broom', 'salmon', 'cereal', 'knife', 'peanuts', 'lime soda', 'jalapeno chips', 'coke', 'apple', 'bowl', 'rice chips', 'redbull', '7up', 'energy bar', 'fork', 'sponge', 'casserole']
        self.locations = ['refrigerator', 'trash can', 'cabinet', 'tablewear cupboard', 'food cupboard', 'microwave', 'far counter', 'close counter', 'table', 'grill', 'utensil drawer', 'floor', 'hob', 'oven', 'sink', 'dish rack', 'table']

    def subgoal_str_to_dict(self, subgoal):
        subgoal_split = subgoal.split(", ")
        subgoal_dict = {"attribute": subgoal_split[1], "obj": subgoal_split[0], "loc": subgoal_split[2]}
        return subgoal_dict

    def evaluate_test_cases(self, n_shots):

        header = pd.DataFrame([], columns=['Goal Type', 'Goal number', 'INPUT - Goal', 'n_run', 'time (s)'])
        header.to_csv(self.csv_output)

        df = pd.read_csv(self.csv_gt_scenarios)
        n_tests = df.shape[0]
        test_start = 1
        test_end = n_tests
        for goal in range(test_start-1, test_end):
            goal_type = df.iloc[goal, 1]
            goal_num = df.iloc[goal, 2]
            self.goal = df.iloc[goal, 3]
            print(self.goal)
            situation = [', '.join(self.objects), ', '.join(self.locations), self.goal]
            for n_run in range(1, self.runs_per_goal+1):
                # t1 START #
                t1_start = time.time()
                unfiltered_subgoals, subgoals_filtered_pddl, subgoals_filtered_common_sense, subgoals_filtered_goal_contrib = self.llm_env_to_goal.llm_subgoals_from_situation(situation, self.pddl_predicates, n_shots)
                # t1 STOP #
                t1_stop = time.time()
                t1 = t1_stop - t1_start

                # Log
                log_row = [goal_type, goal_num, self.goal, n_run, t1]
                data = pd.DataFrame([log_row])
                data.to_csv(self.csv_output, mode='a', header=False)

if __name__ == "__main__":
    load_dotenv()  
    csv_gt_scenarios = "eval_scenarios/eval_time_goal_gen_GT_scenarios.csv"
    
    openai.api_key = os.getenv("OPENAI_API_KEY")

    evalGoalGen = EvalGoalGen(csv_gt_scenarios)

    evalGoalGen.evaluate_test_cases(5)
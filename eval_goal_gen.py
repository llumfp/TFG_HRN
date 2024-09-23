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
        self.csv_output = "outputs/eval_goal_gen" + self.timestr + ".csv" #TODO: pass as parameter
        self.log_data = []

        self.llm_env_to_goal = LLMEnvToGoalReasoner("prompts")
        self.llm_agent_to_action = LLMAgentToActionAllocationReasoner("prompts")
        
        self.pddl_predicates = ["used_to_clean", "stored", "cooked", "served", "placed"] #TODO: get from PDDL domain?

        self.objects = ['tea', 'pepsi', 'chicken', 'grapefruit drink', 'coffee cup', 'mop', 'coke', 'water bottle', 'napkin', 'cleaning cloth', 'broom', 'salmon', 'cereal', 'knife', 'peanuts', 'lime soda', 'jalapeno chips', 'coke', 'apple', 'bowl', 'rice chips', 'redbull', '7up', 'energy bar', 'fork', 'sponge', 'casserole']
        self.locations = ['refrigerator', 'trash can', 'cabinet', 'tablewear cupboard', 'food cupboard', 'microwave', 'far counter', 'close counter', 'table', 'grill', 'utensil drawer', 'floor', 'hob', 'oven', 'sink', 'dish rack', 'table']

    def subgoal_str_to_dict(self, subgoal):
        subgoal_split = subgoal.split(", ")
        subgoal_dict = {"attribute": subgoal_split[1], "obj": subgoal_split[0], "loc": subgoal_split[2]}
        return subgoal_dict

    def evaluate_test_cases(self, n_shots):

        header = pd.DataFrame([], columns=['Test number', 'Goal number', 'INPUT - Goal', 'GT subgoals', \
                                           'OUTPUT - Subgoals no filter no grounding', 'METRIC 1: subgoal completeness - unfiltered and ungrounded', 'METRIC 2: subgoal correctness - unfiltered and ungrounded', 'avge unfiltered and ungrounded', 'METRIC 3: test success - unfiltered and ungrounded',\
                                            'OUTPUT - Subgoals after pddl filter', 'METRIC 1: subgoal completeness - unfiltered', 'METRIC 2: subgoal correctness - unfiltered', 'avge unfiltered', 'METRIC 3: test success - unfiltered',\
                                                'OUTPUT - Subgoals after common sense filter', 'OUTPUT - FINAL subgoals after goal contrib filter', 'METRIC 1: subgoal completeness', 'METRIC 2: subgoal correctness', 'avge', 'METRIC 3: test success'])
        header.to_csv(self.csv_output)

        df = pd.read_csv(self.csv_gt_scenarios)
        n_tests = df.shape[0]
        test_start = 1
        test_end = n_tests
        for test in range(test_start-1, test_end):
            success = 0
            success_unfiltered = 0
            test_number = test + 1
            goal_type = df.iloc[test, 1]
            goal_num = df.iloc[test, 2]
            self.goal = df.iloc[test, 3]
            print(self.goal)
            GT_subgoals = df.iloc[test, 5]
            situation = [', '.join(self.objects), ', '.join(self.locations), self.goal]

            # t1 START #
            unfiltered_subgoals, subgoals_filtered_pddl, subgoals_filtered_common_sense, subgoals_filtered_goal_contrib = self.llm_env_to_goal.llm_subgoals_from_situation(situation, self.pddl_predicates, n_shots)
            # t1 STOP #
            
            # unfiltered_subgoals = ["coke, placed, table", "spoon, stored, drawer"]
            # subgoals_filtered_pddl = ["coke, placed, table", "spoon, stored, drawer"]
            # subgoals_filtered_common_sense = ["coke, placed, table", "spoon, stored, drawer"]
            # subgoals_filtered_goal_contrib = ["coke, placed, table", "spoon, stored, drawer"]
            LLM_final_subgoals = subgoals_filtered_goal_contrib
            # GT_subgoals = ["mop, used to clean, floor"]

            # Calculate metrics
            if '[' in GT_subgoals: # several GT options are possible
                subgoal_completeness_unfilt_unground = 'manual_check'
                subgoal_correctness_unfilt_unground = 'manual_check'
                avge_unfilt_unground = 'manual_check'
                success_unfilt_unground = 'manual_check'
                subgoal_completeness_unfiltered = 'manual_check'
                subgoal_correctness_unfiltered = 'manual_check'
                avge_unfiltered = 'manual_check'
                success_unfiltered = 'manual_check'
                subgoal_completeness = 'manual_check'
                subgoal_correctness = 'manual_check'
                avge = 'manual_check'
                success = 'manual_check'
            else:
                GT_subgoals_list = GT_subgoals.split('/n')
                # Calculate metrics for unfiltered and ungrounded subgoals
                correct_subgoals_unfilt_unground = [subgoal for subgoal in unfiltered_subgoals if subgoal in GT_subgoals_list]
                subgoal_completeness_unfilt_unground = len(correct_subgoals_unfilt_unground)/len(GT_subgoals_list)
                if unfiltered_subgoals:
                    subgoal_correctness_unfilt_unground = len(correct_subgoals_unfilt_unground)/len(unfiltered_subgoals)
                else: subgoal_correctness_unfilt_unground = 0
                avge_unfilt_unground = (subgoal_completeness_unfilt_unground + subgoal_correctness_unfilt_unground) / 2
                if avge_unfilt_unground >= 0.75: success_unfilt_unground = 1

                # Calculate metrics for unfiltered subgoals (only after pddl filter but no LLM filters)
                correct_subgoals_unfiltered = [subgoal for subgoal in subgoals_filtered_pddl if subgoal in GT_subgoals_list]
                subgoal_completeness_unfiltered = len(correct_subgoals_unfiltered)/len(GT_subgoals_list)
                if subgoals_filtered_pddl:
                    subgoal_correctness_unfiltered = len(correct_subgoals_unfiltered)/len(subgoals_filtered_pddl)
                else: subgoal_correctness_unfiltered = 0
                avge_unfiltered = (subgoal_completeness_unfiltered + subgoal_correctness_unfiltered) / 2
                if avge_unfiltered >= 0.75: success_unfiltered = 1

                # Calculate metrics for final subgoals
                correct_subgoals = [subgoal for subgoal in LLM_final_subgoals if subgoal in GT_subgoals_list]
                subgoal_completeness = len(correct_subgoals)/len(GT_subgoals_list)
                if LLM_final_subgoals:
                    subgoal_correctness = len(correct_subgoals)/len(LLM_final_subgoals)
                else: subgoal_correctness = 0
                avge = (subgoal_completeness + subgoal_correctness) / 2
                if avge >= 0.75: success = 1

            log_row = [test_number, goal_num, self.goal, GT_subgoals, unfiltered_subgoals, subgoal_completeness_unfilt_unground, subgoal_correctness_unfilt_unground, avge_unfilt_unground, success_unfilt_unground,\
                       subgoals_filtered_pddl, subgoal_completeness_unfiltered, subgoal_correctness_unfiltered, avge_unfiltered, success_unfiltered,\
                        subgoals_filtered_common_sense, LLM_final_subgoals, subgoal_completeness, subgoal_correctness, avge, success]
            data = pd.DataFrame([log_row])
            data.to_csv(self.csv_output, mode='a', header=False)

if __name__ == "__main__":

    # Input csv path
    csv_gt_scenarios = "eval_scenarios/eval_goal_gen_GT_scenarios_sample.csv"

    openai.api_key = os.getenv("OPENAI_API_KEY")

    evalGoalGen = EvalGoalGen(csv_gt_scenarios)

    evalGoalGen.evaluate_test_cases(5)
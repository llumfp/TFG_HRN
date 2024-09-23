import openai
import re
import sys
import time


from llm_env_to_goal import LLMEnvToGoalReasoner
from llm_agent_to_action import LLMAgentToActionAllocationReasoner
import pandas as pd
from threading import Thread


class EvalAgentAdapt:
    def __init__(self, csv_gt_scenarios, mode):
        self.mode = mode
        self.csv_gt_scenarios = csv_gt_scenarios
        self.timestr = time.strftime("%Y%m%d-%H%M%S")
        self.csv_output = "outputs/eval_agent_adapt" + self.timestr + ".csv" #TODO: pass as parameter
        self.log_data = []

        self.llm_env_to_goal = LLMEnvToGoalReasoner("prompts")
        self.llm_agent_to_action = LLMAgentToActionAllocationReasoner("prompts")

        self.rosplan_interface = RosPlanInterface()

        self.domain_path = "/home/silvia.izquierdo/planning_llm/src/application_kitchen_v2/pddl/kitchen_collab_domain_lowlevel.pddl" #TODO: pass as parameter
        self.problem_path = "/home/silvia.izquierdo/planning_llm/src/application_kitchen_v2/pddl/kitchen_collab_problem_lowlevel.pddl" #TODO: pass as parameter

        # self.objects = ["coffee cup", "mop", "coke", "napkin", "cleaning cloth", "broom", "salmon", "cereal", "knife", "peanuts", "lime soda", "jalapeno chips", "coke", "apple", "bowl", "redbull"]
        # self.locations = ["refrigerator", "trash can", "cabinet", "tablewear cupboard", "food cupboard", "microwave", "kitchen counter", "dining table", "grill", "utensil drawer", "floor", "hob", "oven", "sink", "dish rack"]
        self.agent_cost_track = []

        self.received_plan = False

        self.plan_subscriber = rospy.Subscriber('/rosplan_planner_interface/planner_output', String, self.raw_plan_callback)

    def raw_plan_callback(self, msg):
        self.raw_plan = msg.data
        self.received_plan = True

    def wait_for_plan(self, timeout, period=1):
        mustend = time.time() + timeout
        while time.time() < mustend:
            if self.received_plan:
                return True
            time.sleep(period)
        return False

    def parse_raw_plan(self, raw_plan):
        plan_action = re.compile(r"(.*):\s*\((.*)\)\s*\[(.*)\]", re.MULTILINE)        
        plan = re.findall(plan_action, raw_plan)
        plan = [(float(p[0]), p[1].split(' '), float(p[2])) for p in plan]
        return plan
    
    def subgoal_str_to_dict(self, subgoal):
        subgoal_split = subgoal.split(", ")
        subgoal_dict = {"attribute": subgoal_split[1], "obj": subgoal_split[0], "loc": subgoal_split[2]}
        return subgoal_dict

    def evaluate_test_cases(self):

        header = pd.DataFrame([], columns=['Test number', 'Condition number', 'INPUT - Condition', 'INPUT - scenario', 'INPUT - subgoals',\
                                            'GT subgoals to disfavour', 'GT subgoals to favour', 'OUTPUT - LLM subgoals to disfavour', 'subgoals disfavour correctness', 'subgoals disfavour completeness',\
                                                'OUTPUT - LLM subgoals to favour', 'subgoals favour correctness', 'subgoals favour completeness', 'OUTPUT - Plan',  \
                                                      'plan success', 'subgoals to disfavour not in plan', 'subgoals to favour in plan'])
        header.to_csv(self.csv_output)

        # Get row from excel
        df = pd.read_csv(self.csv_gt_scenarios)
        n_tests = df.shape[0]
        test_start = 49
        test_end = 52
        for test in range(test_start-1, test_end):
            # Get test info
            test_number = test + 1
            condition_num = df.iloc[test, 2]
            condition = df.iloc[test, 3]
            scenario = df.iloc[test, 4]
            subgoals = df.iloc[test, 6]
            GT_disfavour = df.iloc[test, 7]
            GT_favour = df.iloc[test, 8]

            # t2 START #
            # If llm and planning done in one stage:
            agent, subgoals_disfavour, subgoals_favour, pddl_costs = self.llm_agent_to_action.llm_pddl_action_costs_for_agent_condition(subgoals, condition)
            # t2 STOP #

            # Else, first get subgoals for agents from llm and then plan (can get subgoals from excel instead)
            # agent, subgoals_disfavour, subgoals_favour = self.llm_agent_to_action.llm_subgoals_for_agent_condition(subgoals, condition)
            # pddl_costs = self.llm_agent_to_action.llm_pddl_action_costs_for_subgoals(agent, subgoals_disfavour, subgoals_favour)

            # Launch rosplan
            # t3 START #
            rospy.loginfo("Launching ROSPLAN")
            self.rosplan_interface.launch_scenario(self.domain_path, self.problem_path, "true")
            # self.pddl_goal_predicates = self.rosplan_interface.get_pddl_instances('goal_predicates')

            # Add subgoals to PDDL problem
            for subgoal in subgoals.split('\n'):
                goal_dict = self.subgoal_str_to_dict(subgoal)
                self.rosplan_interface.add_pddl_goal(goal_dict)

            # TODO: Add costs to PDDL problem
            for action_cost in pddl_costs:
                self.rosplan_interface.add_pddl_cost(action_cost)

            # Generate problem and plan
            self.raw_plan = ""
            self.plan()
            # t3 STOP #
            # TODO: wait for plan to arrive in self.raw_plan?
            time.sleep(2)
            if self.raw_plan:
                plan_success = 1
            else: plan_success = 0
            subgoals_disfavour_not_in_plan = 1
            subgoals_favour_in_plan = 1
            if plan_success:
                # TODO: que estos sean over the GT para tener metrics que make sense
                parsed_plan = self.parse_raw_plan(self.raw_plan)
                for subgoal in subgoals_favour:
                    subgoals_favour_in_plan = 0
                    subgoal_dict = self.subgoal_str_to_dict(subgoal)
                    for action in parsed_plan:
                        if agent in action[1] and subgoal_dict['obj'].replace(' ', '_') in action[1] and subgoal_dict['loc'].replace(' ', '_') in action[1]:
                            subgoals_favour_in_plan = 1
                            break
                for subgoal in subgoals_disfavour:
                    subgoal_dict = self.subgoal_str_to_dict(subgoal)
                    for action in parsed_plan:
                        if agent in action[1] and subgoal_dict['obj'].replace(' ', '_') in action[1] and subgoal_dict['loc'].replace(' ', '_') in action[1]:
                            subgoals_disfavour_not_in_plan = 0
                            break
                self.rosplan_interface.launch_shutdown()
            
            log_row = [test_number, condition_num, condition, scenario, subgoals, GT_disfavour, GT_favour, subgoals_disfavour, '', '', subgoals_favour, '', '', self.raw_plan, plan_success, subgoals_disfavour_not_in_plan, subgoals_favour_in_plan]
            data = pd.DataFrame([log_row])
            data.to_csv(self.csv_output, mode='a', header=False)
            
            self.rosplan_interface.launch_shutdown()

    def plan(self):
        rospy.loginfo("Generating new problem")
        self.rosplan_interface.generate_problem()
        # Generate new plan
        rospy.loginfo("Generating new plan")
        self.rosplan_interface.generate_plan()
        # plan_ready = self.wait_for_plan(self.received_plan, 40) TODO: doesn't always work
        plan_ready = True
        self.received_plan = False
        rospy.loginfo("Plan generated")

if __name__ == "__main__":

    rospy.init_node('eval_plan_adapt', anonymous=True) 
    # mode = str(rospy.get_param('~mode', "llm")) #take from python param terminal?
    mode = 'llm'
    csv_gt_scenarios = "/home/silvia.izquierdo/planning_llm/src/application_kitchen_v2/eval_scenarios/eval_agent_adapt_GT_scenarios.csv"

    openai.api_key = "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" #TODO: from file

    evalAgentAdapt = EvalAgentAdapt(csv_gt_scenarios, mode)

    evalAgentAdapt.evaluate_test_cases()
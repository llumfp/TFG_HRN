import openai
import re
import os
import time

from llm_env_to_goal import LLMEnvToGoalReasoner
from llm_agent_to_action import LLMAgentToActionAllocationReasoner
import pandas as pd
from threading import Thread

from dotenv import load_dotenv

class EvalAgentAdapt:
    def __init__(self, csv_gt_scenarios, mode):
        self.mode = mode
        self.csv_gt_scenarios = csv_gt_scenarios
        self.timestr = time.strftime("%Y%m%d-%H%M%S")
        self.csv_output = "outputs/eval_agent_adapt" + self.timestr + ".csv" # TODO: pass as parameter
        self.log_data = []

        self.llm_env_to_goal = LLMEnvToGoalReasoner("prompts")
        self.llm_agent_to_action = LLMAgentToActionAllocationReasoner("prompts")

        # Comentado: Partes relacionadas con ROS y planificación
        # self.rosplan_interface = RosPlanInterface()

        # self.domain_path = "/home/silvia.izquierdo/planning_llm/src/application_kitchen_v2/pddl/kitchen_collab_domain_lowlevel.pddl"  # TODO: pass as parameter
        # self.problem_path = "/home/silvia.izquierdo/planning_llm/src/application_kitchen_v2/pddl/kitchen_collab_problem_lowlevel.pddl"  # TODO: pass as parameter

        # self.agent_cost_track = []

        # self.received_plan = False

        # self.plan_subscriber = rospy.Subscriber('/rosplan_planner_interface/planner_output', String, self.raw_plan_callback)

    # Comentado: Métodos relacionados con ROS y planificación
    # def raw_plan_callback(self, msg):
    #     self.raw_plan = msg.data
    #     self.received_plan = True

    # def wait_for_plan(self, timeout, period=1):
    #     mustend = time.time() + timeout
    #     while time.time() < mustend:
    #         if self.received_plan:
    #             return True
    #         time.sleep(period)
    #     return False

    # def parse_raw_plan(self, raw_plan):
    #     plan_action = re.compile(r"(.*):\s*\((.*)\)\s*\[(.*)\]", re.MULTILINE)
    #     plan = re.findall(plan_action, raw_plan)
    #     plan = [(float(p[0]), p[1].split(' '), float(p[2])) for p in plan]
    #     return plan

    def subgoal_str_to_dict(self, subgoal):
        subgoal_split = subgoal.split(", ")
        subgoal_dict = {"attribute": subgoal_split[1], "obj": subgoal_split[0], "loc": subgoal_split[2]}
        return subgoal_dict

    def evaluate_test_cases(self):

        header = pd.DataFrame([], columns=['Test number', 'Condition number', 'INPUT - Condition', 'INPUT - scenario', 'INPUT - subgoals',
                                           'GT subgoals to disfavour', 'GT subgoals to favour', 'OUTPUT - LLM subgoals to disfavour',
                                           'subgoals disfavour correctness', 'subgoals disfavour completeness',
                                           'OUTPUT - LLM subgoals to favour', 'subgoals favour correctness', 'subgoals favour completeness'])
        header.to_csv(self.csv_output)

        # Obtener filas del CSV
        df = pd.read_csv(self.csv_gt_scenarios)
        n_tests = df.shape[0]
        test_start = 1
        test_end = n_tests
        for test in range(test_start - 1, test_end):
            # Obtener información del test
            test_number = test + 1
            condition_num = df.iloc[test, 1]
            condition = df.iloc[test, 2]
            scenario = df.iloc[test, 3]
            subgoals = df.iloc[test, 5]
            GT_disfavour = df.iloc[test, 6]
            GT_favour = df.iloc[test, 7]

            # Llamada al LLM para obtener subgoals favorecidos y desfavorecidos
            agent, subgoals_disfavour, subgoals_favour, pddl_costs = self.llm_agent_to_action.llm_pddl_action_costs_for_agent_condition(subgoals, condition)

            # Procesar subgoals GT
            if isinstance(GT_disfavour, str) and (GT_disfavour.lower() == 'none' or GT_disfavour.strip() == ''):
                GT_disfavour_list = []
            else:
                GT_disfavour_list = GT_disfavour.strip().split('\n')

            if isinstance(GT_favour, str) and (GT_favour.lower() == 'none' or GT_favour.strip() == ''):
                GT_favour_list = []
            else:
                GT_favour_list = GT_favour.strip().split('\n')

            # Calcular métricas de corrección y completitud para subgoals desfavorecidos
            if subgoals_disfavour:
                correct_subgoals_disfavour = [subgoal for subgoal in subgoals_disfavour if subgoal in GT_disfavour_list]
                disfavour_correctness = len(correct_subgoals_disfavour) / len(subgoals_disfavour) if len(subgoals_disfavour) > 0 else None
                disfavour_completeness = len(correct_subgoals_disfavour) / len(GT_disfavour_list) if len(GT_disfavour_list) > 0 else None
            else:
                disfavour_correctness = None
                disfavour_completeness = None

            # Calcular métricas de corrección y completitud para subgoals favorecidos
            if subgoals_favour:
                correct_subgoals_favour = [subgoal for subgoal in subgoals_favour if subgoal in GT_favour_list]
                favour_correctness = len(correct_subgoals_favour) / len(subgoals_favour) if len(subgoals_favour) > 0 else None
                favour_completeness = len(correct_subgoals_favour) / len(GT_favour_list) if len(GT_favour_list) > 0 else None
            else:
                favour_correctness = None
                favour_completeness = None

            # Registrar los resultados
            log_row = [test_number, condition_num, condition, scenario, subgoals, GT_disfavour, GT_favour,
                       subgoals_disfavour, disfavour_correctness, disfavour_completeness,
                       subgoals_favour, favour_correctness, favour_completeness]
            data = pd.DataFrame([log_row])
            data.to_csv(self.csv_output, mode='a', header=False)

    # Comentado: Método de planificación no necesario
    # def plan(self):
    #     rospy.loginfo("Generating new problem")
    #     self.rosplan_interface.generate_problem()
    #     # Generate new plan
    #     rospy.loginfo("Generating new plan")
    #     self.rosplan_interface.generate_plan()
    #     # plan_ready = self.wait_for_plan(self.received_plan, 40) TODO: doesn't always work
    #     plan_ready = True
    #     self.received_plan = False
    #     rospy.loginfo("Plan generated")

if __name__ == "__main__":
    load_dotenv()
    # Comentado: Inicialización de ROS no necesaria
    # rospy.init_node('eval_plan_adapt', anonymous=True)
    # mode = str(rospy.get_param('~mode', "llm")) #take from python param terminal?
    mode = 'llm'
    csv_gt_scenarios = "eval_scenarios/eval_agent_adapt_GT_scenarios.csv"

    openai.api_key = os.getenv("OPENAI_API_KEY")

    evalAgentAdapt = EvalAgentAdapt(csv_gt_scenarios, mode)

    evalAgentAdapt.evaluate_test_cases()

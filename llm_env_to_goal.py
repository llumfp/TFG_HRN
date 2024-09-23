import openai
import re
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)  # for exponential backoff


class LLMEnvToGoalReasoner:

    def __init__(self, prompt_dir):
        self.prompt_dir = prompt_dir

    def llm_subgoals_from_situation(self, situation, predicates, n_shot):

        # situation = [object_list, location_list, goal]
        subgoals = []

        subgoal_prompt = self.create_prompt_subgoals(
            situation[0], situation[1], situation[2], predicates, n_shot)

        subgoals_unfiltered = self.query_llm(subgoal_prompt)
        subgoals_unfiltered = subgoals_unfiltered.split("\n")

        if subgoals_unfiltered:
            # Filter subgoals
            object_list = situation[0].split(", ")
            location_list = situation[1].split(", ")
            subgoals_filtered_pddl = [subgoal for subgoal in subgoals_unfiltered if not self.filter_subgoal_ground_pddl(
                subgoal, predicates, object_list, location_list)[0]]
            subgoals_filtered_common_sense = [subgoal for subgoal in subgoals_filtered_pddl if not self.filter_subgoal_common_sense(
                situation[2], subgoal)[0]]
            subgoals_filtered_goal_contrib = [subgoal for subgoal in subgoals_filtered_common_sense if not self.filter_subgoal_goal_contrib(
                situation[2], subgoal)[0]]

        return subgoals_unfiltered, subgoals_filtered_pddl, subgoals_filtered_common_sense, subgoals_filtered_goal_contrib

    def filter_subgoal(self, goal, subgoal, predicates=[], objects=[], locations=[]):
        print("FILTERING: " + subgoal)

        #Remove the subgoal if it doesn't match any of the available PDDL predicates, locations or objects
        self.filter_subgoal_ground_pddl(subgoal, predicates, objects, locations)

        # Filter using common sense: Should OBJECT be PREDICATE in LOCATION?
        self.filter_subgoal_common_sense(goal, subgoal)

        # Filter to check if this subgoal contributes to the main goal.
        self.filter_subgoal_goal_contrib(goal, subgoal)
    
    def filter_subgoal_ground_pddl(self, subgoal, predicates=[], objects=[], locations=[]):
        subgoal_split = subgoal.split(', ')
        print(subgoal)
        print(predicates)
        print(objects)
        print(locations)
        if len(subgoal_split) != 3:
            return True, "incorrect_subgoal_format"
        subgoal_object = subgoal_split[0]
        subgoal_predicate = subgoal_split[1].replace(" ", "_")
        subgoal_location = subgoal_split[2]
        if subgoal_predicate not in predicates:
            print(subgoal_predicate)
            return True, "wrong_predicate"
        elif subgoal_object not in objects:
            print(subgoal_object)
            return True, "wrong_object"
        elif subgoal_location not in locations:
            print(subgoal_location)
            return True, "wrong_location"
        else: 
            return False, ""
    
    def filter_subgoal_common_sense(self, goal, subgoal):
        filter_prompt = self.create_prompt_filter_subgoal_common_sense(
            goal, subgoal)
        print(filter_prompt)
        response = self.query_llm(filter_prompt)
        print(response)
        if response == "No":
            return True, "common_sense"
        else: 
            return False, ""
    
    def filter_subgoal_goal_contrib(self, goal, subgoal):
        filter_prompt_goal = self.create_prompt_filter_subgoal_main_goal(
            goal, subgoal)
        response = self.query_llm(filter_prompt_goal)
        print(response)
        if response == "No":
            return True, "no_contrib_to_goal"
        else: 
            return False, ""

    def find_alternative_subgoal(self, event, goal, subgoals, predicates, objs_avail, locs_avail):
        prompt = self.create_prompt_alt_subgoal(
            event, goal, ", ".join(objs_avail), ", ".join(locs_avail), subgoals)
        response = self.query_llm(prompt)
        subgoal_affected = re.search('goal to be modified: (.*)\n', response)
        subgoal_affected = subgoal_affected.group(1)
        new_subgoal = response.split("new goal: ",1)[1]
        print(subgoal_affected)
        print(new_subgoal)
        if new_subgoal:
            not_valid = self.filter_subgoal(
                goal, new_subgoal, predicates, objs_avail, locs_avail)
            print(not_valid)
            if not not_valid:
                print(
                    "Alternative subgoal was found: %s", new_subgoal)
                return subgoal_affected, new_subgoal
        print("No alternative object was found.")
        return subgoal_affected, ""

    def check_different_subgoal(self, event, goal, subgoals, predicates, objs_avail, locs_avail):
        prompt = self.create_prompt_diff_subgoal(
            event, goal, subgoals)
        response = self.query_llm(prompt)
        print(response)
        old_subgoal = re.search('subgoal: (.*)\n', response)
        print(old_subgoal)
        old_subgoal = old_subgoal.group(1)
        new_subgoal = re.search('replaced by: (.*)', response)
        new_subgoal = new_subgoal.group(1)
        if old_subgoal:
            not_valid = self.filter_subgoal(
                goal, new_subgoal, predicates, objs_avail, locs_avail)
            print(not_valid)
            if not not_valid:
                print(
                    "Subgoal %s can be replaced by %s", old_subgoal, new_subgoal)
                return old_subgoal, new_subgoal
        print("Subgoal (%s) cannot be replaced by event (%s).", old_subgoal, event)
        return "", new_subgoal

    def subgoal_str_to_dict(self, subgoal):
        subgoal_split = subgoal.split(", ")
        subgoal_dict = {
            "attribute": subgoal_split[1], "obj": subgoal_split[0], "loc": subgoal_split[2]}
        return subgoal_dict

    def subgoal_dict_to_str(self, subgoal_dict):
        subgoal_str = subgoal_dict["obj"] + ", " + \
            subgoal_dict["attribute"] + ", " + subgoal_dict["loc"]
        return subgoal_str

    def create_prompt_alt_subgoal(self, event, goal, objects, locations, subgoals):
        prompt_file = self.prompt_dir + "/subgoal_altern_prompt.txt"
        with open(prompt_file) as file:
            prompt_examples = file.read()
        print(subgoals)
        prompt =  prompt_examples + "\n" + goal + "\nI have these available objects: " + objects + ".\nI have these available locations: " + locations + ".\n\nI have the following goals:\
        \n\n" + subgoals + "\n\n" + event + " Should any of these goals be modified? How?"
        print (prompt)
        return prompt
    
    def create_prompt_diff_subgoal(self, event, goal, subgoals):
        prompt_file = self.prompt_dir + "/subgoal_diff_prompt.txt"
        with open(prompt_file) as file:
            prompt_examples = file.read()
        prompt =  prompt_examples + "\nGoal: " + goal + "\nI have the following subgoals:\
        \n\n" + subgoals + "\n\n" + event + "Can this action substitute any of the subgoals?"
        print (prompt)
        return prompt

    def create_prompt_subgoals(self, obj_string, loc_string, goal, predicates, n_shot):
        prompt_file = self.prompt_dir + "/subgoals_gen_prompt_" + str(n_shot) + "shot.txt"
        with open(prompt_file) as file:
            prompt_examples = file.read()
        prompt = prompt_examples + "\nGoal: " + goal + "\nPredicates: " + (", ").join(predicates) + "\nObjects: " + obj_string + "\nLocations: " + loc_string + \
            "\n\nSubgoals:\n"
        return prompt

    def create_prompt_filter_subgoal_common_sense(self, goal, subgoal):
        subgoal_split = subgoal.split(',')
        # filter_prompt = "Use common sense. For the following questions, answer yes or no.\nShould a broom be stored in the floor?\n\nNo\n\n"\
        #     + "Should a cereal be served as snack in the table?\n\nYes\n\nShould a knife be stored in the utensil drawer?\n\nYes\n\n"\
        #         + "Should a " + subgoal_split[0] + " be " + subgoal_split[1] + " in the" + subgoal_split[2] + "?"

        # filter_prompt = "Use common sense. For the following questions, answer yes or no.\nA broom is stored in the floor. Does it make sense?\n\nNo\n\n"\
        #     + "A cereal is served as snack in the table. Does it make sense?\n\nYes\n\nA knife is stored in the utensil drawer. Does it make sense?\n\nYes\n\n"\
        #         + "A cup is served as snack in the table. Does it make sense?\n\nNo\n\nA fork is served as snack in the table. Does it make sense?\n\nNo\n\n"\
        #             + "A " + subgoal_split[0] + " is " + subgoal_split[1] + " in the" + subgoal_split[2] + ". Does it make sense?"
        filter_prompt = "Use common sense. For the following questions, answer yes or no.\n\nA broom is stored in the floor. Does it make sense?\n\nNo\n\n"\
            + "A cereal is served as snack in the table. Does it make sense?\n\nYes\n\nA coke is placed in the trash can. Does it make sense?\n\nYes\n\n"\
        + "An apple is placed in the far counter. Does it make sense?\n\nYes\n\nAn apple is placed in the trash can. Does it make sense?\n\nYes\n\n"\
        + "A drink is served in the close counter. Does it make sense?\n\nYes\n\n"\
        + "A " + subgoal_split[0] + " is " + subgoal_split[1] + \
            " in the" + subgoal_split[2] + ". Does it make sense?"

        return filter_prompt

    def create_prompt_filter_subgoal_main_goal(self, goal, subgoal):
        subgoal_split = subgoal.split(',')
        filter_prompt = "The goal is: I want to serve a quick snack. Would the following subgoal contribute to the goal? Answer yes or no.\nbanana, served as snack, table\n\nYes\n\n\
            The goal is: I want to clean a kitchen. Would the following subgoal contribute to the goal? Answer yes or no.\nbanana, served as snack, table\n\nNo\n\n\
                The goal is: " + goal + " Would the following subgoal contribute to the goal? Answer yes or no.\n" + subgoal_split[0] + " " + subgoal_split[1] + " " + subgoal_split[2]
        return filter_prompt

    def query_llm(self, prompt):

        print("HOLA ENTRAMOS")

        client = openai.OpenAI()

        # Función de reintento con backoff exponencial
        @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(100))
        def completion_with_backoff(**kwargs):
            return client.chat.completions.create(**kwargs)

        # Definimos los mensajes en formato de chat
        messages = [
            {"role": "user", "content": prompt}
        ]

        # Llamada al modelo GPT-4o-mini
        response = completion_with_backoff(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        print(response)

        message = response.choices[0].message.content.lstrip("\n")
        print(message)

        return message

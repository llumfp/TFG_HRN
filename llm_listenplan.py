from pydantic import BaseModel
import openai
import re
import os
import pandas as pd
import json
import ast
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)
from difflib import get_close_matches

class Goal(BaseModel):
    object: str
    verb: str
    location: str

class Plan(BaseModel):
    plan: list[Goal]
    explanation: str
    class Config:
        arbitrary_types_allowed = True 

class LLMListenPlanReasoner:

    def __init__(self, prompt_dir, goals_json_path):
        self.prompt_dir = prompt_dir
        # Cargamos los objetivos desde el JSON
        with open(goals_json_path, 'r', encoding='utf-8') as f:
            self.goals_data = json.load(f)
        
        # Crear un diccionario para mapear goal_number a goal_code y viceversa
        self.goal_number_to_code = {num: details['goal_code'] for num, details in self.goals_data.items()}
        self.goal_code_to_number = {details['goal_code']: num for num, details in self.goals_data.items()}
        
        # Lista de todos los goal_codes disponibles
        self.all_goal_codes = list(self.goal_code_to_number.keys())

    def process_human_texts(self, plans_df):
        results = []

        for index, row in plans_df.iterrows():
            num_plan = row['num_plan']
            text = row['plan']
            # Parseamos la lista de objetivos disponibles
            available_goals = ast.literal_eval(row['goals'])  # ['1','3','5']
            # Obtener los goal_codes correspondientes a los objetivos disponibles
            available_goal_codes = [self.goal_number_to_code[goal] for goal in available_goals]
            
            extracted_tasks = self.extract_tasks_from_text(text, available_goals, available_goal_codes)
            matched_tasks, unmatched_tasks = self.match_tasks(extracted_tasks, available_goal_codes)
            # Convertir goal_codes a números
            matched_goal_numbers = [self.goal_code_to_number[task] for task in matched_tasks]
            results.append({
                'num_plan': num_plan,
                'original_text': text,
                'matched_goal_numbers': matched_goal_numbers,
                'unmatched_tasks': unmatched_tasks,
                'plan_goals_GT': ast.literal_eval(row['plan_goals_GT'])
            })

        return pd.DataFrame(results)

    def extract_tasks_from_text(self, text, available_goals, available_goal_codes):
        # Preparar la información de los objetivos disponibles para el prompt
        goals_info = "\n".join([f"{num}: {self.goals_data[num]['goal_code']}" for num in available_goals])
        
        # Crear el prompt incluyendo los objetivos disponibles
        prompt = (
            f"Contexto: En este escenario, los objetivos disponibles son los siguientes:\n{goals_info}\n\n"
            f"Texto del humano:\n{text}\n\n"
            "Por favor, extrae la lista de tareas mencionadas en el texto que correspondan a los objetivos disponibles. "
            "Lista de tareas (usa los goal_codes exactamente como aparecen en la lista de objetivos):"
        )
        response_content = self.query_llm(prompt)
        response_dict = json.loads(response_content)
        extracted_tasks = []
        for task in response_dict['plan']:
            obj = task['object'].replace(' ', '_')
            verb = task['verb'].replace(' ', '_')
            loc = task['location'].replace(' ', '_')
            extracted_tasks.append(f"{obj} {verb} {loc}")

        print('--------------------------------')
        print(extracted_tasks)
        return extracted_tasks

    def match_tasks(self, extracted_tasks, available_goal_codes):
        matched_tasks = []
        unmatched_tasks = []

        for task in extracted_tasks:
            # Comprobamos si la tarea está en la lista de goal_codes disponibles
            if task in available_goal_codes:
                matched_tasks.append(task)
            else:
                # Buscamos tareas similares en los goal_codes disponibles
                similar_tasks = get_close_matches(task, available_goal_codes, n=1, cutoff=0.7)
                if similar_tasks:
                    # Nos quedamos con la tarea más similar
                    matched_tasks.append(similar_tasks[0])
                else:
                    unmatched_tasks.append(task)

        return matched_tasks, unmatched_tasks

    def query_llm(self, prompt):
        print("HOLA ENTRAMOS")

        # Configura tu clave de API de OpenAI desde variables de entorno

        client = openai.OpenAI()
        # Función de reintento con backoff exponencial
        @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(5))
        def completion_with_backoff(**kwargs):
            return client.beta.chat.completions.parse(**kwargs)

        # Definimos los mensajes en formato de chat
        messages = [
            {"role": "user", "content": prompt}
        ]

        response = completion_with_backoff(
            model="gpt-4o-mini",  # Asegúrate de que el modelo está disponible
            messages=messages,
            temperature=0,
            max_tokens=256,
            top_p=1,
            response_format=Plan,
            frequency_penalty=0,
            presence_penalty=0
        )

        return response.choices[0].message.content.strip()

if __name__ == "__main__":
    openai.api_key = os.getenv("OPENAI_API_KEY")
    # Rutas a los archivos
    prompt_dir = 'prompts/'
    goals_json_path = 'eval_scenarios/goals.json'  # Asegúrate de que este archivo existe y tiene la estructura correcta
    human_plans_csv = 'eval_scenarios/listen_plans.csv'  # CSV con columnas: num_plan, plan, goals, plan_goals_GT

    # Inicializamos el razonador con la ruta de los prompts y el JSON de objetivos
    reasoner = LLMListenPlanReasoner(prompt_dir=prompt_dir, goals_json_path=goals_json_path)

    # Cargamos el CSV con los textos del humano
    plans_df = pd.read_csv(human_plans_csv)  # Asegúrate de que las columnas son: num_plan, plan, goals, plan_goals_GT

    # Procesamos los textos
    results_df = reasoner.process_human_texts(plans_df)

    # Guardamos los resultados en un nuevo CSV
    results_df.to_csv('tareas_procesadas_format.csv', index=False)

    print("Procesamiento completado. Resultados guardados en 'tareas_procesadas.csv'.")

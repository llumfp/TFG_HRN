import requests
import time

# URLs del servicio de planificación
SOLVER_URL = "https://solver.planning.domains/solve"
CHECK_URL = "https://solver.planning.domains/check/{}"

# Cargar los archivos de dominio y problema PDDL
def load_pddl_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

# Función para enviar los archivos de dominio y problema a la API
def solve_pddl(domain_pddl, problem_pddl):
    # Estructura de datos para la petición
    data = {
        'domain': domain_pddl,
        'problem': problem_pddl
    }
    
    # Realizar la petición POST a la API
    response = requests.post(SOLVER_URL, json=data)
    
    # Verificar que la respuesta sea exitosa
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error: {response.status_code}, {response.text}")

# Función para revisar el resultado del plan
def check_plan(result_id):
    check_url = CHECK_URL.format(result_id)
    response = requests.get(check_url)
    
    # Verificar que la respuesta sea exitosa
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error al obtener el plan: {response.status_code}, {response.text}")

# Ruta a los archivos PDDL
domain_file_path = "domain.pddl"
problem_file_path = "problem.pddl"

# Cargar el contenido de los archivos PDDL
domain_pddl = load_pddl_file(domain_file_path)
problem_pddl = load_pddl_file(problem_file_path)

# Resolver el problema PDDL
try:
    result = solve_pddl(domain_pddl, problem_pddl)
    
    if 'result' in result:
        # Obtener el identificador del plan
        result_id = result['result'].split('/')[2]  # Extraer el ID del resultado de la URL
        
        # Revisar el estado del plan
        time.sleep(2)  # Esperar unos segundos antes de consultar el resultado
        plan_result = check_plan(result_id)
        
        # Mostrar el plan encontrado
        if 'result' in plan_result and 'plan' in plan_result['result']:
            print("Plan encontrado:")
            for action in plan_result['result']['plan']:
                print(f"{action['start']}: {action['name']} [{action['duration']}]")
        else:
            print("No se encontró un plan.")
    else:
        print("No se obtuvo un identificador de resultado.")
except Exception as e:
    print(e)

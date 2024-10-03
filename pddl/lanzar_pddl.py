import requests

# URLs del servicio de planificación
SOLVER_URL = "http://api.planning.domains"

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

# Ruta a los archivos PDDL
domain_file_path = "domain.pddl"
problem_file_path = "problem.pddl"

# Cargar el contenido de los archivos PDDL
domain_pddl = load_pddl_file(domain_file_path)
problem_pddl = load_pddl_file(problem_file_path)

# Resolver el problema PDDL
# try:
result = solve_pddl(domain_pddl, problem_pddl)
print(result)
# Mostrar el plan encontrado
if 'result' in result and 'plan' in result['result']:
    print("Plan encontrado:")
    for action in result['result']['plan']:
        print(f"{action['start']}: {action['name']} [{action['duration']}]")
else:
    print("No se encontró un plan.")
# except Exception as e:
#     print(e)

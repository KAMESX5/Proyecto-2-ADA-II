#kevin Alejandro Marulanda Escobar - 2380697-3743
import os
from minizinc import Instance, Model, Solver

class DataClassifier:
    """Clase para clasificar y almacenar los datos del archivo de texto o dzn."""

    def __init__(self):
        # Variables individuales
        self.num_positions = 0
        self.matrix_size = 0
        self.num_new_programs = 0

        # Arreglos para los datos matriciales
        self.coordinates = []
        self.population_matrix = []
        self.business_matrix = []

    def classify_data_txt(self, content):
        """
        Clasifica los datos de un archivo de texto según el formato especificado.
        :param content: Listado de líneas del archivo.
        """
        try:
            content = [line.strip() for line in content if line.strip()]  # Limpia líneas vacías
            self.num_positions = int(content[0])

            # Coordenadas de localizaciones existentes
            self.coordinates = [list(map(int, content[i + 1].split())) for i in range(self.num_positions)]

            # Tamaño de la matriz
            matrix_size_line_index = 1 + self.num_positions
            self.matrix_size = int(content[matrix_size_line_index])

            # Matriz de segmento de población
            n = self.matrix_size
            population_matrix_start = matrix_size_line_index + 1
            population_matrix_end = population_matrix_start + n
            self.population_matrix = [list(map(int, content[i].split())) for i in range(population_matrix_start, population_matrix_end)]

            # Matriz de entorno empresarial
            business_matrix_start = population_matrix_end
            business_matrix_end = business_matrix_start + n
            self.business_matrix = [list(map(int, content[i].split())) for i in range(business_matrix_start, business_matrix_end)]

            # Número de programas nuevos
            self.num_new_programs = int(content[business_matrix_end])

        except (IndexError, ValueError) as e:
            raise ValueError(f"Error procesando el archivo de texto: {e}")

    def classify_data_dzn(self, content):
        """
        Clasifica los datos de un archivo DZN según el formato MiniZinc.
        :param content: Listado de líneas del archivo.
        """
        try:
            data = "".join(content)

            def extract_array(name):
                import re
                pattern = f"{name}\s*=\s*array2d\(.*?,\s*\[(.*?)\]\);"
                match = re.search(pattern, data, re.DOTALL)
                if not match:
                    raise ValueError(f"{name} no encontrado")
                array_data = match.group(1).replace("\n", "").split(",")
                return [int(val.strip()) for val in array_data]

            self.matrix_size = int(data.split("n = ")[1].split(";")[0].strip())
            self.num_positions = int(data.split("num_existing_positions = ")[1].split(";")[0].strip())

            coord_data = data.split("existing_positions = [| ")[1].split(" |]")[0].strip()
            self.coordinates = [list(map(int, pair.split(","))) for pair in coord_data.split("|")]

            population_flat = extract_array("population_segment")
            self.population_matrix = [population_flat[i:i + self.matrix_size] for i in range(0, len(population_flat), self.matrix_size)]

            business_flat = extract_array("business_environment")
            self.business_matrix = [business_flat[i:i + self.matrix_size] for i in range(0, len(business_flat), self.matrix_size)]

            self.num_new_programs = int(data.split("num_new_programs = ")[1].split(";")[0].strip())

        except Exception as e:
            raise ValueError(f"Error procesando el archivo DZN: {e}")

    def format_for_minizinc(self):
        """Formatea los datos clasificados para que se ajusten a la entrada esperada en MiniZinc."""
        formatted_data = []
        n = self.matrix_size

        # Tamaño de la matriz
        formatted_data.append(f"n = {n};")
        # Número de posiciones existentes
        formatted_data.append(f"num_existing_positions = {self.num_positions};")
        # Coordenadas en formato MiniZinc
        formatted_coords = " | ".join([f"{x}, {y}" for x, y in self.coordinates])
        formatted_data.append(f"existing_positions = [| {formatted_coords} |];")
        # Número de nuevos programas
        formatted_data.append(f"num_new_programs = {self.num_new_programs};")
        # Matriz de segmento de población
        flat_population = [str(item) for row in self.population_matrix for item in row]
        formatted_data.append(f"population_segment = array2d(0..{n-1}, 0..{n-1}, [{', '.join(flat_population)}]);")
        # Matriz de entorno empresarial
        flat_business = [str(item) for row in self.business_matrix for item in row]
        formatted_data.append(f"business_environment = array2d(0..{n-1}, 0..{n-1}, [{', '.join(flat_business)}]);")

        return "\n".join(formatted_data)

    def execute_minizinc_model(self, model_path):
        """Ejecuta el modelo MiniZinc usando los datos formateados."""
        try:
            # Cargar el solver
            solver = Solver.lookup("gecode")  # Asegúrate de que Gecode esté instalado

            # Formatear los datos para MiniZinc
            input_data = self.format_for_minizinc()
            input_file = os.path.abspath("input_data.dzn")
            model_path = os.path.abspath(model_path)

            # Escribir los datos en un archivo temporal
            with open(input_file, "w") as file:
                file.write(input_data)

            # Cargar el modelo 
            model = Model(model_path)

            # Crear una instancia del modelo
            instance = Instance(solver, model)

            # Proporcionar datos a la instancia
            instance["n"] = self.matrix_size
            instance["num_existing_positions"] = self.num_positions
            instance["existing_positions"] = self.coordinates
            instance["num_new_programs"] = self.num_new_programs
            instance["population_segment"] = self.population_matrix
            instance["business_environment"] = self.business_matrix

            # Imprimir los datos de entrada formateados
            print("Datos de entrada formateados para MiniZinc:")
            print(f"n: {self.matrix_size}")
            print(f"num_existing_positions: {self.num_positions}")
            print(f"existing_positions: {self.coordinates}")
            print(f"num_new_programs: {self.num_new_programs}")
            print(f"population_segment: {self.population_matrix}")
            print(f"business_environment: {self.business_matrix}")

            # Resolver el modelo
            result = instance.solve()

            # Mostrar resultados
            print("Resultados de la ejecución del modelo MiniZinc:")
            print(result)

            return result

        except Exception as e:
            # Captura la salida de error
            error_message = f"Error ejecutando MiniZinc: {str(e)}"
            self.log_error(error_message)
            raise RuntimeError(error_message)

    def log_error(self, message):
        """Registra un mensaje de error en la consola."""
        print(f"Error: {message}")
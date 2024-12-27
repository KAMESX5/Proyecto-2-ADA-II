  % kevin Alejandro Marulanda Escobar - 2380697-3743
  include "globals.mzn"; % Importa las restricciones globales
  
  % Parámetros de entrada
  int: n; % Tamaño de la matriz
  int: num_existing_positions; % Número de posiciones existentes
  array[1..num_existing_positions, 1..2] of int: existing_positions; % Coordenadas de las posiciones actuales
  int: num_new_programs; % Número de programas nuevos
  array[0..n-1, 0..n-1] of int: population_segment; % Matriz de segmento de población
  array[0..n-1, 0..n-1] of int: business_environment; % Matriz de entorno empresarial
  
  % Convertir las posiciones existentes al rango (0, n-1) con coordenadas invertidas
  array[0..num_existing_positions-1, 0..1] of int: adjusted_existing_positions =
      array2d(0..num_existing_positions-1, 0..1, [
          if j == 0 then existing_positions[i, 2] 
          else existing_positions[i, 1] 
          endif
          | i in 1..num_existing_positions, j in 0..1
      ]);
  
  % Cálculo de totales para posiciones existentes población existente y entorno empresarial existente
  int: total_existing_population = sum([ 
      sum([population_segment[x, y] |
          x in max(0, adjusted_existing_positions[e, 0] - 1)..min(n-1, adjusted_existing_positions[e, 0] + 1),
          y in max(0, adjusted_existing_positions[e, 1] - 1)..min(n-1, adjusted_existing_positions[e, 1] + 1)]) 
      | e in 0..num_existing_positions-1
  ]);
  
  int: total_existing_business = sum([ 
      sum([business_environment[x, y] |
          x in max(0, adjusted_existing_positions[e, 0] - 1)..min(n-1, adjusted_existing_positions[e, 0] + 1),
          y in max(0, adjusted_existing_positions[e, 1] - 1)..min(n-1, adjusted_existing_positions[e, 1] + 1)]) 
      | e in 0..num_existing_positions-1
  ]);
  
  % Restricciones
  int: min_population = 25; % Restricción mínima para el segmento de población
  int: min_business = 20; % Restricción mínima para el entorno empresarial
  
  % Variables de decisión
  array[0..num_new_programs-1, 0..1] of var 0..n-1: new_program_positions; % Coordenadas de los nuevos programas
  
  % Restricciones
  constraint
      % Los nuevos programas no pueden estar contiguos a las posiciones existentes
      forall(p in 0..num_new_programs-1) (
          forall(e in 0..num_existing_positions-1) (
              abs(new_program_positions[p, 0] - adjusted_existing_positions[e, 0]) >= 3 \/ 
              abs(new_program_positions[p, 1] - adjusted_existing_positions[e, 1]) >= 3
          )
      )
      /\ 
      % Los nuevos programas no pueden estar contiguos entre sí
      forall(p1, p2 in 0..num_new_programs-1 where p1 < p2) (
          abs(new_program_positions[p1, 0] - new_program_positions[p2, 0]) >= 3 \/
          abs(new_program_positions[p1, 1] - new_program_positions[p2, 1]) >= 3
      )
      /\ 
      % Cada nueva posición debe cumplir las condiciones de la matriz de población
      forall(p in 0..num_new_programs-1) (
          sum([population_segment[x, y] |
              x in max(0, new_program_positions[p, 0] - 1)..min(n-1, new_program_positions[p, 0] + 1),
              y in max(0, new_program_positions[p, 1] - 1)..min(n -1, new_program_positions[p, 1] + 1)]) >= min_population
      )
      /\ 
      % Cada nueva posición debe cumplir las condiciones de la matriz de entorno empresarial
      forall (p in 0..num_new_programs- 1) (
          sum([business_environment[x, y] |
              x in max(0, new_program_positions[p, 0] - 1)..min(n-1, new_program_positions[p, 0] + 1),
              y in max(0, new_program_positions[p, 1] - 1)..min(n-1, new_program_positions[p, 1] + 1)]) >= min_business
      );
  
  % Función para ordenar coordenadas
  array[0..num_new_programs-1, 0..1] of var 0..n-1: sorted_new_program_positions;
  
  % Ordenar las nuevas posiciones
  constraint
      forall(i in 0..num_new_programs-1) (
          sorted_new_program_positions[i, 0] = new_program_positions[i, 0] /\
          sorted_new_program_positions[i, 1] = new_program_positions[i, 1]
      )
      /\ 
      % Asegurarse de que las coordenadas estén ordenadas
      forall(i in 0..num_new_programs-2) (
          (sorted_new_program_positions[i, 0] < sorted_new_program_positions[i+1, 0]) \/
          (sorted_new_program_positions[i, 0] == sorted_new_program_positions[i+1, 0] /\
          sorted_new_program_positions[i, 1] <= sorted_new_program_positions[i+1, 1])
      );
  
  % Función objetivo: Maximizar la suma del segmento de población y entorno empresarial
  var int: total_population = sum([ 
      sum([population_segment[x, y] |
          x in max(0, sorted_new_program_positions[e, 1] - 1)..min(n-1, sorted_new_program_positions[e, 1] + 1),
          y in max(0, sorted_new_program_positions[e, 0] - 1)..min(n-1, sorted_new_program_positions[e, 0] + 1)]) 
      | e in 0..num_new_programs-1]);
  
  var int: total_business = sum([ 
      sum([business_environment[x, y] |
          x in max(0, sorted_new_program_positions[e, 1] - 1)..min(n-1, sorted_new_program_positions[e, 1] + 1),
          y in max(0, sorted_new_program_positions[e, 0] - 1)..min(n-1, sorted_new_program_positions[e, 0] + 1)]) 
      | e in 0..num_new_programs-1]);
  
  solve maximize total_population + total_business;
  
  % Salida: Mostrar los valores alrededor de las posiciones existentes
  output  ["\nGanancia Total: " ++ show(total_existing_population + total_existing_business)]
  ++ ["\nNueva Ganancia total: "++ show(total_existing_population + total_existing_business+total_population + total_business) ++ "\n"] 
  ++ [
      "(" ++ show(existing_positions[i, 1]) ++ ", " ++ show(existing_positions[i, 2]) ++ ")\n"
      | i in 1..num_existing_positions]
  ++ [
      "(" ++ show(sorted_new_program_positions[p, 0]) ++ ", " ++ show(sorted_new_program_positions[p, 1]) ++ ")\n"
      | p in 0..num_new_programs-1
  ];
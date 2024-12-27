#kevin Alejandro Marulanda Escobar - 2380697-3743
import tkinter as tk
from tkinter import filedialog, messagebox
from Punto1 import DataClassifier

def open_file_and_classify():
    """Abre un archivo de texto o .dzn, clasifica los datos y los muestra en el cuadro de texto."""
    file_path = filedialog.askopenfilename(
        title="Seleccionar archivo",
        filetypes=[("Archivos de texto y DZN", "*.txt;*.dzn"), ("Todos los archivos", "*.*")]
    )
    if file_path:
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.readlines()

            # Clasificar los datos utilizando la clase
            classifier = DataClassifier()
            if file_path.endswith(".txt"):
                classifier.classify_data_txt(content)
            elif file_path.endswith(".dzn"):
                classifier.classify_data_dzn(content)
            else:
                raise ValueError("Formato de archivo no soportado")

            # Ejecutar el modelo MiniZinc
            model_path = filedialog.askopenfilename(
                title="Seleccionar modelo MiniZinc",
                filetypes=[("Archivos MiniZinc", "*.mzn"), ("Todos los archivos", "*.*")]
            )
            if not model_path:
                raise ValueError("No se seleccionó un modelo MiniZinc")

            # Ejecutar el modelo MiniZinc
            result = classifier.execute_minizinc_model(model_path)

            # Mostrar los resultados en el cuadro de texto
            text_area.delete(1.0, tk.END)  # Limpiar el área de texto
            if result:  # Verificar que el resultado no sea None o vacío
                text_area.insert(tk.END, "Resultados del modelo:\n\n")
                text_area.insert(tk.END, result)
            else:
                text_area.insert(tk.END, "No se obtuvieron resultados.")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo procesar el archivo:\n{e}")

# Crear la ventana principal
root = tk.Tk()
root.title("MiniZinc Solver GUI")
root.resizable(width=True, height=True)  # permitir redimensionar la ventana
root.geometry("800x600")  # tamaño de la ventana
root.configure(bg="black")  # color Negro de fondo en la ventana

# Botón para abrir el archivo
open_button = tk.Button(
    root,
    text="Abrir Archivo",
    command=open_file_and_classify,
    bg="#3c3c3c",  # Fondo oscuro del botón
    fg="#ffffff",  # Texto blanco
    activebackground="#575757",  # Fondo al presionar
    activeforeground="#ffffff",  # Texto al presionar
    relief=tk.FLAT,
)
open_button.pack(pady=10)

# Cuadro de texto para mostrar el contenido
text_area = tk.Text(
    root,
    wrap=tk.WORD,
    font=("Consolas", 12),
    bg="#1e1e1e",  # Fondo oscuro del cuadro de texto
    fg="#d4d4d4",  # Texto gris claro
    insertbackground="#ffffff",  # Cursor blanco
    selectbackground="#575757",  # Selección gris
    selectforeground="#ffffff",  # Texto seleccionado blanco
)
text_area.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

# Barra de desplazamiento
scrollbar = tk.Scrollbar(text_area, bg="#1e1e1e", troughcolor="#3c3c3c", activebackground="#575757")
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
text_area.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=text_area.yview)

# Inicia el bucle principal
root.mainloop()

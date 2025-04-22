import tkinter as tk
from tkinter import ttk, scrolledtext
import re

class RegexGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Generador de Expresiones Regulares")
        self.root.geometry("600x700")
        
        # Variables para los filtros
        self.match_start = tk.BooleanVar()
        self.match_end = tk.BooleanVar()
        self.digits = tk.BooleanVar()
        self.letters = tk.BooleanVar()
        self.special_chars = tk.BooleanVar()
        self.custom_pattern = tk.StringVar()
        self.min_length = tk.StringVar(value="0")
        self.max_length = tk.StringVar(value="")
        self.selected_preset = tk.StringVar()
        
        # Patrones predefinidos
        self.presets = {
            "Ninguno": {
                "match_start": False,
                "match_end": False,
                "digits": False,
                "letters": False,
                "special_chars": False,
                "custom_pattern": "",
                "min_length": "0",
                "max_length": ""
            },
            "Correo electrónico": {
                "match_start": True,
                "match_end": True,
                "digits": True,
                "letters": True,
                "special_chars": True,
                "custom_pattern": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
                "min_length": "5",
                "max_length": "254"
            },
            "URL": {
                "match_start": True,
                "match_end": True,
                "digits": True,
                "letters": True,
                "special_chars": True,
                "custom_pattern": r"https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[\w-]*)*",
                "min_length": "10",
                "max_length": ""
            },
            "Número de teléfono": {
                "match_start": True,
                "match_end": True,
                "digits": True,
                "letters": False,
                "special_chars": True,
                "custom_pattern": r"\d{3}[-.\s]?\d{3}[-.\s]?\d{4}",
                "min_length": "10",
                "max_length": "12"
            },
            "Fecha (DD/MM/YYYY)": {
                "match_start": True,
                "match_end": True,
                "digits": True,
                "letters": False,
                "special_chars": True,
                "custom_pattern": r"\d{2}/\d{2}/\d{4}",
                "min_length": "10",
                "max_length": "10"
            }
        }
        
        # Interfaz
        self.create_widgets()
        
        # Actualizar regex inicial
        self.update_regex()
    
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Título
        ttk.Label(main_frame, text="Generador de Expresiones Regulares", font=("Helvetica", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        
        # Lista desplegable para patrones predefinidos
        ttk.Label(main_frame, text="Seleccionar patrón predefinido:").grid(row=1, column=0, sticky=tk.W, pady=5)
        preset_combobox = ttk.Combobox(main_frame, textvariable=self.selected_preset, values=list(self.presets.keys()), state="readonly")
        preset_combobox.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        preset_combobox.set("Ninguno")
        preset_combobox.bind("<<ComboboxSelected>>", self.load_preset)
        
        # Checkboxes para opciones comunes
        ttk.Checkbutton(main_frame, text="Iniciar con (^)", variable=self.match_start, command=self.update_regex).grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Checkbutton(main_frame, text="Terminar con ($)", variable=self.match_end, command=self.update_regex).grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Checkbutton(main_frame, text="Dígitos (0-9)", variable=self.digits, command=self.update_regex).grid(row=4, column=0, sticky=tk.W, pady=5)
        ttk.Checkbutton(main_frame, text="Letras (a-z, A-Z)", variable=self.letters, command=self.update_regex).grid(row=5, column=0, sticky=tk.W, pady=5)
        ttk.Checkbutton(main_frame, text="Caracteres especiales", variable=self.special_chars, command=self.update_regex).grid(row=6, column=0, sticky=tk.W, pady=5)
        
        # Entrada para patrón personalizado
        ttk.Label(main_frame, text="Patrón personalizado:").grid(row=7, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.custom_pattern).grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        self.custom_pattern.trace("w", self.update_regex)
        
        # Entradas para longitud
        ttk.Label(main_frame, text="Longitud mínima:").grid(row=9, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.min_length, width=10).grid(row=9, column=1, sticky=tk.W, pady=5)
        self.min_length.trace("w", self.update_regex)
        
        ttk.Label(main_frame, text="Longitud máxima:").grid(row=10, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.max_length, width=10).grid(row=10, column=1, sticky=tk.W, pady=5)
        self.max_length.trace("w", self.update_regex)
        
        # Área de visualización del regex
        ttk.Label(main_frame, text="Expresión Regular Generada:").grid(row=11, column=0, sticky=tk.W, pady=10)
        self.regex_display = scrolledtext.ScrolledText(main_frame, height=4, width=50, wrap=tk.WORD)
        self.regex_display.grid(row=12, column=0, columnspan=2, pady=5)
        self.regex_display.config(state='disabled')
        
        # Botón para copiar
        ttk.Button(main_frame, text="Copiar al Portapapeles", command=self.copy_to_clipboard).grid(row=13, column=0, columnspan=2, pady=10)
    
    def load_preset(self, event=None):
        preset_name = self.selected_preset.get()
        preset = self.presets[preset_name]
        
        # Actualizar variables con los valores del patrón predefinido
        self.match_start.set(preset["match_start"])
        self.match_end.set(preset["match_end"])
        self.digits.set(preset["digits"])
        self.letters.set(preset["letters"])
        self.special_chars.set(preset["special_chars"])
        self.custom_pattern.set(preset["custom_pattern"])
        self.min_length.set(preset["min_length"])
        self.max_length.set(preset["max_length"])
        
        # Actualizar la regex
        self.update_regex()
    
    def update_regex(self, *args):
        regex_parts = []
        
        # Si hay un patrón personalizado, usarlo directamente
        if self.custom_pattern.get():
            regex = self.custom_pattern.get()
        else:
            # Construir el conjunto de caracteres
            char_set = []
            if self.digits.get():
                char_set.append(r"\d")
            if self.letters.get():
                char_set.append(r"[a-zA-Z]")
            if self.special_chars.get():
                char_set.append(r"[!@#$%^&*()_+\-=\[\]{};:'\",.<>?]")
            
            # Combinar el conjunto de caracteres
            if char_set:
                regex_parts.append(f"[{''.join(char_set)}]")
            else:
                regex_parts.append(r".")  # Cualquier carácter si no se selecciona nada
            
            # Añadir restricciones de longitud
            min_len = self.min_length.get()
            max_len = self.max_length.get()
            
            if min_len.isdigit() and int(min_len) > 0:
                if max_len.isdigit() and int(max_len) >= int(min_len):
                    regex_parts.append(f"{{{min_len},{max_len}}}")
                else:
                    regex_parts.append(f"{{{min_len},}}")
            elif max_len.isdigit() and int(max_len) > 0:
                regex_parts.append(f"{{0,{max_len}}}")
            
            # Combinar todas las partes
            regex = "".join(regex_parts)
        
        # Añadir inicio y fin si están seleccionados
        if self.match_start.get():
            regex = f"^{regex}"
        if self.match_end.get():
            regex = f"{regex}$"
        
        # Actualizar display
        self.regex_display.config(state='normal')
        self.regex_display.delete(1.0, tk.END)
        self.regex_display.insert(tk.END, regex)
        self.regex_display.config(state='disabled')
        
        self.current_regex = regex
    
    def copy_to_clipboard(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.current_regex)
        self.root.update()  # Necesario para que el portapapeles se actualice

if __name__ == "__main__":
    root = tk.Tk()
    app = RegexGeneratorApp(root)
    root.mainloop()
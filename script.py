import pandas as pd
import tkinter as tk
from tkinter import messagebox
import threading
import time

# === CARGAR PREGUNTAS ===
df = pd.read_excel("preguntas.xlsx")
df.columns = df.columns.str.strip()
preguntas = df.sample(60).reset_index(drop=True)

# === VARIABLES DE ESTADO ===
respuestas_usuario = [''] * 60
pregunta_actual = 0
tiempo_restante = 60 * 60  # 1 hora en segundos

# === INTERFAZ ===
root = tk.Tk()
root.title("Examen Simulado")
root.geometry("700x450")

pregunta_var = tk.StringVar()
opcion_var = tk.StringVar()

label_timer = tk.Label(root, text="⏳ Tiempo restante: 60:00", font=("Arial", 12, "bold"), fg="red")
label_timer.pack(pady=5)

label_pregunta = tk.Label(root, text="", wraplength=650, justify="left", font=("Arial", 12))
label_pregunta.pack(pady=10)

radio_buttons = []
for opcion in ["A", "B", "C", "D"]:
    rb = tk.Radiobutton(root, text="", variable=opcion_var, value=opcion, font=("Arial", 11))
    rb.pack(anchor="w")
    radio_buttons.append(rb)

def mostrar_pregunta(index):
    pregunta = preguntas.iloc[index]
    pregunta_var.set(f"{index + 1}. {pregunta['Pregunta']}")
    label_pregunta.config(text=pregunta_var.get())

    opciones = [pregunta['Opción A'], pregunta['Opción B'], pregunta['Opción C'], pregunta['Opción D']]
    for i, texto in enumerate(opciones):
        radio_buttons[i].config(text=f"{chr(65+i)}. {texto}")
    opcion_var.set(respuestas_usuario[index])

def siguiente():
    global pregunta_actual
    if opcion_var.get() not in ['A', 'B', 'C', 'D']:
        messagebox.showwarning("Advertencia", "Debes seleccionar una opción (A, B, C o D).")
        return
    respuestas_usuario[pregunta_actual] = opcion_var.get()
    if pregunta_actual < 59:
        pregunta_actual += 1
        mostrar_pregunta(pregunta_actual)
    else:
        terminar_examen()

def anterior():
    global pregunta_actual
    if pregunta_actual > 0:
        respuestas_usuario[pregunta_actual] = opcion_var.get()
        pregunta_actual -= 1
        mostrar_pregunta(pregunta_actual)

def terminar_examen():
    correctas = 0
    errores = []
    for i, row in preguntas.iterrows():
        correcta = row['Respuesta Correcta'].strip().upper()
        usuario = respuestas_usuario[i]
        if usuario == correcta:
            correctas += 1
        else:
            errores.append((i+1, usuario, correcta, row['Pregunta']))
    
    nota = round((correctas / 60) * 20, 2)
    resumen = f"✔️ Correctas: {correctas}\n❌ Incorrectas: {60 - correctas}\n📈 Nota: {nota}/20"

    if errores:
        resumen += "\n\n🔎 Preguntas incorrectas:\n"
        for num, tu, corr, texto in errores:
            resumen += f"{num}. Tu respuesta: {tu} | Correcta: {corr}\n   {texto[:70]}...\n"

    messagebox.showinfo("Resultados", resumen)
    root.quit()

# === TEMPORIZADOR ===
def actualizar_timer():
    global tiempo_restante
    mins, secs = divmod(tiempo_restante, 60)
    label_timer.config(text=f"⏳ Tiempo restante: {mins:02}:{secs:02}")
    if tiempo_restante > 0:
        tiempo_restante -= 1
        root.after(1000, actualizar_timer)
    else:
        messagebox.showinfo("⏰ Tiempo agotado", "Se acabó el tiempo. El examen se enviará automáticamente.")
        terminar_examen()

# === BOTONES DE NAVEGACIÓN ===
frame_botones = tk.Frame(root)
frame_botones.pack(pady=20)

btn_anterior = tk.Button(frame_botones, text="⏪ Anterior", command=anterior)
btn_anterior.grid(row=0, column=0, padx=10)

btn_siguiente = tk.Button(frame_botones, text="Siguiente ⏩", command=siguiente)
btn_siguiente.grid(row=0, column=1, padx=10)

# === INICIO DE LA INTERFAZ ===
mostrar_pregunta(pregunta_actual)
actualizar_timer()
root.mainloop()

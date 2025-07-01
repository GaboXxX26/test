import pandas as pd
import tkinter as tk
from tkinter import messagebox
import random

# === CARGAR PREGUNTAS Y MEZCLAR RESPUESTAS ===
df = pd.read_excel("preguntas.xlsx")
df.columns = df.columns.str.strip()
preguntas_originales = df.sample(60).reset_index(drop=True)

# Preparar estructura con preguntas y respuestas mezcladas
preguntas = []
for _, row in preguntas_originales.iterrows():
    opciones = [
        ("A", row['Opción A']),
        ("B", row['Opción B']),
        ("C", row['Opción C']),
        ("D", row['Opción D']),
    ]
    random.shuffle(opciones)  # Mezclar opciones
    correcta = row['Respuesta Correcta'].strip().upper()
    texto_correcto = row[f'Opción {correcta}']
    nueva_correcta = next(i for i, (_, texto) in enumerate(opciones) if texto == texto_correcto)
    preguntas.append({
        "pregunta": row['Pregunta'],
        "opciones": [texto for _, texto in opciones],
        "correcta_idx": nueva_correcta
    })

# === VARIABLES DE ESTADO ===
respuestas_usuario = [''] * 60
pregunta_actual = 0
tiempo_restante = 60 * 60  # 1 hora

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
for i in range(4):
    rb = tk.Radiobutton(root, text="", variable=opcion_var, value=str(i), font=("Arial", 11))
    rb.pack(anchor="w")
    radio_buttons.append(rb)

def mostrar_pregunta(index):
    pregunta = preguntas[index]
    label_pregunta.config(text=f"{index + 1}. {pregunta['pregunta']}")
    for i, texto in enumerate(pregunta['opciones']):
        radio_buttons[i].config(text=f"{chr(65 + i)}. {texto}")
    opcion_var.set(respuestas_usuario[index])

def siguiente():
    global pregunta_actual
    if opcion_var.get() not in ['0', '1', '2', '3']:
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
    for i, pregunta in enumerate(preguntas):
        seleccion = respuestas_usuario[i]
        if seleccion == '':
            seleccion = '-'
        correcta_idx = pregunta['correcta_idx']
        if str(seleccion) == str(correcta_idx):
            correctas += 1
        else:
            errores.append((
                i+1,
                chr(65 + int(seleccion)) if seleccion != '-' else "-",
                chr(65 + correcta_idx),
                pregunta['pregunta']
            ))

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

# === BOTONES ===
frame_botones = tk.Frame(root)
frame_botones.pack(pady=20)

btn_anterior = tk.Button(frame_botones, text="⏪ Anterior", command=anterior)
btn_anterior.grid(row=0, column=0, padx=10)

btn_siguiente = tk.Button(frame_botones, text="Siguiente ⏩", command=siguiente)
btn_siguiente.grid(row=0, column=1, padx=10)

# === INICIAR ===
mostrar_pregunta(pregunta_actual)
actualizar_timer()
root.mainloop()

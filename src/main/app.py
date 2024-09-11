########################################
#######        ### - ###         #######
######        Main screen         ######
#######        ### - ###         #######
########################################

from datetime import date, datetime, timedelta
from PIL import Image, ImageTk
from tkinter import ttk
import tkinter as tk
import pandas as pd
import sys
import os




sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dao import database as db

current_date = date.today().__format__("%d/%m/%Y")
current_time = datetime.now().strftime("%H:%M:%S")
current_competence = date.today().__format__("%m/%Y")

def remove_widgets():
    global png_logo, lbl_logo, lbl_logo, btn_return
    main_widgets = [png_logo, lbl_logo, lbl_logo, btn_return]

    for widget in root.winfo_children():
        if widget not in main_widgets:
            widget.destroy()


def validate_float_input(P):
    if P == "":
        return True
    try:
        float(P.replace(',', '.'))
        if ',' in P and len(P.split(',')[1]) > 2:
            return False
        return True
    except ValueError:
        return False


def validate_reference_input(P):
    if len(P) > 7:
        return False
    if len(P) == 3 and P[-1] != '/':
        return False
    if (not P[:2].isdigit() or (len(P) > 3 and not P[3:].isdigit())) and str(P) != '':
        return False
    return True


def validate_date_input(P):
    if len(P) > 10:
        return False
    if len(P) in [3, 6] and P[-1] != '/':
        return False
    if len(P) != 3 and len(P) != 6 and len(P) < 10 and not P[-1].isdigit():
        return False
    return True


def validate_description(event):
    global text_description
    text = text_description.get("1.0", "end-1c")
    if len(text) > 400:
        text_description.delete("1.0", "end-1c")
        text_description.insert("1.0", text[:400])


def execute_insert_mov_fin():
    global entry_competence, entry_date_trans, drop_mov_type, entry_date_launch, entry_time_launch, drop_cat_type, text_description, entry_value_trans, entry_dicount_trans, drop_participants

    competence = entry_competence.get()
    trans_date = entry_date_trans.get()
    launch_date = entry_date_launch.get()
    launch_time = entry_time_launch.get()
    movement = str(drop_mov_type.get()).split(' - ')[0]
    category = str(drop_cat_type.get()).split(' - ')[0]
    participant = str(drop_participants.get()).split(' - ')[0]
    description = text_description.get("1.0", "end-1c")
    value_trans = float(str(entry_value_trans.get()).replace(',','.')) if entry_value_trans.get() not in ['', None] else 0
    value_discount = float(str(entry_dicount_trans.get()).replace(',','.')) if entry_dicount_trans.get() not in ['', None] else 0
    launch_date = f'{launch_date.split("/")[2]}-{launch_date.split("/")[1]}-{launch_date.split("/")[0]}'

    if len(competence) not in [6,7] or '/' not in competence or (len(competence) == 6 and len(competence.split("/")[0] == 2)): # error, reference incomplete, slash not in reference, year is not complete
        print("Ajuste a competência e tente novamente")
        return False
    else:
        competence = f"{(int(competence.split('/')[1])*100)+int(competence.split('/')[0])}"

    if trans_date.count("/") != 2 or len(trans_date) != 10 or trans_date == '':
        print("Ajuste a data da transação e tente novamente!")
        return False
    else:
        date_trans = f'{trans_date.split("/")[2]}-{trans_date.split("/")[1]}-{trans_date.split("/")[0]}'

    if category == '0':
        print("Categoria invalida")
        return False
    if str(value_trans) == '0':
        print("Valor invalida")
        return False



    return_insert = db.launch_financial_movement(
        bdreflan=competence,
        bddatatrans=date_trans,
        bddatalan=launch_date,
        bdhoralan=launch_time,
        bdcodcat=category,
        bddescmov=description,
        bdvlr=value_trans,
        bdvlrdesc=value_discount,
        bdcodter=participant,
        bdcodmov=movement
    )
    if return_insert:
        print("Lançamento realizado")
    else:
        print("Lançamento recusado")


def place_table(data, column_names, column_widths, place_x, place_y):
    columns = tuple(column_names)
    tree = ttk.Treeview(root, columns=columns, show='headings', height=10)

    for i,col in enumerate(columns):
        tree.heading(col, text=col)
        tree.column(col, anchor='center', width=column_widths[i])  # Define a largura de cada coluna

    sum_output_value = 0
    sum_input_value = 0

    for line in data:
        if 'saida' in str(line[4]).lower():
            sum_output_value += line[5]
        elif 'entrada' in str(line[4]).lower():
            sum_input_value += line[5]
        
        tree.insert('', tk.END, values=line)

    scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscroll=scrollbar.set)

    width_value = 0
    for i in column_widths:
        width_value += int(i) 
    tree.place(x=place_x, y=place_y, width=width_value, height=200)  
    scrollbar.place(x=int(width_value+place_x-1), y=place_y, height=200)

    lbl_sum_input = tk.Label(root, text=f'Total entradas: {"{:.2f}".format(sum_input_value)}', font=("Helvetica",11), bg="white")
    lbl_sum_output = tk.Label(root, text=f'Total saídas: {"{:.2f}".format(sum_output_value)}', font=("Helvetica",11), bg="white")
    lbl_total = tk.Label(root, text=f'Total: {"{:.2f}".format(sum_input_value-sum_output_value)}', font=("Helvetica",11), bg="white")

    lbl_sum_input.place(x=place_x ,y=place_y+200)
    lbl_sum_output.place(x=place_x+180 ,y=place_y+200)
    lbl_total.place(x=place_x+500 ,y=place_y+200)


def execute_query_mov_fin():
    global entry_competence_start, entry_competence_end, drop_cat_type, drop_participants, drop_mov_type

    competence_start = entry_competence_start.get()
    competence_end = entry_competence_end.get()
    cat_type = drop_cat_type.get().split(" - ")[0]
    participant = drop_participants.get().split(" - ")[0]
    mov_type = drop_mov_type.get()


    if len(competence_start) not in [6,7] or '/' not in competence_start or (len(competence_start) == 6 and len(competence_start.split("/")[0] == 2)): # error, reference incomplete, slash not in reference, year is not complete
        print("Ajuste a competência inicial e tente novamente")
        return False
    else:
        competence_start = f"{(int(competence_start.split('/')[1])*100)+int(competence_start.split('/')[0])}"
    
    if len(competence_end) not in [6,7] or '/' not in competence_end or (len(competence_end) == 6 and len(competence_end.split("/")[0] == 2)): # error, reference incomplete, slash not in reference, year is not complete
        print("Ajuste a competência final e tente novamente")
        return False
    else:
        competence_end = f"{(int(competence_end.split('/')[1])*100)+int(competence_end.split('/')[0])}"

    return_insert = db.get_financial_movements(
        bdreflan_start=competence_start,
        bdreflan_end=competence_end,
        bdcodter=participant,
        bdcodcat=cat_type,
        bdcodmovimentacao=mov_type,
    )
    if return_insert:
        print(return_insert)
        place_table(return_insert,['Código', 'Data', 'Categoria', 'Participante', 'Movimentação', 'Valor'],[60,70,150,170,90,100],35,340)
    else:
        print("Consulta recusada")


def layout_launch_finance():
    """
    Set layout to launch finance movements
    """
    global root, text_description, entry_competence, entry_date_trans, drop_mov_type, entry_date_launch, entry_time_launch, drop_cat_type, text_description, entry_value_trans, entry_dicount_trans, drop_participants

    remove_widgets()

    movement_types = db.get_movement_types()
    category_types = db.get_categories()
    participants = db.get_participants()
    category_types.insert(0, '0 - Selecione uma categoria')


    lbl_title = tk.Label(root, text="Lançamento de movimentações financeiras", font=("Helvetica", 15), bg="white")

    lbl_competence = tk.Label(root, text="Referência", font=("Helvetica",9), bg="white")
    entry_competence = tk.Entry(root, width=7, bg="#FAF3E0", validate="key", validatecommand=(root.register(validate_reference_input), '%P'))

    lbl_date_trans = tk.Label(root, text="Data", font=("Helvetica",9), bg="white")
    entry_date_trans = tk.Entry(root, width=10, bg="#FAF3E0", validate="key", validatecommand=(root.register(validate_date_input), '%P'))

    lbl_date_launch = tk.Label(root, text="Lançamento", font=("Helvetica",9), bg="white")
    entry_date_launch = tk.Entry(root, width=10, bg="#FAF3E0")

    lbl_time_launch = tk.Label(root, text="Hora", font=("Helvetica",9), bg="white")
    entry_time_launch = tk.Entry(root, width=8, bg="#FAF3E0")

    lbl_mov_type = tk.Label(root, text="Movimento", font=("Helvetica",9), bg="white")
    drop_mov_type = ttk.Combobox(root, values=movement_types, width=12, state='readonly')

    lbl_cat_type = tk.Label(root, text="Categoria", font=("Helvetica",9), bg="white")
    drop_cat_type = ttk.Combobox(root, values=category_types, width=35, state='readonly')

    lbl_value_trans = tk.Label(root, text="Valor", font=("Helvetica",9), bg="white")
    entry_value_trans = tk.Entry(root, width=17, bg="#FAF3E0", validate="key", validatecommand=(root.register(validate_float_input), '%P'))

    lbl_dicount_trans = tk.Label(root, text="Desconto", font=("Helvetica",9), bg="white")
    entry_dicount_trans = tk.Entry(root, width=17, bg="#FAF3E0", validate="key", validatecommand=(root.register(validate_float_input), '%P'))

    lbl_participants = tk.Label(root, text="Participante", font=("Helvetica",9), bg="white")
    drop_participants = ttk.Combobox(root, values=participants, width=35, state='readonly')
  
    lbl_description = tk.Label(root, text="Descrição da movimentação", font=("Helvetica",9), bg="white")
    text_description = tk.Text(root, width=77, height=6, wrap=tk.WORD, bg="#FAF3E0")

    btn_launch_data = tk.Button(root, text="Lançar movimentação",font=("Helvetica",9), bg="#E8F5E9", width=25, height=2, command=execute_insert_mov_fin)
    btn_query_data = tk.Button(root, text="Consultar movimentações",font=("Helvetica",9), bg="#E3F2FD", width=25, height=2, command=layout_query_finance)
   
   
   
   
   
   
   
   
    lbl_title.place(x=175, y=80)

    lbl_competence.place(x=50, y=130)
    entry_competence.place(x=120, y=132)
    entry_competence.insert(0, current_competence)

    lbl_date_trans.place(x=170, y=130)
    entry_date_trans.place(x=205, y=132)

    lbl_mov_type.place(x=275,y=130)
    drop_mov_type.current(0)
    drop_mov_type.place(x=340,y=130)

    lbl_date_launch.place(x=440, y=130)
    entry_date_launch.place(x=520, y=132)
    entry_date_launch.insert(0, current_date)
    entry_date_launch.config(state="readonly")

    lbl_time_launch.place(x=586, y=130)
    entry_time_launch.place(x=620, y=132)
    entry_time_launch.insert(0, current_time)
    entry_time_launch.config(state="readonly")

    lbl_cat_type.place(x=50, y=160)
    drop_cat_type.place(x=115, y=162)
    drop_cat_type.current(0)

    lbl_value_trans.place(x=400, y=160)
    entry_value_trans.place(x=437, y=162)

    lbl_dicount_trans.place(x=400, y=190)
    entry_dicount_trans.place(x=460, y=192)


    lbl_participants.place(x=50 ,y=190)
    drop_participants.current(0) 
    drop_participants.place(x=130 ,y=192)

    lbl_description.place(x=290,y=225)
    text_description.place(x=50,y=250)
    text_description.bind("<KeyRelease>", validate_description)

    btn_launch_data.place(x=125, y=370)
    btn_query_data.place(x=400, y=370)


def layout_query_finance():
    """
    Set layout to query finance movements
    """
    global entry_competence_start, entry_competence_end, drop_cat_type, drop_participants, drop_mov_type

    remove_widgets()

    movement_types = db.get_movement_types()
    category_types = db.get_categories()
    participants = db.get_participants()
    category_types.insert(0, '0 - Todas as categorias')
    participants.insert(0, '0 - Todos os participantes')
    movement_types.insert(0, 'Todos')

    lbl_title = tk.Label(root, text="Consulta de movimentações financeiras", font=("Helvetica", 15), bg="white")

    lbl_competence_start = tk.Label(root, text="Referência inicial", font=("Helvetica",9), bg="white")
    entry_competence_start = tk.Entry(root, width=7, bg="#FAF3E0", validate="key", validatecommand=(root.register(validate_reference_input), '%P'))
   
    lbl_competence_end = tk.Label(root, text="Referência final", font=("Helvetica",9), bg="white")
    entry_competence_end = tk.Entry(root, width=7, bg="#FAF3E0", validate="key", validatecommand=(root.register(validate_reference_input), '%P'))

    lbl_mov_type = tk.Label(root, text="Movimento", font=("Helvetica",9), bg="white")
    drop_mov_type = ttk.Combobox(root, values=movement_types, width=12, state='readonly')
   
    lbl_cat_type = tk.Label(root, text="Categoria", font=("Helvetica",9), bg="white")
    drop_cat_type = ttk.Combobox(root, values=category_types, width=35, state='readonly')
   
    lbl_participants = tk.Label(root, text="Participante", font=("Helvetica",9), bg="white")
    drop_participants = ttk.Combobox(root, values=participants, width=35, state='readonly')

    btn_query_data = tk.Button(root, text="Consultar movimentação",font=("Helvetica",9), bg="#E8F5E9", width=25, height=2, command=execute_query_mov_fin)

    lbl_result_query = tk.Label(root, text="Dados da consulta", font=("Helvetica",12), bg="white")



    ###########################

   
    lbl_title.place(x=195, y=80)

    lbl_competence_start.place(x=100, y=130)
    entry_competence_start.insert(0, current_competence)
    entry_competence_start.place(x=210, y=132)

    lbl_competence_end.place(x=100, y=160)
    entry_competence_end.insert(0, current_competence)
    entry_competence_end.place(x=210, y=162)
    
    lbl_cat_type.place(x=300, y=130)
    drop_cat_type.place(x=380 , y=132)
    drop_cat_type.current(0)
    
    lbl_participants.place(x=300,y=160)
    drop_participants.current(0) 
    drop_participants.place(x=380 ,y=162)

    lbl_mov_type.place(x=100,y=190)
    drop_mov_type.current(0)
    drop_mov_type.place(x=210,y=190)
    
    btn_query_data.place(x=275, y=230)

    lbl_result_query.place(x=300, y=300)


def layout_starter():
    """
    Set the starter layout, all functions are disponibilized in this layout 
    """

    remove_widgets()
  
  
    lbl_desc_1 = tk.Label(root, text="Lançamentos", font=("Helvetica", 15), bg="white")
    btn_launch_fin = tk.Button(root, text="Movimentação financeira", font=("Helvetica", 11), bg="white", command=layout_launch_finance, width=25,height=2)

    lbl_desc_2 = tk.Label(root, text="Consultas", font=("Helvetica", 15), bg="white")
    btn_query_fin = tk.Button(root, text="Movimentação financeira", font=("Helvetica", 11), bg="white", command=layout_query_finance, width=25,height=2)

    lbl_desc_1.place(x=110,y=150)
    btn_launch_fin.place(x=50,y=200)
    
    lbl_desc_2.place(x=525,y=150)
    btn_query_fin.place(x=450,y=200)




if __name__ == '__main__':
    root = tk.Tk()
    root.geometry("730x750+0+0")
    root.title("EFC - Easy Finance Controller")
    root.resizable(width=False, height=False)
    root.config(bg='white')
    

    png_logo = Image.open(r'src\assets\logo_efc.png')
    png_logo = ImageTk.PhotoImage(png_logo)
    lbl_logo = tk.Label(root, image=png_logo, highlightcolor='white',highlightthickness=False, border=0)
    lbl_logo.place(x=315, y=5)

    btn_return = tk.Button(root, text="Início", font=("Helvetica", 11), bg="white", command=layout_starter, width=7,height=1)
    btn_return.place(x=610, y=7)
    
    layout_starter()
    root.mainloop()

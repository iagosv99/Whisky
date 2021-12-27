import streamlit as st
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import  stopwords
from nltk.stem import PorterStemmer
import numpy as np
import altair as alt
from itertools import cycle
from st_aggrid import  GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode

import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import pairwise_distances

nltk.download('punkt')
nltk.download('stopwords')

global df

#Tratamiento del dataset
url = 'https://raw.githubusercontent.com/AnHell999/Whisky/main/scotch_review.csv'
df = pd.read_csv(url)
df = df.drop(['currency', 'Unnamed: 0'], axis=1)
df[['review.point']].astype(int)
df['price'] = pd.to_numeric(df['price'])
df_copy  = df.copy(True) 

################################################################
def procesarDf(df_proc):
  ps = PorterStemmer()
  procesedTxt = []

  for row in df_proc.itertuples(index=False):

    text = word_tokenize(row[4])
    stops = set(stopwords.words("english"))
    text = [ps.stem(w) for w in text if not w in stops and w.isalnum()]
    text = " ".join(text)

    procesedTxt.append(text)

  df_proc['procesed_desc'] = pd.Series(procesedTxt)
  return df_proc

################################
def getMatrix(df_proc):  
  BoWModel = TfidfVectorizer()
  BoWModel.fit(df_proc['procesed_desc'])
  TextsBow = BoWModel.transform(df_proc['procesed_desc'])

  return pairwise_distances(TextsBow,TextsBow,metric='cosine')
################################       

# DB
import sqlite3
conn = sqlite3.connect('data.db')
c = conn.cursor()

# Functions
def create_table():
    c.execute('CREATE TABLE IF NOT EXISTS blogtable(author TEXT,title TEXT,article TEXT,postdate DATE)')


def view_all_notes():
    c.execute('SELECT * FROM blogtable')
    data = c.fetchall()
    return data

def view_all_titles():
    c.execute('SELECT DISTINCT title FROM blogtable')
    data = c.fetchall()
    return data

def get_nombre_Whisky(nombre,d):  
    i = d.loc[:, 'name'] == nombre
    df_nmobre = d.loc[i]
    return df_nmobre

def get_categoria_Whisky(categoria,d):  
    i = d.loc[:, 'category'] == categoria
    df_categoria = d.loc[i]
    return df_categoria

def get_precio_Whisky(precio,d):  
    i = d.loc[:, 'price'] == precio
    df_precio = d.loc[i]
    return df_precio

def filtradoNumerico(numericCol, min, max, ascent, d):

  df_precio = d.loc[(d.loc[:,numericCol] >= min) & (d.loc[:, numericCol] <= max)]
  df_precio = df_precio.sort_values(numericCol, ascending=ascent)
  return df_precio
    
def getIndex(value,d):
  print(value)
  i = d.loc[:, 'name'] == value
  df_tmp = d.loc[i]
  i2 = df_tmp.index.tolist()
  return i2[0]

def filtradoTextual(value,d):  
  i = d.loc[:, 'category'] == value
  df_single_malt = d.loc[i]
  return df_single_malt

def rango(index):
  precio_base = df_copy.price[index]
  min = precio_base/2
  max = precio_base*2
  d = filtradoNumerico('price',min,max,True,df_copy)
  d = filtradoTextual(df_copy.iloc[index].category, d)
  d = d.reset_index(drop=True)
  return d

def recomeda(index):
  df_to_recomend = procesarDf(df_copy)
  df_to_recomend = rango(index)

  index2 = getIndex(df_copy.name.iloc[index], df_to_recomend)

  matrixDescription = getMatrix(df_to_recomend)

  distance = list(enumerate(matrixDescription[index2]))
  ordenados_por_resena = sorted(distance, key=lambda x: x[1])
  top_index = ordenados_por_resena[1:10]
  top = [i[0] for i in top_index]

  return df_to_recomend.iloc[top]


# Layout Templates
html_temp = """
<div style="background-color:#955624;padding:10px;border-radius:10px">
<h1 style="color:white;text-align:center;">WISHKY</h1>
</div>
"""
title_temp ="""
<div style="background-color:#464e5f;padding:10px;border-radius:10px;margin:10px;">
<h4 style="color:white;text-align:center;">{}</h1>
<img src="https://www.w3schools.com/howto/img_avatar.png" alt="Avatar" style="vertical-align: middle;float:left;width: 50px;height: 50px;border-radius: 50%;" >
<h6>Author:{}</h6>
<br/>
<br/> 
<p style="text-align:justify">{}</p>
</div>
"""
article_temp ="""
<div style="background-color:#464e5f;padding:10px;border-radius:5px;margin:10px;">
<h4 style="color:white;text-align:center;">{}</h1>
<h6>Author:{}</h6> 
<h6>Post Date: {}</h6>
<img src="https://www.w3schools.com/howto/img_avatar.png" alt="Avatar" style="vertical-align: middle;width: 50px;height: 50px;border-radius: 50%;" >
<br/>
<br/>
<p style="text-align:justify">{}</p>
</div>
"""
head_message_temp ="""
<div style="background-color:#464e5f;padding:10px;border-radius:5px;margin:10px;">
<h4 style="color:white;text-align:center;">{}</h1>
<img src="https://www.w3schools.com/howto/img_avatar.png" alt="Avatar" style="vertical-align: middle;float:left;width: 50px;height: 50px;border-radius: 50%;">
<h6>Author:{}</h6> 
<h6>Post Date: {}</h6> 
</div>
"""
full_message_temp ="""
<div style="background-color:silver;overflow-x: auto; padding:10px;border-radius:5px;margin:10px;">
<p style="text-align:justify;color:black;padding:10px">{}</p>
</div>
"""

def main():
    
    st.markdown(html_temp.format('royalblue','white'),unsafe_allow_html=True)

    menu = ["Home","Iniciar Sesión","Registrarse","Encuentra tu whisky","Recomendador de whisky"]
    choice = st.sidebar.selectbox("Menu",menu)

    if choice == "Iniciar Sesión":
        st.subheader("Recomendador de whiskys")

        username = st.sidebar.text_input("Usuario")
        password = st.sidebar.text_input("Contraseña",type='password')

        if st.sidebar.checkbox("Iniciar Sesión"):

            create_usertable()
            hashed_pswd = make_hashes(password)

            result = login_user(username,check_hashes(password,hashed_pswd))
            if result:

                st.success("Hola {}".format(username))  

                if choice:
                    nombres = df['name'].unique()
                    st.write("")
                    nombre = st.selectbox('Introduce tu Whisky favorito\n', nombres)
  

                    index = getIndex(nombre,df)
                
                    recomendacion = recomeda(index)
                    recomendacionP=recomendacion[['name']]
                
                    st.caption("Tus 10 recomendaciones personalizadas:")

                    
                    #Example controlers
                    sample_size = st.sidebar.number_input("rows", min_value=10, value=10)
                    

                    return_mode = st.sidebar.selectbox("Return Mode", list(DataReturnMode.__members__), index=1)
                    return_mode_value = DataReturnMode.__members__[return_mode]

                    update_mode = st.sidebar.selectbox("Update Mode", list(GridUpdateMode.__members__), index=6)
                    update_mode_value = GridUpdateMode.__members__[update_mode]

                    #enterprise modules
                    enable_enterprise_modules = st.sidebar.checkbox("Enable Enterprise Modules")
                    if enable_enterprise_modules:
                        enable_sidebar =st.sidebar.checkbox("Enable grid sidebar", value=False)
                    else:
                        enable_sidebar = False

                    #features
                    fit_columns_on_grid_load = st.sidebar.checkbox("Fit Grid Columns on Load")

                    enable_selection=st.sidebar.checkbox("Enable row selection", value=True)
                    if enable_selection:
                        st.sidebar.subheader("Selection options")
                        selection_mode = st.sidebar.radio("Selection Mode", ['single','multiple'])
                        
                        use_checkbox = st.sidebar.checkbox("Use check box for selection")
                        if use_checkbox:
                            groupSelectsChildren = st.sidebar.checkbox("Group checkbox select children", value=True)
                            groupSelectsFiltered = st.sidebar.checkbox("Group checkbox includes filtered", value=True)

                        if ((selection_mode == 'multiple') & (not use_checkbox)):
                            rowMultiSelectWithClick = st.sidebar.checkbox("Multiselect with click (instead of holding CTRL)", value=False)
                            if not rowMultiSelectWithClick:
                                suppressRowDeselection = st.sidebar.checkbox("Suppress deselection (while holding CTRL)", value=False)
                            else:
                                suppressRowDeselection=False
                        st.sidebar.text("___")

                    enable_pagination = st.sidebar.checkbox("Enable pagination", value=False)
                    if enable_pagination:
                        st.sidebar.subheader("Pagination options")
                        paginationAutoSize = st.sidebar.checkbox("Auto pagination size", value=True)
                        if not paginationAutoSize:
                            paginationPageSize = st.sidebar.number_input("Page size", value=5, min_value=0, max_value=sample_size)
                        st.sidebar.text("___")

                    #Infer basic colDefs from dataframe types
                    gb = GridOptionsBuilder.from_dataframe(recomendacionP)

                    #customize gridOptions
                    gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc='sum', editable=True)


                    if enable_sidebar:
                        gb.configure_side_bar()

                    if enable_selection:
                        gb.configure_selection(selection_mode)
                        if use_checkbox:
                            gb.configure_selection(selection_mode, use_checkbox=True, groupSelectsChildren=groupSelectsChildren, groupSelectsFiltered=groupSelectsFiltered)
                        if ((selection_mode == 'multiple') & (not use_checkbox)):
                            gb.configure_selection(selection_mode, use_checkbox=False, rowMultiSelectWithClick=rowMultiSelectWithClick, suppressRowDeselection=suppressRowDeselection)

                    if enable_pagination:
                        if paginationAutoSize:
                            gb.configure_pagination(paginationAutoPageSize=True)
                        else:
                            gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=paginationPageSize)

                    gb.configure_grid_options(domLayout='normal')
                    gridOptions = gb.build()

                    grid_response = AgGrid(
                        recomendacionP, 
                        gridOptions=gridOptions,
                        height=300, 
                        width='100%',
                        data_return_mode=return_mode_value, 
                        update_mode=update_mode_value,
                        fit_columns_on_grid_load=fit_columns_on_grid_load,
                        allow_unsafe_jscode=True, #Set it to True to allow jsfunction to be injected
                        enable_enterprise_modules=enable_enterprise_modules,
                        )

                    recomendacionP = grid_response['data']
                    selected = grid_response['selected_rows']
                    selected_df = pd.DataFrame(selected)

                    with st.spinner("Displaying results..."):
                        #displays the chart
                        chart_data = recomendacionP.loc[:,['name']].assign(source='total')

                        if not selected_df.empty:
                            selected_data = selected_df.loc[:,['name']].assign(source='selection')
                            chart_data = pd.concat([chart_data, selected_data])


                        st.subheader("Whisky seleccionado:")
                        st.write(grid_response['selected_rows'])

                else:
                    st.warning("Incorrect Username/Password")

    elif choice == "Registrarse":
        st.subheader("Crear nueva cuenta")
        new_user = st.text_input("Usuario")
        new_password = st.text_input("Contraseña",type='password')

        if st.button("Registro"):
            create_usertable()
            add_userdata(new_user,make_hashes(new_password))
            st.success("Has creado exitosamente tu cuenta")
            st.info("Ir al menú de Inicio de Sesión para correctamente iniciar sesión")


    elif choice == "Home":
        st.write("")
        st.subheader("Lista de todos los whiskys")
        st.write("")
        st.write(df)
        st.write("")
        st.write("")
        
        
    elif choice == "Encuentra tu whisky":
        st.subheader("Encuentra tu whisky ideal")
        df_muestra = df

        st.write("Categoria")
        categorias = df['category'].unique()
        categoria = st.selectbox('Nombre', categorias)
        df_muestra = df[df['category'] == categoria]

        st.write("Precio")
        precios = df_muestra['price'].unique()
        precio_min = st.selectbox('Precio minimo', precios)
        precio_max = st.selectbox('Precio maximo', precios)
        if precio_min > precio_max:
            precio_min = precios.min()
            precio_max = precios.max()
        df_muestra = filtradoNumerico('price',precio_min,precio_max,True,df_muestra)

        ratings = df_muestra['review.point'].unique()
        rg_rev = st.slider('Rating',int(ratings.min()),int(ratings.max()),(80,85))                 
        df_muestra = filtradoNumerico('review.point',rg_rev[0],rg_rev[1],True,df_muestra)
        
        df_muestra            

    elif choice == "Recomendador de whisky":
        nombres = df['name'].unique()
        st.write("")
        nombre = st.selectbox('Tu Whisky favorito\n', nombres)
        df[df['name'] == nombre]

        index = getIndex(nombre,df)
    
        recomendacion = recomeda(index)
        st.dataframe(recomendacion[['name','description']])


import hashlib
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password,hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False

# DB  Functions
def create_usertable():
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT,password TEXT, whiskys TEXT)')


def add_userdata(username,password):
    c.execute('INSERT INTO userstable(username,password) VALUES (?,?)',(username,password))
    conn.commit()

def add_whisky(whisky):
    c.execute('INSERT INTO userstable(whiskys) VALUE (?)',(whisky))
    conn.commit()

def login_user(username,password):
    c.execute('SELECT * FROM userstable WHERE username =? AND password = ?',(username,password))
    data = c.fetchall()
    return data


def view_all_users():
    c.execute('SELECT * FROM userstable')
    data = c.fetchall()
    return data






if __name__ == '__main__':
    main()
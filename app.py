import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

global df

#Tratamiento del dataset
url = 'https://raw.githubusercontent.com/AnHell999/Whisky/main/scotch_review.csv'
df = pd.read_csv(url)
df = df.drop(['currency', 'Unnamed: 0'], axis=1)
df[['review.point']].astype(int)
df['price'] = pd.to_numeric(df['price'])
df_copy  = df.copy(True) 
################################
import nltk

from nltk.tokenize import word_tokenize
from nltk.corpus import  stopwords
from nltk.stem import PorterStemmer

nltk.download('punkt')
nltk.download('stopwords')
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
print()
################################
def getMatrix(df_proc):  
  BoWModel = TfidfVectorizer()
  BoWModel.fit(df_proc['procesed_desc'])
  TextsBow = BoWModel.transform(df_proc['procesed_desc'])

  return pairwise_distances(TextsBow,TextsBow,metric='cosine')

print()
################################
#           

# DB
import sqlite3
conn = sqlite3.connect('data.db')
c = conn.cursor()

# Functions
def create_table():
    c.execute('CREATE TABLE IF NOT EXISTS blogtable(author TEXT,title TEXT,article TEXT,postdate DATE)')

def add_data(author,title,article,postdate):
    c.execute('INSERT INTO blogtable(author,title,article,postdate) VALUES (?,?,?,?)',(author,title,article,postdate))
    conn.commit()

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


def get_review_Min(df):
    ratings_min = df['review.point'].min()
    return ratings_min

def get_review_Max(df):
    ratings_max = df['review.point'].max()
    return ratings_max

    

def get_blog_by_title(title):
    c.execute('SELECT * FROM blogtable WHERE title="{}"'.format(title))
    data = c.fetchall()
    return data
def get_blog_by_author(author):
    c.execute('SELECT * FROM blogtable WHERE author="{}"'.format(author))
    data = c.fetchall()
    return data

def delete_data(title):
    c.execute('DELETE FROM blogtable WHERE title="{}"'.format(title))
    conn.commit()


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
    """A Simple CRUD  Blog"""
    
    st.markdown(html_temp.format('royalblue','white'),unsafe_allow_html=True)

    menu = ["Home","Encuentra tu whisky"]
    choice = st.sidebar.selectbox("Menu",menu)



    if choice == "Home":
        st.subheader("Lista de todos los whiskys")
        st.write(df)
        st.caption("Para ordenar el dataset por una columna  -->  hacer click en el título de dicha columna")
        st.caption("Para visualizar el contenido completo de una celda  -->  en modo pantalla reducida, desplazar el cursor hacia dicha celda")

        st.subheader("Buscar whisky")
        search_choice = st.radio("Field to Search By",("nombre","categoria","precio","rating"))


        if search_choice == "nombre":
            nombres = df['name'].unique()
            nombre = st.selectbox('Nombre', nombres)
            df[df['name'] == nombre]

        elif search_choice == "categoria":
            categorias = df['category'].unique()
            categoria = st.selectbox('Nombre', categorias)
            df[df['category'] == categoria]
            

        elif search_choice == "precio":
            precios = df['price'].unique()
            precio_min = st.selectbox('Precio mínimo', precios,435)
            precio_max = st.selectbox('Precio máximo', precios,60)
            if precio_min > precio_max:
                precio_min = 12.0
                precio_max = 50.0
            df_precio = filtradoNumerico('price',precio_min,precio_max,True,df_copy)
            df_precio

        elif search_choice == "rating":
            rg_rev = st.slider('Rating',63,100,(80,99))                 
            st.write('Values', rg_rev)
            df_rating = filtradoNumerico('review.point',rg_rev[0],rg_rev[1],True,df_copy)
            df_rating
    
        
    elif choice == "Encuentra tu whisky":
        st.subheader("Encuentra tu whisky ideal")

        st.write("Categoría")
        categorias = df['category'].unique()
        categoria = st.selectbox('Nombre de la categoría', categorias)

        st.write("Precio")
        precios = df['price'].unique()
        precio_min = st.selectbox('Precio minimo', precios,435)
        precio_max = st.selectbox('Precio maximo', precios,60)
        if precio_min > precio_max:
            precio_min = 12.0
            precio_max = 1000000.0
        
        st.write("Rating")
        rg_rev = st.slider('Rating de los whiskys',63,100,(80,99))                 

        df_muestra = df    
        df_muestra = df[df['category'] == categoria]
        df_muestra = filtradoNumerico('price',precio_min,precio_max,True,df_muestra)   
        df_muestra = filtradoNumerico('review.point',rg_rev[0],rg_rev[1],True,df_muestra)
        df_muestra

    

if __name__ == '__main__':
    main()
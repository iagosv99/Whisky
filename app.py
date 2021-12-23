import streamlit as st
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import  stopwords
from nltk.stem import PorterStemmer

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

    menu = ["Home","Encuentra tu whisky","Recomendador de whisky"]
    choice = st.sidebar.selectbox("Menu",menu)



    if choice == "Home":
        st.write("")
        st.subheader("Lista de todos los whiskys")
        st.write("")
        st.write(df)
        st.write("")
        st.write("")
        st.video("https://www.youtube.com/watch?v=iyWG_uQjGW8&ab_channel=FREEMOVIES")

        
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
        nombre = st.selectbox('Nombre', nombres)
        df[df['name'] == nombre]

        index = getIndex(nombre,df)
    
        df_to_recomend = procesarDf(df_copy)
        df_to_recomend = rango(index)

        index2 = getIndex(df_copy.name.iloc[index], df_to_recomend)

        matrixDescription = getMatrix(df_to_recomend)

        distance = list(enumerate(matrixDescription[index2]))
        ordenados_por_resena = sorted(distance, key=lambda x: x[1])
        top_index = ordenados_por_resena[1:10]
        top = [i[0] for i in top_index]

        df_to_recomend.iloc[top]



if __name__ == '__main__':
    main()
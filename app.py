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
<div style="background-color:{};padding:10px;border-radius:10px">
<h1 style="color:{};text-align:center;">WISHKY </h1>
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

    menu = ["Home","View Posts","Add Posts","Search","Manage Blog"]
    choice = st.sidebar.selectbox("Menu",menu)



    if choice == "Home":
        st.subheader("Lista de todos los whiskys")
        try:
            df = pd.read_csv(url)
        except Exception as e:
            print(e)
            df = pd.read_excel(url)
        st.write(df)

        st.subheader("Buscar whisky")
        search_choice = st.radio("Field to Search By",("nombre","categoria","precio"))


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
            precio = st.selectbox('Precio', precios)
            df[df['price'] == precio]
                         
            
        st.subheader("Ver 15 ultimos")
        entrada = 15
        print("\n")
        i = int(entrada)
        st.write(df_copy.tail(i))
        
        
    elif choice == "View Posts":
        st.subheader("View Articles")
        all_titles = [i[0] for i in view_all_titles()]
        postlist = st.sidebar.selectbox("View Posts",all_titles)
        post_result = get_blog_by_title(postlist)
        for i in post_result:
            b_author = i[0]
            b_title = i[1]
            b_article = i[2]
            b_post_date = i[3]
            st.markdown(head_message_temp.format(b_title,b_author,b_post_date),unsafe_allow_html=True)
            st.markdown(full_message_temp.format(b_article),unsafe_allow_html=True)



    elif choice == "Add Posts":
        st.subheader("Add Articles")
        create_table()
        blog_author = st.text_input("Enter Author Name",max_chars=50)
        blog_title = st.text_input("Enter Post Title")
        blog_article = st.text_area("Post Article Here",height=200)
        blog_post_date = st.date_input("Date")
        if st.button("Add"):
            add_data(blog_author,blog_title,blog_article,blog_post_date)
            st.success("Post:{} saved".format(blog_title))	




    elif choice == "Search":
        st.subheader("Search Articles")
        search_term = st.text_input('Enter Search Term')
        search_choice = st.radio("Field to Search By",("title","author"))
        
        if st.button("Search"):

            if search_choice == "title":
                article_result = get_blog_by_title(search_term)
            elif search_choice == "author":
                article_result = get_blog_by_author(search_term)


            for i in article_result:
                b_author = i[0]
                b_title = i[1]
                b_article = i[2]
                b_post_date = i[3]
                st.markdown(head_message_temp.format(b_title,b_author,b_post_date),unsafe_allow_html=True)
                st.markdown(full_message_temp.format(b_article),unsafe_allow_html=True)




    elif choice == "Manage Blog":
        st.subheader("Manage Articles")

        result = view_all_notes()
        clean_db = pd.DataFrame(result,columns=["Author","Title","Articles","Post Date"])
        st.dataframe(clean_db)

        unique_titles = [i[0] for i in view_all_titles()]
        delete_blog_by_title = st.selectbox("Unique Title",unique_titles)
        new_df = clean_db
        if st.button("Delete"):
            delete_data(delete_blog_by_title)
            st.warning("Deleted: '{}'".format(delete_blog_by_title))


        if st.checkbox("Metrics"):
            
            new_df['Length'] = new_df['Articles'].str.len()
            st.dataframe(new_df)


            st.subheader("Author Stats")
            new_df["Author"].value_counts().plot(kind='bar')
            st.pyplot()

            st.subheader("Author Stats")
            new_df['Author'].value_counts().plot.pie(autopct="%1.1f%%")
            st.pyplot()

        if st.checkbox("Word Cloud"):
            st.subheader("Generate Word Cloud")
            # text = new_df['Articles'].iloc[0]
            text = ','.join(new_df['Articles'])
            wordcloud = WordCloud().generate(text)
            plt.imshow(wordcloud,interpolation='bilinear')
            plt.axis("off")
            st.pyplot()

        if st.checkbox("BarH Plot"):
            st.subheader("Length of Articles")
            new_df = clean_db
            new_df['Length'] = new_df['Articles'].str.len()
            barh_plot = new_df.plot.barh(x='Author',y='Length',figsize=(20,10))
            st.pyplot()


if __name__ == '__main__':
    main()


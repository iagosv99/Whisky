import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use('Agg')


####################################CSV
#Cargamos los datos del fichero csv de github 
url = 'https://raw.githubusercontent.com/AnHell999/Whisky/main/scotch_review.csv'
df = pd.read_csv(url)
df = df.drop(['currency', 'Unnamed: 0'], axis=1)
df[['review.point']].astype(int)
df['price'] = pd.to_numeric(df['price'])
df_copy  = df.copy(True)  

#Importamos librerias para el procesado del texto
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import  stopwords
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import pairwise_distances

nltk.download('punkt')
nltk.download('stopwords')

#Procesamos el texto
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

#Creación de la bolsa de palabras
def getMatrix(df_proc):  
  BoWModel = TfidfVectorizer()
  BoWModel.fit(df_proc['procesed_desc'])
  TextsBow = BoWModel.transform(df_proc['procesed_desc'])

  return pairwise_distances(TextsBow,TextsBow,metric='cosine')

print()

#Visualizar las últimas filas del dataset 
def visualizarTablas():
	entrada = 12#input("Numero de whiskys a listar por el final: ")
	print("\n")
	try:
		i = int(entrada)
	except:
		print(entrada +", no es un numero, se listaran los 5 ultimos whisky por defecto")
		i = 5

	df_copy.tail(i)

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
<h1 style="color:{};text-align:center;">Simple Blog </h1>
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
		st.subheader("Home")
		visualizarTablas()

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


import streamlit as st     
import pandas as pd
from dateutil.relativedelta import relativedelta 
import datetime, pytz   
import numpy as np
import plotly.express as px
from database_streamlit import Database
import plotly.graph_objects as go
import os
from utils import roundTime

user = os.environ["MONGO_USR"] 
password= os.environ["MONGO_PSSWD"]

cfg = {
        'mongo_url' : f"mongodb+srv://{user}:{password}@cluster0.qgy0n.mongodb.net/RiccioneSocialDist?retryWrites=true&w=majority",
        'db_name' : 'RiccioneSocialDist',
        'collection': 'people'
    }

DB = Database(cfg)
ITA = pytz.timezone("Europe/Rome")
DELTA_MIN = 5


def get_drawing_data(data, from_date, to_date, column="people_count"):
    offset = datetime.timedelta(minutes=DELTA_MIN)
    df = pd.DataFrame()
    from_date = roundTime(from_date, DELTA_MIN*60)
    to_date = roundTime(to_date, DELTA_MIN*60)  
    while from_date < to_date:
        next_time_frame = from_date+offset
        if not data.empty:
            date = data['timestamp'].dt.tz_localize(tz=ITA)
            mask = (date > from_date) & (date <= next_time_frame)
            rows = data.loc[mask] 
            if rows.empty:
                count = 0
            else:
                count = np.mean(rows[column])
        else:
            count = 0
        time_from = from_date.strftime("%H:%M")
        row = {'time': f'{time_from}',  'count': count}
        df = df.append(row, ignore_index=True)
        from_date += offset
    return df


def draw_histogram(data, column="count", title_name="People Count"):

    if not data.empty:
        # if title_name == "Indice distanziamento Sociale medio":
        #     data["color"] = 'green'
        #     data["color"].loc[data['count'] < 0.5] = 'red'
        # else:
        #     data["color"] = 'navy'
        
        # fig = px.bar(data, x='time', y='count', color="color", width=400, height=400)
        fig = px.bar(data, x='time', y='count',  width=400, height=400)
        
        fig.update_traces(showlegend=False)
        my_layout = go.Layout({"title": "", 
                                "yaxis": {'visible': True, 'showticklabels': True, 'ticks': 'outside', 'title': ''},
                                "xaxis": {'visible': True, 'showticklabels': True, 'ticks': 'outside', 'title': ''}})
        fig.update_layout( my_layout )        
        fig.update_layout(xaxis=go.layout.XAxis( tickangle = 330))  
        config = {'staticPlot': True}
        st.plotly_chart(fig, config=config)
        
def is_online(data, start_time):
    if data is not None:
        last_update = data['timestamp'].replace(tzinfo=None)  
        return (last_update + datetime.timedelta(seconds=120)) > start_time.replace(tzinfo=None)  
    else:
        return False   

def main():
 
    st.title("Var Group - Convention 2021")   
    st.subheader("Analisi Distanziamento Sociale")
    now = datetime.datetime.now().astimezone(ITA)
    current_time = now.strftime("%d-%m-%Y %H:%M")
    from_date = now - relativedelta(hours=1)

    # Get data from the database
    last_hour = DB.get_last_hour_data(from_date, now)
    data = DB.get_last_update()
    
    if is_online(data, now):
        st.write(f"🟢 Camera Online")
    else:
        st.write(f"🔴 Camera Offline")
    st.write(f"Ora Attuale: {current_time}")

    with st.container():
        current_people_count = data['current_people_count']
        st.header(f"🚶Conteggio Persone Attuale: {current_people_count}")
        people_count_df = get_drawing_data(last_hour, from_date, now, column="people_count")
        draw_histogram(people_count_df, title_name = "Numero medio di persone")
        parag = "Numero medio di persone nell'ultima ora ad intervalli di 5 minuti"
        st.write(parag)

    with st.container():
        current_covid_risk = data['current_covid_risk']
        st.header(f"⚠️ Indice di Distanziamento Sociale Attuale: {int(current_covid_risk*100)} %")
        covid_risk_df = get_drawing_data(last_hour, from_date, now, column="covid_risk")
        draw_histogram(covid_risk_df,  title_name = "Indice distanziamento Sociale medio")
        parag = "Indice di distanziamento sociale medio nell'ultima ora a intervalli di 5 minuti"
        st.write(parag)


    col1, col2, col3 = st.columns(3)
    button = col2.button(label="Aggiorna")
    if button:
        st.balloons()
    
    with st.expander("Apri Spiegazione"):
     st.write("""
         I grafici mostrano il numero medio di persone e l'indice di distanziamento sociale nell'ultima ora a intervalli di 5 minuti. \n
         L'indice di distanziamento Sociale è considerato come:
         (numero di persone distanti più di 70 cm ) / (numero totale di persone) """)

if __name__ == '__main__':
    main()

   
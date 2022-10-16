import streamlit as st
import datetime
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
import pickle
from math import floor, ceil
from tqdm import tqdm
import gc


da = pd.read_csv('traffic_data_processed.csv')
da = da.drop('ID', axis=1)
useless_cols1 = ['day_of_weekmin_vehicles', 'day_of_weekstd_vehicles',
                 'Vehicles', 'Seconds', 'Junction',
                 'day_of_weekmedian_vehicles', 'Year']
useless_cols2 = ['day_of_weekmin_vehicles',
                 'Vehicles', 'Seconds', 'Junction', ]
useless_cols3 = ['day_of_weekmin_vehicles',
                 'Vehicles', 'Seconds', 'Junction']
useless_cols4 = ['day_of_weekstd_vehicles', 'day_of_weekmin_vehicles',
                 'Vehicles', 'Seconds', 'Junction',
                 'Year', 'day_of_weekmedian_vehicles']

pickle_in = open("junction1_model.pkl", "rb")
junc1 = pickle.load(pickle_in)
pickle_in.close()

pickle_in = open("junction2_model.pkl", "rb")
junc2 = pickle.load(pickle_in)
pickle_in.close()

pickle_in = open("junction3_model.pkl", "rb")
junc3 = pickle.load(pickle_in)
pickle_in.close()

pickle_in = open("junction4_model.pkl", "rb")
junc4 = pickle.load(pickle_in)
pickle_in.close()

# @app.route('/')


def welcome():
    return "Welcome All"

# @app.route('/predict',methods=["Get"])


def predict_traffic(junction, DateTime):

    df = pd.DataFrame(columns=['DateTime', 'Junction', 'Year', 'Month',
                      'day_of_month', 'day_of_week', 'Date', 'Time', 'day_of_year'])
    df.loc[0] = 0
    df['DateTime'] = pd.to_datetime(DateTime)

    df['Year'] = df['DateTime'].dt.year
    df['Month'] = df['DateTime'].dt.month
    df['day_of_month'] = df['DateTime'].dt.day
    df['Junction'] = junction
    df['day_of_week'] = df['DateTime'].dt.dayofweek
    df['Date'] = df['DateTime'].dt.date
    df['Time'] = df['DateTime'].dt.hour

    df['day_of_year'] = df['DateTime'].dt.dayofyear
    df['Seconds'] = pd.to_timedelta(df['DateTime'].dt.strftime(
        '%H:%M:%S')).dt.total_seconds().astype(int)
    df['DateTime'] = df['DateTime'].values.astype(np.int64) / 10 ** 9
    L_encoder = LabelEncoder()
    df['Date'] = L_encoder.fit_transform(df['Date'])

    db = pd.concat([da, df], axis=0)

    def agg_functions(df1):
        features = ['Month', 'day_of_month',
                    'day_of_week', 'Date', 'Time', 'day_of_year']
        for x in tqdm(features):
            t = df1.groupby(x)['Vehicles'].agg(
                ['std', 'max', 'min', 'mean', 'median'])
            t.columns = [x+c+'_vehicles' for c in t.columns]
            t = t.astype({c: np.float32 for c in t.columns})
            t.reset_index(inplace=True)
    #         display(t)
            # display(t.T.to_dict('list'))
            df1 = df1.merge(t, on=x, how='left')
            gc.collect()
        return df1
    df = agg_functions(db)
    df = df.tail(1)
    #df = df.drop(useless_cols, axis=1).reset_index(drop=True)

    if junction == 1:
        df = df.drop(useless_cols1, axis=1).reset_index(drop=True)
        prediction = ceil(float(junc1.predict(df)))
    elif junction == 2:
        df = df.drop(useless_cols2, axis=1).reset_index(drop=True)
        prediction = ceil(float(junc2.predict(df)))
    elif junction == 3:
        df = df.drop(useless_cols3, axis=1).reset_index(drop=True)
        prediction = ceil(float(junc3.predict(df)))
    elif junction == 4:
        df = df.drop(useless_cols4, axis=1).reset_index(drop=True)
        prediction = ceil(float(junc4.predict(df)))

    return prediction


def main():
    #st.title("Junction Traffic Predictor by Team Scipy")
    html_temp = """
    <div style="background-color:tomato;padding:10px">
    <h2 style="color:white;text-align:center;font-family:'Caveat',cursive;font-weight: 400;max-width: 800px; width: 85%; margin: 0 auto;">Junction Traffic Predictor</h2>
    </div>
    """
    st.markdown(html_temp, unsafe_allow_html=True)

    date = st.sidebar.date_input(
        'Date', datetime.datetime.today())  # (2011, 1, 28))
    time = st.sidebar.time_input(
        'Time', datetime.datetime.now())  # (hour=18, minute=54, second=30))
    datestr = date.strftime("%Y-%m-%d")
    timestr = time.strftime("%H:%M:%S")
    DateTime = datestr + ' ' + timestr
    DateTime1 = pd.to_datetime(DateTime)
    junction = st.number_input(
        'Which Junction:', min_value=1, max_value=4, value=1, step=1, format='%d')

    prediction = predict_traffic(junction, DateTime)

    result = ""
    if st.button("Predict"):
        result = prediction
    st.success('Successful!!!')
    st.write('The Traffic Prediction for Junction', junction, ' at Date:',
             date, 'and Time:', time, 'is: ', prediction, '\u00B1 3 Vehicles')
    if st.button("About"):
        st.text("Team Scipy")
        st.text("Hamoye Premiere Project")
        st.text("Built with Streamlit")


if __name__ == '__main__':
    main()

from lectura_archivos import file_to_df,filtrar_patentes,get_OD_df
from tiempoViaje import get_ttravel_df, get_avg_df, get_poly_df
import plotly.graph_objs as go
import datetime
import dash
import dash_core_components as dcc
import dash_html_components as html
import os
import glob
import pandas as pd
from dash.dependencies import Input, Output
import flask

csalles_dir = os.path.abspath('/Users/Joni/Documents/matriz-OD/02_identificacion-archivos/Logs-U4-campos-salles')
pico_dir = os.path.abspath('/Users/Joni/Documents/matriz-OD/02_identificacion-archivos/Logs-U5-pico')

if 'TT.csv' not in os.listdir(os.getcwd()):
    dias = [3, 4, 5, 6]

    for i, dia in enumerate(dias):
        csalles_files = glob.glob(csalles_dir + '/*0' + str(dia) + '.log')
        pico_files = glob.glob(pico_dir + '/*0' + str(dia) + '.log')

        print('Definiendo el sentido para el dia {}'.format(dia))
        O, D = get_OD_df(csalles_files, pico_files)
        if i == 0:
            print('Tiempo de viaje para el dia {}'.format(dia))
            TT_df = get_ttravel_df(O, D, 6)
        else:
            print('Tiempo de viaje para el dia {}'.format(dia))
            aux_tt = get_ttravel_df(O, D, 6)
            TT_df = TT_df.append(aux_tt)

    TT_df.to_csv('TT.csv', index=False)
else:
    TT_df = pd.read_csv('TT.csv')

data_plot = [TT_df]

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

server = flask.Flask(__name__)
app = dash.Dash(__name__,server=server, external_stylesheets=external_stylesheets)

colors = {
    'background': '#ffffff',
    'text': '#111111'
}

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(
        children='Tiempo de Viaje',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    html.Div(children='Grafico de dispersión de tiempo de viaje', style={
        'textAlign': 'center',
        'color': colors['text']
    }),
    html.Div([
        dcc.Graph(
                    id='graph-with-input',
                ),
        html.I("Intervalo de tiempo para calcular el promedio. [min]"),
        html.Br(),
        dcc.Input(
                    id="input-min",
                    type="number",
                    value=5,
                    placeholder="Tiempo para promedio",
                    debounce=True
                )
    ])
])

@app.callback(
    Output('graph-with-input', 'figure'),
    [Input('input-min', 'value')])
def update_figure(avg_time):
    avg_df = get_avg_df(TT_df, avg_time)
    poly_df = get_poly_df((avg_df))
    data_plot = [
        go.Scatter(x=TT_df['Hora'],
                   y=TT_df['T_viaje'],
                   mode='markers',
                   marker=dict(color='black', size=3),
                   text=TT_df['Patente'],
                   name='Tiempo de viaje'
                   ),
        go.Scatter(x=avg_df['Hora'],
                   y=avg_df['T_viaje_avg'],
                   mode='markers',
                   marker=dict(color='yellow',size=5),
                   name='Promedio cada {} min.'.format(avg_time)
                   ),
        go.Scatter(x=poly_df['Hora'],
                   y=poly_df['T_viaje_poly'],
                   mode='lines',
                   marker=dict(color='red'),
                   line_width=3,
                   name='Curva de ajuste'
                   ),
    ]
    return {
            'data': data_plot,
            'layout': {
                'yaxis': {'title': 'Tiempo de viaje<br> </b>',
                          'tickmode': 'array',
                          'tickvals': list(range(0,max(TT_df['T_viaje'].values.tolist()),30)),
                          'ticktext': [str(datetime.timedelta(seconds=t)) for t in range(0,max(TT_df['T_viaje'].values.tolist()),30)]
                          },
                'yaxis_tickformat': '%M:%S s',
                'xaxis': {'title': 'Fecha y hora'},
                'plot_bgcolor': colors['background'],
                'paper_bgcolor': colors['background'],
                'font': {
                    'color': colors['text']
                },
                'hovermode':'closest',
            }
        }


if __name__ == '__main__':
    app.run_server(host = '10.78.175.27', port =5000 , debug=True)



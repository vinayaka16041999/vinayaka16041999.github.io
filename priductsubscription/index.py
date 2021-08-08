import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc
from variables import *
import plotly.graph_objects as go
from plotly.subplots import make_subplots


app = dash.Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])



app.layout = dbc.Container(
    [   
        html.Br(),
        dbc.Row(cards),
        html.Br(),
        html.Br(),
        html.Br(),
        dbc.Row(
            [   
                dbc.Col(graphs1,md=5),
                dbc.Col(graphs2,md=5),
                dbc.Col(controls),
            ],
        ),
    ],
    fluid=True,
    style={'margin':'0 !important','padding':'0 !important'}
)

@app.callback(
    Output("bar-graph", "figure"),
    [
        Input("age-group", "value"),
        Input("marital-status", "value"),
        Input("churn-type", "value"),
        Input("month-quarter","value")
    ],
)
def make_graph(age,marital,churn,monthq):
    if monthq == "month":
        temp1 = df[(df['churn_cat']=='{}'.format(churn)) & (df['marital']=='{}'.format(marital)) & (df['age_group']== '{}'.format(age))]
        temp1['month'] = temp1['month'].apply(lambda x: x.title())
        fig1 = px.histogram(temp1,x="month",color="job_type",histfunc="count",color_discrete_sequence=px.colors.sequential.Agsunset)
        return fig1
    else:
        temp1 = df[(df['churn_cat']=='{}'.format(churn)) & (df['marital']=='{}'.format(marital)) & (df['age_group']== '{}'.format(age))]
        fig1 = px.histogram(temp1,x="quarter",color="job_type",histfunc="count",color_discrete_sequence=px.colors.sequential.Agsunset)
        return fig1

 
@app.callback(
    Output("line-graph", "figure"),
    [
        Input("month-quarter","value"),
        Input("age-group","value"),
        Input("churn-type", "value")
    ],
)
def make_graph2(month_quarter,age,churn):
    temp2 = df[(df['age_group']=='{}'.format(age)) & (df['churn_cat']=='{}'.format(churn))]
    if month_quarter=="month":
        temp2['month'] = temp2['month'].apply(lambda x: x.title())
        time_data = temp2[['camp_success','month']].groupby('month').count().reindex(months_in_order)
        fig2 = px.line(time_data.cumsum(), x=time_data.index, y="camp_success",labels={'x':'Months'},height=400,color_discrete_sequence=['#0d0887'])
        return fig2
    else:
        time_data = temp2[['camp_success','quarter']].groupby('quarter').count().reindex(quarter_in_order)
        fig2 = px.line(time_data.cumsum(), x=time_data.index, y="camp_success",labels={'x':'Quarter'},height=400,color_discrete_sequence=['#0d0887'])
        return fig2

@app.callback(
    Output("bar-graph2", "figure"),
    [
        Input("loan-cat","value"),
        Input("churn-type", "value"),
        Input("age-group","value")
    ],
)
def make_graph3(loan,churn,age):
    temp3 = df[(df['hasloan']==loan) & (df['age_group']== '{}'.format(age))]
    balance_df = temp3[['job_type','balance']].groupby('job_type').mean().reset_index()
    if churn=="Subscribed":
            dff = df[(df['default']=='yes') | (df['churn']==1)].reset_index()
            gain_df = pd.merge(pd.crosstab(dff['job_type'],dff['default']).drop(columns="no").reset_index(),pd.crosstab(dff['job_type'],dff['churn_cat']).drop(columns="UnSubscribed").reset_index(),on=['job_type'])
            gain_df.replace(0,1,inplace=True)
            gain_df['%'] = ((gain_df.Subscribed-gain_df.yes)/gain_df.yes)*100
            graph1_data = pd.merge(gain_df,balance_df,on=['job_type'])
            
            fig3 = make_subplots(specs=[[{"secondary_y": True}]])
            fig3.add_trace(go.Bar(x=graph1_data['job_type'], y=graph1_data['balance'],marker={'color':'#46039f'}),secondary_y=False,)
            fig3.add_trace(go.Scatter(x=graph1_data['job_type'], y=graph1_data['%']),secondary_y=True,)
            fig3.update(layout_showlegend=False)
            fig3.update_xaxes(title_text="Job Type")
            fig3.update_yaxes(title_text="Avg Balance", secondary_y=False)
            fig3.update_yaxes(title_text="% Subscribers Gained", secondary_y=True)
            return fig3
    else:
            dff = df[(df['default']=='no') | (df['churn']==0)].reset_index()
            gain_df = pd.merge(pd.crosstab(dff['job_type'],dff['default']).drop(columns="yes").reset_index(),pd.crosstab(dff['job_type'],dff['churn_cat']).drop(columns="Subscribed").reset_index(),on=['job_type'])
            gain_df.replace(0,1,inplace=True)
            gain_df['%'] = ((gain_df.UnSubscribed-gain_df.no)/gain_df.no)*100
            graph1_data = pd.merge(gain_df,balance_df,on=['job_type'])
            
            fig3 = make_subplots(specs=[[{"secondary_y": True}]])
            fig3.add_trace(go.Bar(x=graph1_data['job_type'], y=graph1_data['balance'],marker={'color':'#46039f'}),secondary_y=False,)
            fig3.add_trace(go.Scatter(x=graph1_data['job_type'], y=graph1_data['%']),secondary_y=True,)
            fig3.update(layout_showlegend=False)
            fig3.update_xaxes(title_text="Job Type")
            fig3.update_yaxes(title_text="Avg Balance", secondary_y=False)
            fig3.update_yaxes(title_text="% UnSubscribers Gained", secondary_y=True)
            return fig3
            

@app.callback(
    Output("tree-map", "figure"),
    [
        Input("churn-type", "value"),
    ],
)
def make_graph4(churn):
    temp4 = df[(df['churn_cat']=='{}'.format(churn))]
    temp4 = temp4[['job_type','last_contact_duration']].groupby("job_type").mean('last_contact_duration').round(2).reset_index()
    fig4 = px.treemap(temp4,path=['job_type'],values='last_contact_duration',height=400,color_discrete_sequence=px.colors.sequential.Agsunset)
    fig4.data[0].textinfo = 'label+value'
    return fig4

@app.callback(
    Output("card-1","children"),

    [
     Input('churn-type','value'),
     Input("age-group","value"),
     Input('job-type','value')
     ]
    )
def update_cards(churn,age,job):
    temp5 = df[(df['churn_cat']=='{}'.format(churn)) & (df['age_group']=='{}'.format(age)) & (df['job_type']=='{}'.format(job))]
    if churn=="Subscribed":
        return '₹ '+str(round(temp5[["balance","churn"]].groupby("churn").mean().balance.iloc[0]))
    else:
        return '₹ '+str(round(temp5[["balance","churn"]].groupby("churn").mean().balance.iloc[0]))
 
@app.callback(
    Output("card-2","children"),
    Output("card-22","children"),
    [
     Input('churn-type','value'),
     ]
    )
def update_cards2(churn):
    temp6 = (pd.crosstab(index=df['age_group'],columns=df['churn_cat'],normalize='columns').round(3)*100)
    if churn=='Subscribed':
        perc = str(round(sum(temp6.sort_values(by="Subscribed",ascending=False).reset_index().iloc[:2,:].Subscribed)))+'%'
        lis = 'are '+temp6.sort_values(by="Subscribed",ascending=False).reset_index().iloc[:2,:].age_group[0]+' and '+temp6.sort_values(by="Subscribed",ascending=False).reset_index().iloc[:2,:].age_group[1]
        return perc,lis
    else:
        perc = str(round(sum(temp6.sort_values(by="UnSubscribed",ascending=False).reset_index().iloc[:2,:].UnSubscribed)))+'%'
        lis = 'are '+temp6.sort_values(by="UnSubscribed",ascending=False).reset_index().iloc[:2,:].age_group[0]+' and '+temp6.sort_values(by="UnSubscribed",ascending=False).reset_index().iloc[:2,:].age_group[1]
        return perc,lis
@app.callback(
    Output("card-3","children"),

    [
     Input('churn-type','value'),
     Input("age-group","value"),
     ]
    )
def update_cards3(churn,age):
    temp7 = df[df['age_group']=='{}'.format(age)]
    if churn=='Subscribed':
        perc = str(round((temp7['churn_cat'].value_counts()[1] - temp7['default'].value_counts()[1])/temp7['default'].value_counts()[1]*100))+'% '+'('+str(temp7['churn_cat'].value_counts()[1])+')'
        return perc
    else:
        perc = str(round((temp7['churn_cat'].value_counts()[0] - temp7['default'].value_counts()[0])/temp7['default'].value_counts()[0]*100))+'% '+'('+str(temp7['churn_cat'].value_counts()[0])+')'
        return perc

@app.callback(
    Output('card-4','children'),
    Output('card-44','children'),
    [
     Input('churn-type','value'),
     Input('job-type','value')
     ]
    )
def update_cards4(churn,job):
    temp8 = df[(df['churn_cat']=='{}'.format(churn)) & (df['job_type']=='{}'.format(job))]
    if churn=='Subscribed':
        d = temp = ((pd.crosstab(columns=temp8['churn_cat'],index=temp8['hasloan'],normalize='columns')*100).reset_index()).sort_values(by='Subscribed',ascending=False)
        if d.hasloan[0]==False:
            perc = str(round(d.Subscribed[0]))+'%'
            strg = "Customers dosen't have loan."
            return perc,strg
        else:
            perc = str(round(d.Subscribed[0]))+'%'
            strg = 'Customers has loan.'
            return perc,strg
    else:
        d = temp = ((pd.crosstab(columns=temp8['churn_cat'],index=temp8['hasloan'],normalize='columns')*100).reset_index()).sort_values(by='UnSubscribed',ascending=False)
        if d.hasloan[0]==False:
            perc = str(round(d.UnSubscribed[0]))+'%'
            strg = "Customers dosen't have loan."
            return perc,strg
        else:
            perc = str(round(d.UnSubscribed[0]))+'%'
            strg = 'Customers has loan.'
            return perc,strg
 
@app.callback(
    Output('card-5','children'),
    Input('churn-type','value')
    )
def update_cards5(churn):
    temp9 = df[df['churn_cat']=='{}'.format(churn)]
    val = str(round((temp9[['last_contact_duration','churn_cat']].groupby("churn_cat").mean()).last_contact_duration[0]))+' seconds'
    return val

if __name__ == "__main__":
    app.run_server(port='8080')
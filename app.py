from flask import Flask, flash, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
#from flask_table import Table, Col
from datetime import datetime
import sqlite3
import matplotlib.pyplot as plt
import squarify
import collections
import numpy as np
import pandas as pd
from pandas import DataFrame
#import pandas.io.formats.style
#from IPython.display import HTML

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///isg.db'
app.secret_key = 'dasistnurmeinkeyBYja6455'
db = SQLAlchemy(app)
global startwert
startwert = []

def berechnen(b_auswahl, bubble):

    # Massnahmen-Wirkung werden eingetragen
    def wirkung(massNr, massQu):
        dauer_bis = df_mass.loc[massNr - 1][7] + massQu +1 # bis wie lange wirkt es
        if dauer_bis > 9:   #vorher 8
            dauer_bis = 9   #vorher 8
        for z in range(11, anzmass1):  # kpi1 .. kpi19
            for s in range(massQu, dauer_bis):
                wirkungen[s][z - 11] = wirkungen[s][z - 11] + df_mass.loc[massNr - 1][z] / abschw_faktor


    db_conn = sqlite3.connect('isg.db')  # only memory ":memory:"
    engine = create_engine('sqlite:///isg.db', echo=False)
    the_cursor = db_conn.cursor()

    # SQL into Pandas
    query = "SELECT * from kpi ORDER BY nr ASC;"
    df_kpi = pd.read_sql_query(query, db_conn)
    query = "SELECT * from mass;"
    df_mass = pd.read_sql_query(query, db_conn)
    query = "SELECT * from treiber;"
    df_treiber = pd.read_sql_query(query, db_conn)
    query = "SELECT * from auswahl;"
    df_auswahl = pd.read_sql_query(query, db_conn)
    # Erstelle massnahmen array aus
    query_mass = "SELECT runde, M1, M2, M3, M4, M5, startwert, date_created FROM auswahl WHERE sim_id = '" + str(b_auswahl[0]) + "' AND gruppe = '" + str(b_auswahl[1])+ "' AND race = '" + str(b_auswahl[3]) + "';"
    query_start = "SELECT runde, M1, M2, M3, M4, M5, startwert, date_created FROM auswahl WHERE sim_id = '" + str(b_auswahl[0]) + "' AND runde = 0;"
    pd.set_option('max_colwidth', 240)
    df_auswahl_start = pd.read_sql_query(query_start, db_conn)
    df_auswahl_start['date_created'] = pd.to_datetime(df_auswahl_start['date_created'])

    df_auswahl_start.sort_values(by=['date_created'], ascending=False)
    while df_auswahl_start.shape[0] > 1:
        df_auswahl_start.drop([1], inplace=True)

    df_auswahl_mass1 = pd.read_sql_query(query_mass, db_conn).sort_values('runde')
    check_runde = df_auswahl_mass1['runde'][0]
    for i in range(df_auswahl_mass1.shape[0]-1):
        if df_auswahl_mass1['runde'][i+1] == check_runde:
            df_auswahl_mass1.drop([i+1], inplace=True)

    df_auswahl_mass = pd.concat([df_auswahl_start, df_auswahl_mass1], ignore_index=True, sort=False)

    anzahl_qu = len(df_auswahl_mass)
    if not df_auswahl_mass.loc[df_auswahl_mass['runde']==0].empty:
        anzahl_qu -= 1

    startwert = df_auswahl_mass.loc[df_auswahl_mass['runde']==0, 'startwert'].to_string()
    if startwert[:5] == 'Serie':
        startwert = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

    else:
        startwert = startwert[1:]
        startwert = startwert[1:len(startwert)].replace(' ', '').lstrip()
        startwert = startwert[1:len(startwert)].replace(',', ' ').lstrip()
        startwert = (startwert.split(" "))
        for ele in startwert:
            startwert = [float(ele) for ele in startwert]

    #startwert = [2.4, 2, 2.8, 3.2, 1.2, 3.2, 2.8, 5.2, 2, 2.8, 1.6, 1.6, 2.8, 2.4, 2.8, 2, 3.2, 4.8, 2]
    #startwert = input('Neuer Startwert    1, 2, 3, 4, 5, 6, 7, 8, 9 , 10, 11, 12, 13, 14, 15, 16, 17, 18, 19')

#    if len(startwert) == 0:
#        startwert = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

    startwert_tn = [0.00001, 0.00001, 0.00001, 0.00001, 0.00001, 0.00001, 0.00001, 0.00001, 0.00001, 0.00001, 0.00001, 0.00001, 0.00001, 0.00001, 0.00001, 0.00001, 0.00001, 0.00001, 0.00001]


    # füllt in kpi die Startwerte aus     #print(df_kpi.loc[:, ['identifier', 't0']])
    global kpi_liste
    kpi_liste = df_kpi['identifier'].to_list()
    df_kpi['t0'] = startwert
    for i in range(1, 10):
        df_kpi['t'+str(i)] = startwert_tn

    anzkpi = len(df_kpi)  # anzahl kpis = 19
    anzkpi1 = 9  # Anzahl Tertiale
    anzmass = len(df_mass)
    anzmass1 = 30  # spaltenanzahl in DB für massnahmen
    anztr = 19
    anztr1 = 5
    abschw_faktor = 4
    differenz = 2
    degradation = -0.07
    hw_abwertung = -0.05
    wirkungen = DataFrame(np.random.rand(anzkpi * anzkpi).reshape(anzkpi, anzkpi)) * 0


    # massQu = anzahl_qu
    for q in range(anzahl_qu+1):
        for i in range(1, 6):  # max 5 massnahmen je Qu
            massNr = df_auswahl_mass.loc[q][i]
            if not not massNr:
                if massNr > 0:
                    wirkung(massNr, q)  # massQu)   # Massnahmen-Wirkungen berechnen

    # Rechne UWD
    for q in range(0, anzkpi1):  # anzkpi1 anzahl tertial
        for k in range(0, anzkpi):  # anzahl KPIs
            for t in range(3, anztr1 + 3):  # Anzahl Treiber-Kpi auf einen KPI
                if len(str(df_treiber.loc[k][t])) > 3:
                    trInd = int(float(str(df_treiber.loc[k][t])))
                elif len(str(df_treiber.loc[k][t])) > 0:
                    trInd = df_treiber.loc[k][t]
                else:
                    trInd = 0
                tertial = 't' + str(q + 1)
                if trInd > 0:
                    if abs(df_kpi.loc[k][q + 8 -1] - df_kpi.loc[int(trInd) - 1][q + 8 -1]) > differenz:
                        if df_kpi.loc[k][q + 8 -1] > df_kpi.loc[int(trInd) - 1][q + 8 -1]:
                            df_kpi.at[k, tertial] = df_kpi.loc[k][q + 8] - 1
                        else:
                            df_kpi.at[k, tertial] = df_kpi.loc[k][q + 8] + 1
            hw_faktor = 1
            if q == 0:
                hw_faktor = 0

            df_kpi.at[k, tertial] = df_kpi.loc[k][q + 8] + df_kpi.loc[k][q + 8 -1] + wirkungen[q+1][k] \
                                    + (hw_abwertung + degradation * df_kpi.loc[k][q + 8 -1]) * hw_faktor     #jetzt sind UWD-Korrekturen gespeichert, nä.Schritt = addiere diese Werte mit Endwerten aus vorquartal


    endwert=df_kpi   # Todo schreibe in kpi
    df_kpi.to_sql('kpi', con=engine, if_exists='replace', index=False)
    if bubble == 1:
        endwert = df_kpi['t' + str(i)].values.tolist()   #lass dir eine liste zurückgeben

    return endwert
    

class Auswahl(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sim_id = db.Column(db.String(50))
    gruppe = db.Column(db.String(30))
    runde = db.Column(db.Integer)
    race = db.Column(db.String(5), default=" ")
    M1 = db.Column(db.Integer, default=0)
    M2 = db.Column(db.Integer, default=0)
    M3 = db.Column(db.Integer, default=0)
    M4 = db.Column(db.Integer, default=0)
    M5 = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    startwert = db.Column(db.String(240))

    #def __repr__(self):
    #    return '<Task %r>' % self.id


class Kpi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Nr = db.Column(db.Integer)
    identifier = db.Column(db.String(50))
    title = db.Column(db.String(50))
    dimension = db.Column(db.String(20))
    race = db.Column(db.String(5))
    explanation = db.Column(db.String(200))
    t0 = db.Column(db.Float)
    t1 = db.Column(db.Float)
    t2 = db.Column(db.Float)
    t3 = db.Column(db.Float)
    t4 = db.Column(db.Float)
    t5 = db.Column(db.Float)
    t6 = db.Column(db.Float)
    t7 = db.Column(db.Float)
    t8 = db.Column(db.Float)
    t9 = db.Column(db.Float)
    

class Mass(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Nr = db.Column(db.Integer)
    title = db.Column(db.String(50))
    kosten = db.Column(db.Integer)
    wissen = db.Column(db.Integer)
    quality = db.Column(db.Integer)
    zeit = db.Column(db.Integer)
    dauer = db.Column(db.Integer)
    lag = db.Column(db.Integer)
    fokus_kpi = db.Column(db.String(50))
    segment = db.Column(db.String(50))
    k01= db.Column(db.Integer)
    k02= db.Column(db.Integer)
    k03= db.Column(db.Integer)
    k04= db.Column(db.Integer)
    k05= db.Column(db.Integer)
    k06= db.Column(db.Integer)
    k07= db.Column(db.Integer)
    k08= db.Column(db.Integer)
    k09= db.Column(db.Integer)
    k10= db.Column(db.Integer)
    k11= db.Column(db.Integer)
    k12= db.Column(db.Integer)
    k13= db.Column(db.Integer)
    k14= db.Column(db.Integer)
    k15= db.Column(db.Integer)
    k16= db.Column(db.Integer)
    k17= db.Column(db.Integer)
    k18= db.Column(db.Integer)
    k19= db.Column(db.Integer)


class Treiber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Nr = db.Column(db.Integer)
    identifier = db.Column(db.String(50))
    treiber1= db.Column(db.Integer)
    treiber2= db.Column(db.Integer)
    treiber3= db.Column(db.Integer)
    treiber4= db.Column(db.Integer)
    treiber5= db.Column(db.Integer)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))


@app.route('/treemap')
def treemap():
    def element(elem):
        return elem[1]

    def not_in_use(filename):
        try:
            os.rename(filename, filename)
            return True
        except:
            return False

    db_conn = sqlite3.connect('isg.db')
    query = "SELECT M1, M2, M3, M4, M5 from auswahl;"
    df = pd.read_sql_query(query, db_conn)
    df = df.values.tolist()
    df = [item for elem in df for item in elem]
    df = [x for x in df if str(x) != 'nan']
    df = [x for x in df if str(x) != '']
    counter = collections.Counter(df)
    mass = []
    mass = [counter.keys()]
    mass = [item for elem in mass for item in elem]
    #mass = [(map(int, mass))]
    #mass = [int(i) for i in mass]
    wert = []
    wert = [counter.values()]
    wert = [item for elem in wert for item in elem]
    #auswertung = [ [mass] for mass in zip(mass, wert)]
    auswertung = np.column_stack(( mass, wert)).tolist()
    auswertung.sort(key=element, reverse=True)
    df_auswertung = pd.DataFrame(auswertung)
    color_list = ["gold", "turquoise", "purple"]
    squarify.plot(sizes=df_auswertung[1], label=df_auswertung[0],
                  text_kwargs={'fontsize': 9, 'fontname': "Roboto", 'weight': 'normal'}, norm_x=8, norm_y=5,
                  color=color_list, alpha=0.2, bar_kwargs=dict(linewidth=2, edgecolor="white"))
    plt.axis('off')
    plt.savefig("image\Massnahmen_Treemap.png", format="png")
    #plt.show()
    return render_template('treemap.html', **locals())



@app.route('/startwert', methods=('GET', 'POST'))
def startwert():
    global startwert
    flash('kein startwert')

    #startwert = [2.4, 2, 2.8, 3.2, 1.2, 3.2, 2.8, 5.2, 2, 2.8, 1.6, 1.6, 2.8, 2.4, 2.8, 2, 3.2, 4.8, 2]
    if request.method == 'POST':
        content = request.form['content']
        if not content:
            return redirect('startwert.html')

        return render_template('/')

    return render_template('startwert.html')


@app.route('/list')
def list():

    con = sqlite3.connect("isg.db")
    #con.row_factory = sqlite3.Row
    #cur = con.cursor()
    #cur.execute("select * from auswahl")
    #rows = cur.fetchall()
    query = "SELECT * from auswahl ORDER BY sim_id, date_created DESC;"
    rows = pd.read_sql_query(query, con)

    return render_template("list.html", rows=rows)

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        task_sim_id = request.form.get('sim_id')
        task_gruppe = request.form.get('gruppe')
        task_runde = request.form.get('runde')
        task_race = request.form.get('race')
        task_M1 = request.form.get('M1')
        task_M2 = request.form.get('M2')
        task_M3 = request.form.get('M3')
        task_M4 = request.form.get('M4')
        task_M5 = request.form.get('M5')
        task_startwert = request.form.get('startwert')

        new_task = Auswahl(sim_id=task_sim_id, gruppe= task_gruppe, runde= task_runde, race=task_race, M1=task_M1, M2=task_M2, M3=task_M3, M4=task_M4, M5=task_M5, startwert=task_startwert)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was no DB'
    else:
        task = Auswahl.query.order_by(Auswahl.date_created.desc()).all()
        return render_template('index.html', tasks=task, **locals())


@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Auswahl.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that'


@app.route('/bubblecalc/<string:bubbleargumente>', methods=['POST', 'GET'])
def bubblecalc(bubbleargumente):
    listArgumente = (bubbleargumente.split(";"))
    #muster für argumente = SIMID; GRUPPE; Runde; RACE; m1; m2; m3; m4; m5  zB Test;A;1;R;42;24;66
    i = 0
    Argumente = []
    for ele in listArgumente:
        if i == 2 or i > 3:
            Argumente.append(int(ele))
        else:
            Argumente.append(ele)
        i += 1
    for j in range(9-i):
        Argumente.append(0)

    task = Auswahl.query.first_or_404()
    #if request.method == 'POST':
    task.sim_id = Argumente[0]
    task.gruppe = Argumente[1]
    task.runde = Argumente[2]
    task.race = Argumente[3]
    task.M1 = Argumente[4]
    task.M2 = Argumente[5]
    task.M3 = Argumente[6]
    task.M4 = Argumente[7]
    task.M5 = Argumente[8]
    task.startwert = ""

    new_task = Auswahl(sim_id=task.sim_id, gruppe=task.gruppe, runde=task.runde, race=task.race, M1=task.M1, M2=task.M2, M3=task.M3, M4=task.M4, M5=task.M5, startwert=task.startwert)

    #try:
    db.session.add(new_task)
    db.session.commit()
    b_auswahl = [task.sim_id, task.gruppe, task.runde, task.race, task.M1, task.M2, task.M3, task.M4, task.M5, task.startwert]
    neuberechnet = np.round(berechnen(b_auswahl,1), 2)        #berechnen(b_auswahl, 1=von bubble  0=aus programm)
    neuberechnet = str(neuberechnet)
    neuberechnet = neuberechnet.replace('[', '')
    neuberechnet = neuberechnet.replace(']', '')
    #print(neuberechnet)

    return neuberechnet           #redirect('/')
    #except:
    #    return 'There was no DB'
    #return redirect('/')


@app.route('/bubblestart/<string:bubbleargumente>', methods=['POST', 'GET'])
def bubblestart(bubbleargumente):
    listArgumente = (bubbleargumente.split(";"))
    #muster für argumente = SIMID; startwerte  zB Test;42,4.3,6.6
    Argumente = []
    for ele in listArgumente:
        Argumente.append(ele)

    task = Auswahl.query.first_or_404()
    #if request.method == 'POST':
    task.sim_id = Argumente[0]
    task.gruppe = ''
    task.runde = 0
    task.race = ''
    task.M1 = 0
    task.M2 = 0
    task.M3 = 0
    task.M4 = 0
    task.M5 = 0
    task.startwert =  Argumente[1]

    new_task = Auswahl(sim_id=task.sim_id, gruppe=task.gruppe, runde=task.runde, race=task.race, M1=task.M1, M2=task.M2, M3=task.M3, M4=task.M4, M5=task.M5, startwert=task.startwert)

    #try:
    db.session.add(new_task)
    db.session.commit()
    return 'Done'     #redirect('/')


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Auswahl.query.get_or_404(id)

    if request.method == 'POST':
        task.sim_id = request.form['sim_id']
        task.gruppe = request.form['gruppe']
        task.runde = request.form['runde']
        task.race = request.form['race']
        task.M1 = request.form['M1']
        task.M2 = request.form['M2']
        task.M3 = request.form['M3']
        task.M4 = request.form['M4']
        task.M5 = request.form['M5']
        task.startwert = request.form['startwert']

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating your task'
    else:
        return render_template('update.html', task=task)


@app.route('/calcul/<int:id>', methods=['GET', 'POST'])
def calcul(id):

    def color(val):
        if val < 0:
            color = 'red'
        elif val >= 4:
            color = 'green'
        else:
            color = 'yellow'
        return 'background-color: %s' % color

    task = Auswahl.query.get_or_404(id)
    b_auswahl = [task.sim_id, task.gruppe, task.runde, task.race, task.M1, task.M2, task.M3, task.M4, task.M5, task.startwert]
    #if len(startwert) == 0:
    #    startwert = input("Startwert ist: ")
    endwert_q = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    #Berechnen
    neuberechnet = np.round(berechnen(b_auswahl,0), 2)
    kpi_liste_name = neuberechnet['identifier'].values.tolist()
    endwert_q = neuberechnet['t'+str(b_auswahl[2])].values.tolist()
    #html_result = HTML(neuberechnet.to_html(classes='table table-striped'))

    df = neuberechnet[['identifier', 'title', 't0', 't1', 't2', 't3', 't4', 't5', 't6', 't7', 't8', 't9']]
    #df = df.round(decimals=2)
    #df.style.format({'t1': '{:.2%}', 't2': '{:.2%}', 't3': '{:.2}'})
    #pd.options.display.float_format = '{:,.2f}'.format
    styled_df = df.style.applymap(color, subset=['t0', 't1', 't2', 't3', 't4', 't5', 't6', 't7', 't8', 't9'])                   #.format("{:.2f}")

    html = styled_df.hide_index().render()
    html = html.replace("000", "")
    #tasks = Kpi.query.all()
    #print(tasks)
    return render_template('calcul.html',  **locals())


if __name__ == "__main__":
    app.run(debug=True)

#bausw= ['ISAAC','D', 3, '', 40,	56,	63, 0,0,'']
#berechnen(bausw)
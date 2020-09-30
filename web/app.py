from flask_pymongo import PyMongo
from flask import Flask, render_template
import io
import random
import matplotlib.ticker as ticker
from flask import Response
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://db_mongo:27017/flask_db"
mongo = PyMongo(app)


@app.route('/plot.png')
def plot_png():
    fig = create_figure()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

def create_figure():
    x_data = mongo.db.api_data.find({}, {"_id": 0, "datetime_str": 1})
    y_data = mongo.db.api_data.find({}, {"_id": 0, "wind_speed": 1})
    x = list(map(lambda x: x['datetime_str'], x_data))[:12]
    y = list(map(lambda x: x['wind_speed'], y_data))[:12]
    figure, ax = plt.subplots(figsize=(11.1, 4))
    #figure.patch.set_facecolor('#191919')
    #ax.set_facecolor('#191919')
    ax.plot(
        x,
        y,
        color='#24385b',
        marker='o',
        ms='18',
        linewidth=2
    )
    lines = '#dde3e6'
    ax.hlines(8, 0, (len(x) - 1), color='red', linestyle=':')
    ax.grid(color=lines, linewidth=1)
    ax.spines['bottom'].set_color(lines)
    ax.spines['top'].set_color(lines)
    ax.spines['left'].set_color(lines)
    ax.spines['right'].set_color(lines)
    matplotlib.rcParams['axes.linewidth'] = 1.5
    ax.yaxis.set_major_locator(ticker.MultipleLocator(1))
    ax.set_ylabel('Speed m/s', color='black')
    ax.tick_params(
        axis='both',
        direction='inout',
        color=lines,
        labelcolor='black',
    )
    for x, y in zip(x, y):
        plt.text(
            x,
            y,
            str(y),
            horizontalalignment='center',
            verticalalignment='center',
            fontweight='bold',
            color='white',
            fontsize=9,
    )
    plt.tight_layout()
    return figure


@app.route('/')
def flask_mongo():
    data = mongo.db.api_data.find()
    return render_template(
        "flask.html",
        data=data,
        name='flask',
    )

@app.route('/django_postgres')
def django_postgres():
    return render_template(
        "django.html",
        name='django',
    )

@app.route('/documentation')
def documentation():
    return render_template(
        "documentation.html",
        name='documentation',
    )

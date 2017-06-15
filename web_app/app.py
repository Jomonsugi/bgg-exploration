from flask import Flask, render_template, request
from als_for_flask import for_flask
from jinja2 import Template
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/user_rec', methods=['POST'])
def button1():
    user_name = (request.form['user_input'])
    df = for_flask(user_name)
    # return render_template('user_rec.html',tables=[df.to_html(classes='user_recs')],
    # titles = ['na','Your Recommendations'])
    return render_template('user_rec.html', tables = df.to_html())


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
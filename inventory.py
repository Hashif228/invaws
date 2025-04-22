from flask import Flask,render_template,request,flash
app=Flask(__name__)
app.secret_key="heee"

@app.route("/dashboard")
def dashboard():
    return render_template('dashboard.html')


@app.route("/hom")
def hom():
    return render_template('hom.html')



@app.route("/ddd")
def ddd():
    return render_template('ddd.html')
@app.route("/login")
def login():
    return render_template('login.html')





@app.route("/report")
def report():
    return render_template('report.html')

@app.route("/das")
def das():
    return render_template('das.html')


@app.route("/products")
def products():
    return render_template('products.html')


@app.route("/fm",methods=['GET','POST'])
def fm():
    if request.method=="POST":
        uname=request.form["uname"]
        return f"hello {uname}"
    else:
        return render_template('fm.html')



@app.template_filter()
def hi(s):
    return s[::-1]

@app.route("/analytics")
def analytics():
    return render_template('analytics.html',jkk="hey")



@app.route("/stock")
def stock():
    return render_template('stock.html')

@app.route("/sales")
def sales():
    return render_template('sales.html')

@app.route("/search")
def search():
    return render_template("search.html")


@app.route("/setting")
def setting():
    return render_template("setting.html")


if __name__=="__main__":
    app.run(debug=True)
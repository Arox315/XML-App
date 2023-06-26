from flask import Flask, render_template, request, redirect, url_for
import xml.etree.cElementTree as ET
import os
import oracledb
import dbconfig
from xmlmethods import export_xml, insert_to_database, error_codes

app = Flask(__name__)
path = os.path.realpath(os.path.dirname(__file__))+"/tables"
conn = dbconfig.Connect()

tables = []
user = ""
password = ""
dsn = ""

@app.route("/")
def index():
    return render_template('index.html',tables = tables,len=len)

@app.route("/export-table/<string:table_name>")
def export_table(table_name):
    filepath = path+f"/{table_name}.xml"
    if not os.path.exists(filepath): 
        try:
            export_xml(table_name, user, password, dsn)
        except oracledb.Error as er:
            er_obj, = er.args
            error_code = er_obj.code
            error_message = er_obj.message
            error_summary = "Nieudało się nawiącać połączenia z bazą danych!"
            return render_template('error.html',tables=tables,table_name=None,err_data=[error_summary,error_code,error_message],len=len)
    tree = ET.parse(filepath)
    root = tree.getroot()
    return render_template('export-table.html',tables=tables,root=root,len=len)

@app.route("/import-table", methods=['GET','POST'])
def import_table():
    if user == "" or password == "" or dsn == "":
        return redirect(url_for('connect'))

    if request.method == "POST":
        if request.files:
            file = request.files['content']
            if file.filename == '': 
                return redirect(url_for('import_table'))
            tree = ET.parse(file)
            root = tree.getroot()
            
            try:
                insert_to_database(root, user, password, dsn)
            except oracledb.Error as er:
                er_obj, = er.args
                error_code = er_obj.code
                error_message = er_obj.message
                error_summary = error_codes[error_code] if error_code in error_codes else "Napotkano nieoczekiwany błąd!"
                return render_template('error.html',tables=tables,table_name=root.tag,err_data=[error_summary,error_code,error_message],len=len)
            else:
                return render_template('import-table.html',tables=tables,root=root,len=len)
        
    return render_template('import-table.html',tables=tables,root=None,len=len)

@app.route("/connect", methods=['GET','POST'])
def connect():
    if request.method == "POST":
        conn.set_connection_data(request.form['user'],
        request.form['password'], request.form['ip'],
        request.form['port'], request.form['service-name'])

        x,y,z = conn.get_connection_data()
        global user
        user = x
        global password
        password = y
        global dsn
        dsn = z

        try:
            connection = oracledb.connect(
                user=user,
                password=password,
                dsn=dsn
            ) 
        except oracledb.Error as er:
            er_obj, = er.args
            error_code = er_obj.code
            error_message = er_obj.message
            error_summary = "Nieudało się nawiącać połączenia z bazą danych!"
            return render_template('error.html',tables=tables,table_name=None,err_data=[error_summary,error_code,error_message],len=len)
        else:
            cursor = connection.cursor()
            cursor.execute("select table_name from user_tables order by table_name asc")
            table_names = cursor.fetchall()
            for table_name in table_names: tables.append(table_name[0].title())
            connection.close()
            return redirect(url_for('index'))
    
    return render_template('connect.html',tables=tables,len=len)


if __name__ == "__main__":
    app.run(debug=True)

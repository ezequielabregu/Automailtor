#!/usr/bin/env python
from flask import Flask, render_template, request, redirect, url_for
import csv, smtplib, ssl
import os
from datetime import datetime

app = Flask(__name__)

ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '.')) + '/'

@app.route('/')
def index():
    with open(ROOT_DIR+"contactos.csv") as file:
        reader = csv.reader(file)
        return render_template('index.html', csv=reader)

@app.route('/submit_form', methods=['POST'])
def submit_form():
    name = request.form.get('name')
    email = request.form.get('email')
    print(name)
    if not name or not email:
        with open(ROOT_DIR+"contactos.csv") as file:
            reader = csv.reader(file)
            error = "Name or email cannot be empty"
            return render_template('index.html', error=error, csv=reader)
    else:
        with open(ROOT_DIR+'contactos.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([name, email])

        with open(ROOT_DIR+"contactos.csv") as file:
            reader = csv.reader(file)
            return render_template('index.html', csv=reader)#, name=name)

@app.route('/edit_file', methods=['GET', 'POST'])
def edit_file():
    if request.method == 'POST':
        content = request.form['content']
        with open(ROOT_DIR+'static/mensaje.txt', 'w') as file:
            file.write(content)
        return redirect(url_for('index'))    
        #return render_template('success.html')
    else:
        with open(ROOT_DIR+'static/mensaje.txt', 'r') as file:
            content = file.read()
        return render_template('edit_file.html', content=content)

@app.route('/edit_data', methods=['GET', 'POST'])
def edit_data():
    if request.method == 'POST':
        with open(ROOT_DIR+'contactos.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(request.form.getlist('data'))
        return render_template('success.html')
    else:
        with open(ROOT_DIR+'contactos.csv', 'r') as csvfile:
            reader = csv.reader(csvfile)
            data = [row for row in reader]
        return render_template('edit_data.html', data=data)

@app.route('/upload', methods = ['GET', 'POST'])
def upload():
    if request.method == 'POST':
        f = request.files['file']
        f.save('contactos.csv')
        #print ('file uploaded successfully')
        return redirect(url_for('index'))  

@app.route('/send_emails', methods=['POST'])
def send_emails():

    sender = "eabregu.dev@gmail.com"
    password = "wbxjwtzkbuqbcfke"  # input("Type your password and press enter: ")

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender, password)

        with open(ROOT_DIR+"static/mensaje.txt", "r", encoding="utf-8") as f_text:
            text = f_text.read()
                    # Read the user names from a CSV file
            with open(ROOT_DIR+"contactos.csv", "r") as f:
                reader = csv.DictReader(f)
                read_csv = csv.reader(f)
                for row in reader:
                    message = text
                    message = message.format(name=row['name'])
                    #f.close()
                    print("======== Sending emails ========\n\n")
                    print(row['name'] + " ---> " + row['email'])
                    sending = row['name'] + " ---> " + row['email']
                    server.sendmail(
                        sender,
                        row['email'],
                        message
                    )
                #print("{:<15} {:<15} ".format(name, email))
        return redirect(url_for('success')) 

@app.route('/success')
def success():
    with open(ROOT_DIR+"contactos.csv") as file:
        reader = csv.reader(file)
        return render_template('success.html', csv=reader)

@app.route('/restart')
def restart():
    
    timestamp = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")

    with open(ROOT_DIR+'contactos.csv', mode='r') as source:
        reader = csv.reader(source)

        with open(ROOT_DIR+'archive/'+timestamp+'.csv', 'w', newline='') as destination:
            writer = csv.writer(destination)
            for row in reader:
                writer.writerow([row[0], row[1]])
    destination.close()
    source.close()

    os.remove(ROOT_DIR+'contactos.csv')

    with open(ROOT_DIR+'contactos.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['name', 'email'])
        file.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
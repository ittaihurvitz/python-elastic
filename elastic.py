from flask import Flask, render_template, flash, request
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
import requests
import json
 
# App config.
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176b'
 
class ReusableForm(Form):
    #name = TextField('Name:', validators=[validators.required()])
    simple = TextField('Simple:')
    nested = TextField('Nested:')
    mixed1 = TextField('Mixed1:')
    mixed2 = TextField('Mixed2:')
 
@app.route("/", methods=['GET', 'POST'])

def hello():

    URL = "http://localhost:9200/mixed1/_search"
    totalhits = "0"

    form = ReusableForm(request.form)
 
    print form.errors

    if request.method == 'POST':
        simple=request.form['simple']
        strsimple = simple.encode('ascii','ignore')

        nested=request.form['nested']
        strnested = nested.encode('ascii','ignore')
        
        mixed1=request.form['mixed1']
        strmixed1 = mixed1.encode('ascii','ignore')
        mixed2=request.form['mixed2']
        strmixed2 = mixed2.encode('ascii','ignore')
        print strsimple, " ", strnested, " ", strmixed1, " ", strmixed2

        data1 = {
                  "query": {
                    "simple_query_string" : {
                      "query" : strsimple,
                      "default_operator": "and"
                    }
                  }
                }


        
        data2 =  {
                  "query": {
                    "nested": {
                      "inner_hits": {
                        "highlight": {
                          "fields": {
                            "color": {}
                          }
                        }
                      },
                      "path": "prognosis",
                      "query": {
                        "bool": {
                          "must": [
                            {
                              "match": {
                                "prognosis.color": strnested
                              }
                            }
                          ]
                        }
                      }
                    }
                  }
                }

        data3 = {
                  "query": {
                    "bool": { 
                      "must": [
                        {
                          "match": {"age": strmixed1}
                        },
                        {
                          "nested": {
                            "inner_hits": {
                              "highlight": {
                                "fields": {
                                  "color": {}
                                }
                              }
                            },
                            "path": "prognosis",
                            "query": {
                              "bool": {
                                "must": [
                                  {
                                    "match": {
                                      "prognosis.color": strmixed2
                                    }
                                  }
                                ]
                              }
                            }
                          }
                        }
                      ]
                    }
                  }
                }

        if request.form['submit_button'] == 'simple':
            data = data1
            strrun = "simple with: " + strsimple
        elif request.form['submit_button'] == 'nested':
            data = data2
            strrun = "nested with: " + strnested
        elif request.form['submit_button'] == 'mixed':
            data = data3
            strrun = "mixed with: " + strmixed1 + " + " + strmixed2
        else:
            data = data1
            strrun = "nested with: " + strsimple


        flash('Running for= ' + strrun)

        print "#################"
        print data
        print "#################"
        r = requests.post(url = URL, json = data)
        text_file = open("Output.txt", "w")
        text_file.write(json.dumps(r.json(), indent=4)) # can consider sort_keys=True
        text_file.close()
        
        resp = r.json()
        totalhits = "0"
        try:
            totalhits = resp['hits']['total']
        except (NameError,KeyError):
            totalhits = "none"
        except:
            totalhits = "none!"

    if form.validate():
        # Save the comment here.
        flash('Total hits= ' + str(totalhits))
    else:
        flash('All the form fields are required. ')
        
    return render_template('query.html', form=form)
 
if __name__ == "__main__":
    app.run()

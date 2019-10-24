#import all neccesay libraries
import urllib
import json
import urllib.request
import urllib.parse
import random
import html
import re
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp
from helpers import *

# Configure application
app = Flask(__name__, template_folder='templates',static_folder='static')

#query all info for later use
namelist = get_names()
logo = get_thumbnail()
abstract = get_abs()
games = get_games()


# Ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/", methods=["GET", "POST"])
def index():
    '''index'''   
    return render_template("index.html",logo=logo)

@app.route("/Info", methods=["GET","POST"])
def inforoute():
    # Get ten titles with their respective links
    titlelist = []
    for title in games:
        temp = title.split('/')[-1]
        temp = re.sub("_", " " ,temp)
        titlelist.append(temp)
    game1 = titlelist[0]
    game2 = titlelist[1]
    game3 = titlelist[2]
    game4 = titlelist[3]
    game5 = titlelist[4]
    game6 = titlelist[5]
    game7 = titlelist[6]
    game8 = titlelist[7]
    game9 = titlelist[8]
    game10 = titlelist[9]
    
    #render the info page 
    return render_template("Info.html",abstract=abstract,games1=games[0],games2=games[1],games3=games[2],games4=games[3],games5=games[4],games6=games[5],games7=games[6],games8=games[7],games9=games[8],games10=games[9], game1=game1, game2=game2, game3=game3, game4=game4, game5=game5, game6=game6, game7=game7, game8=game8, game9=game9, game10=game10)

@app.route("/index", methods=["GET","POST"])
def indexroute():
    '''Index'''
    return render_template("index.html",logo=logo)

@app.route("/results", methods=["GET","POST"])
def resultsroute():

    #if any field is empty return error
    if request.args.get('pok1') == "" or request.args.get('pok2') == "":
        return render_template('apology.html')
    
    #Check if the entered names are pokemon
    if request.args.get('pok1') not in namelist or request.args.get('pok2') not in namelist:
        return render_template('apology.html')
    
    # Query the results
    result = results(request.args.get('pok1'),request.args.get('pok2'))
    
    # If there is a winner
    if len(result) == 4:
        # Split the results in all subparts
        tekst = result[0]
        image = result[1]
        
        # Create the link to the local directory
        sound = "static/sound/" + str((urllib.parse.unquote(str(result[2]))).split('/')[-1])
    
        #Little easteregg of limmy's show, recommendation: https://www.youtube.com/watch?v=uH0hikcwjIA
        if request.args.get('pok1') == "Steelix" and request.args.get('pok2') == "Fearow":
            tekst = tekst[:-1] + " and beacause Steel is heavier than Feathers"
        if request.args.get('pok1') == "Fearow" and request.args.get('pok2') == "Steelix":
            tekst = tekst[:-1] + " and because Steel is heavier than Feathers"

        # Create the bulbapedia (Wiki) link
        link = "https://bulbapedia.bulbagarden.net/wiki/" + result[3]

        # Render the results page
        return render_template("results.html",tekst=tekst,image=image,sound=sound,link=link)
    
    # If it is a draw
    else:
        # Split the results in all subparts
        tekst = result[0]
        image = result[1]
        image2 = result[3]
        
        # Create the links to the local directory
        sound = "static/sound/" + str((urllib.parse.unquote(str(result[2]))).split('/')[-1])
        sound2 = "static/sound/" + str((urllib.parse.unquote(str(result[4]))).split('/')[-1])
        
        # Create the bulbapedia (Wiki) links
        link1 = "https://bulbapedia.bulbagarden.net/wiki/" + result[5]
        link2 = "https://bulbapedia.bulbagarden.net/wiki/" + result[6]

        # Render the results page
        return render_template("resultsdraw.html",tekst=tekst, image=image, sound=sound, image2=image2, sound2=sound2, link1=link1, link2=link2)
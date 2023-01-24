import json
import os

import mysql.connector
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

# File path
CONFIG_PATH = os.path.join(ROOT, "config.json")

# Read MySQL username, password, database from configuration file
with open(CONFIG_PATH, "r") as f:
    jobj = json.load(f)
    MYSQL_USER = jobj["mysql_user"]
    MYSQL_PWD = jobj["mysql_pwd"]
    MYSQL_DB = jobj["mysql_db"]


@csrf_exempt
def index(request):
    return render(request, "index.html")


@csrf_exempt
def search(request):
    print(request.method)
    if request.method != "POST":
        return HttpResponse("Invalid request!")

    params = request.POST
    # used to produce query string, based off method selected by user
    def generateQuery(method, istring):
        # BOTH METHOD 1 AND 2 do NOT need istring
        # method 2, 3, 4 require 'imdb' table, method 1 queries 'posts' table
        if method == 1:
            return f"SELECT * FROM posts ORDER BY score Desc LIMIT {params['k']};"
        # MAY be able to share some code with method 4? 
        if method == 2:
            return f"SELECT * FROM imdb WHERE Movie_Titles LIKE \"%{params['year']}%\""

        # method 4, istring is USED ON one of three different columns
        column= ""        
        if params['typeChoice'] == 'post':
            column = 'Post_Titles'
        elif params['typeChoice'] == 'movie':
            column = 'Movie_Titles'
        elif params['typeChoice'] == 'genre':
            column = 'genres'
        return f"SELECT * FROM imdb WHERE {column} LIKE \"%{istring}%\""
    
    limit_no = int(params.get("limit", 20))
    usingKMethod = (params['k'] != '' and int(params['k']) > 0)    
    usingYearMethod = (params['year'] != '' and int(params['year']) > 0)
    usingWordCloud = ('wordcloud' in params)
    
    # order of precedence among FEATURES (aka methods for the backend):
    # k-most (1), year (2), cloud (3), then regular (4)
    if usingKMethod:
        query = generateQuery(1, "")
    elif usingYearMethod:
        query = generateQuery(2, "")
    elif usingWordCloud:
        order = "ASC"
        query = f"SELECT * FROM wordclouds ORDER BY wordcloud_urls {order} "
        query += f"LIMIT 1;"

    # Method 4: String is used as conditional value
    else:
        query = generateQuery(4, params['istring'])

    # IF the K-most method is chosen
    if not usingKMethod and not usingWordCloud:
        query += f" LIMIT {limit_no};"

    conn = mysql.connector.connect(user=MYSQL_USER, password=MYSQL_PWD,
                                   host="localhost",
                                   database=MYSQL_DB)
    cursor = conn.cursor()
    cursor.execute(query)

    # HTML Response Content
    # FOR Method one ONLY
    if usingKMethod:
        lines = [
            "<!DOCTYPE html>",
            "<html>",
            "<style>",
            "table, th, td {",
            "  border:1px solid black;",
            "}",
            "</style>",
            "<body>",
            "<table>",
            "  <tr>",
            "    <th>#</th>",
            "    <th>Title</th>",
            "    <th>ID</th>",
            "    <th>Score</th>",
            "    <th>Total Comments</th>",
            "    <th>URL</th>",
            "  </tr>",
        ]
        num = 1
        for row in cursor.fetchall():
            lines.append("  <tr>")
            # Result number, Title, ID, Score, Total Comments, URL
            lines.append(f"    <th>{num}</th>")
            lines.append(f"    <th>{row[0]}</th>")
            lines.append(f"    <th>{row[1]}</th>")
            lines.append(f"    <th>{row[2]}</th>")
            lines.append(f"    <th>{int(row[3])}</th>")
            lines.append(f"    <th>{row[4]}</th>")
            lines.append("  </tr>")
            num += 1
    elif usingWordCloud:
        url =  ".." + cursor.fetchall()[0][0][24:]
        print('type of url:', type(url))
        print('url:', url)
        lines = [
            "<!DOCTYPE html>",
            "<html>",
            "<style>",
            "table, th, td {",
            "  border:1px solid black;",
            "}",
            "</style>",
            "<body>",
            "<img src=\"https://i.postimg.cc/6qYKHcYj/titles-wordcloud.png\" />",
            "</body>",
            "</html>",
        ]
        return HttpResponse("\n".join(lines))
    else:   
        lines = [
            "<!DOCTYPE html>",
            "<html>",
            "<style>",
            "table, th, td {",
            "  border:1px solid black;",
            "}",
            "</style>",
            "<body>",
            "<table>",
            "  <tr>",
            "    <th>#</th>",
            "    <th>Post Title</th>",
            "    <th>Movie Title</th>",
            "    <th>Genre</th>",
            "  </tr>",
        ]
        num = 1
        for row in cursor.fetchall():
            lines.append("  <tr>")
            # Row number, Post Title, Movie Title, genre
            lines.append(f"    <th>{num}</th>")
            lines.append(f"    <th>{row[0]}</th>")
            lines.append(f"    <th>{row[1]}</th>")
            lines.append(f"    <th>{row[2]}</th>")
            lines.append("  </tr>")
            num += 1

    # Will occur for ALL features
    lines.append("</table>")
    lines.append("</body>")
    lines.append("</html>")
    cursor.close()
    conn.close()

    return HttpResponse("\n".join(lines))

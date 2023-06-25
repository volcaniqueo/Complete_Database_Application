from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection, IntegrityError
from django.shortcuts import render, redirect
import json
from decimal import Decimal

global auth_map
global active_user_type
global active_username
auth_map = dict()
auth_map["username_value"] = False
active_username = ""
active_user_type = ""

# Create your views here.

def log_out(request):
    global active_user_type
    global active_username
    auth_map[active_username] = False
    active_username = ""
    active_user_type = ""
    return redirect('/movie_app')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user_type = request.POST['user_type']
        db_table = ""
        if user_type == "database_manager":
            db_table = user_type
        else:
            db_table = "user1"
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM {0} WHERE username=(%s) AND password1=(%s);".format(db_table), [username, password])
            user = cursor.fetchone()
        if user is not None:
            # Assuming username is the column index of the user's username in the result
            auth_map[username] = True
            global active_user_type
            global active_username
            active_username = username
            active_user_type = user_type
            if user_type == "database_manager":
                return redirect('db_home/')
            elif user_type == "audience":
                return redirect('audience_home/')
            else:
                return redirect('director_home/')
        else:
            error_message = 'Invalid username or password.'
            return render(request, 'login.html', {'error_message': error_message})
    else:
        return render(request, 'login.html')


def db_home(request):
    if active_user_type == "database_manager":
        return render(request, "db_home.html")
    else:
        return redirect('/movie_app')
def add_user(request):
    if active_user_type != "database_manager":
        return redirect('/movie_app')
    if request.method == 'POST':
        name = request.POST['name']
        surname = request.POST['surname']
        username = request.POST['username']
        password = request.POST['password']
        user_type = request.POST['user_type']
        nationality = ""

        if user_type == "director":
            nationality = request.POST['nationality']

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO user1 (username, password1, surname, name1) "
                    "VALUES (%s, %s, %s, %s)",
                    [username, password, surname, name]
                )
                if user_type == "audience":
                    cursor.execute(
                        f"INSERT INTO audience (username) "
                        "VALUES (%s)",
                        [username]
                    )
                elif user_type == "director":
                    cursor.execute(
                        f"INSERT INTO director (username, nationality) "
                        "VALUES (%s, %s)",
                        [username, nationality]
                    )

                connection.commit()
                
                result_message = "Succesfully created user instance."

        except IntegrityError:
            result_message = "Username already exists!"
        
        except Exception as e:
            # Handle other exceptions
            print(f"Error creating User and Audience: {str(e)}")
            result_message = "Unsuccessfull attempt!"

        return render(request, "add_user.html",{'result_message':result_message})

    else:
        return render(request, "add_user.html")

def delete_audience(request):
    if active_user_type != "database_manager":
        return redirect('/movie_app')
    if request.method == 'POST':
        username = request.POST['username']
        with connection.cursor() as cursor:
            cursor.execute("SELECT EXISTS(SELECT 1 FROM audience WHERE username = %s)",[username])
            exists = cursor.fetchone()[0]

        if exists:
            try:
                with connection.cursor() as cursor:
                    cursor.execute("DELETE FROM user1 WHERE username = %s", [username])
                    connection.commit()

                result_message = "Succesfully deleted audience instance."
                return render(request, "delete_audience.html",{'result_message':result_message})
            except Exception as e:
                result_message = f"Unsuccessfull attempt! {str(e)}"
                return render(request, "delete_audience.html",{'result_message':result_message})

        else:
            result_message = "Unsuccessfull attempt! No such Audience instance present."
            return render(request, "delete_audience.html",{'result_message':result_message})
    else:
        return render(request, "delete_audience.html")

def update_director(request):
    if active_user_type != "database_manager":
        return redirect('/movie_app')
    if request.method == 'POST':
        username = request.POST['username']
        platform_id = request.POST['platform_id']
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT EXISTS(SELECT 1 FROM director WHERE username = %s)",[username])
                exists_dir = cursor.fetchone()[0]
                cursor.execute("SELECT EXISTS(SELECT 1 FROM rating_platform WHERE platform_id = %s)",[platform_id])
                exists_platform = cursor.fetchone()[0]
            if not exists_dir:
                result_message = "Unsuccessfull attempt! No such Director instance present."
                return render(request, "update_director.html",{'result_message':result_message})
            elif not exists_platform:
                result_message = "Unsuccessfull attempt! No such Rating Platform instance present."
                return render(request, "update_director.html",{'result_message':result_message})

            with connection.cursor() as cursor:
                cursor.execute("SELECT EXISTS(SELECT 1 FROM registered WHERE username = %s)",[username])
                registered_dir = cursor.fetchone()[0]
                if registered_dir:
                    cursor.execute("UPDATE registered SET platform_id = %s WHERE username = %s", [platform_id, username])
                    connection.commit()
                    result_message = "Rating Platform of the Director is updated."
                    return render(request, "update_director.html",{'result_message':result_message})
                else:
                    cursor.execute("INSERT INTO registered (username, platform_id) VALUES (%s, %s)",[username,platform_id])
                    connection.commit()
                    result_message ="Director registered to a Rating Platform for the first time."
                    return render(request, "update_director.html",{'result_message':result_message})
        except Exception as e:
            result_message = f"Unsuccessfull attempt! {str(e)}"
            return render(request, "update_director.html",{'result_message':result_message})

    else:
        return render(request, "update_director.html")

def view_list(request):
    if active_user_type != "database_manager":
        return redirect('/movie_app')
    if request.method == 'POST':
        choice = request.POST['choice']
        viewlist = []
        if choice == 'directors':
            with connection.cursor() as cursor:
                cursor.execute("SELECT director.username, name1, surname, nationality, platform_id "
                               "FROM director "   
                               "JOIN user1 AS u ON director.username = u.username " 
                               "JOIN registered AS reg ON reg.username = director.username;"
                               )
                viewlist = cursor.fetchall()
                viewlist = convert(viewlist)
                connection.commit()
        elif choice == 'directors-s':
            username = request.POST['username']
            with connection.cursor() as cursor:
                cursor.execute("SELECT movie.movie_id, movie.movie_name, theater.theater_id, theater.district, occupience_info.time1, occupience_info.slot_number "
                               "FROM movie "   
                               "JOIN directs ON movie.movie_id = directs.movie_id " 
                               "JOIN has_movie ON has_movie.movie_id = movie.movie_id " 
                               "JOIN place ON place.session_id = has_movie.session_id "
                               "JOIN occupience_info ON occupience_info.occupience_id = place.occupience_id " 
                               "JOIN theater ON occupience_info.theater_id = theater.theater_id "
                               "WHERE directs.username = (%s);",
                               [username]
                               )
                viewlist = cursor.fetchall()
                viewlist = convert(viewlist)
                viewlist = fix_time(viewlist, 4)
                connection.commit()
        elif choice == 'ratings':
            movie_id = request.POST['movie_id']
            with connection.cursor() as cursor:
                cursor.execute("SELECT movie.movie_id, movie.movie_name, movie.overall_rating "
                               "FROM movie " 
                               "WHERE movie.movie_id = (%s);",
                               [movie_id]
                               )
                viewlist = cursor.fetchall()
                viewlist = convert(viewlist)
                #for elem in viewlist:
                #    val = elem[-1]
                #    val = float(val.quantize(Decimal('0.00')))
                #    elem[-1] = val
                connection.commit()
        elif choice == 'movies':
            username = request.POST['username']
            with connection.cursor() as cursor:
                cursor.execute("SELECT movie.movie_id, movie.movie_name, ratings.rating "
                               "FROM movie "   
                               "JOIN ratings ON movie.movie_id = ratings.movie_id "
                               "JOIN audience ON ratings.username = audience.username "
                               "WHERE audience.username = (%s);" ,
                               [username]
                               )
                viewlist = cursor.fetchall()
                viewlist = convert(viewlist)
                connection.commit()
        viewlist_json = json.dumps(viewlist)
        choice_json = json.dumps(choice)
        return render(request, "view_list.html", {'viewlist_json':viewlist_json, 'choice_json':choice_json})
    else:
        return render(request, "view_list.html")

# Director User Functionalities
def director_home(request):
    if active_user_type == "director":
        return render(request, "director_home.html")
    else:
        return redirect('/movie_app')

def view_list_director(request):
    if active_user_type != "director":
        return redirect('/movie_app')
    if request.method == 'POST':
        choice = request.POST['choice']
        viewlist = []
        try:
            if choice == 'theaters':
                csv_input = request.POST['theaters']
                csv_list = csv_input.split(',')
                date = csv_list[0] + ' 00:00:00'
                tset = set()
                for i in range(1, len(csv_list)):
                    slot = csv_list[i]
                    with connection.cursor() as cursor:
                        cursor.execute("SELECT theater.theater_id "
                                   "FROM theater "   
                                   "JOIN occupience_info AS oi ON oi.theater_id = theater.theater_id " 
                                   "WHERE oi.slot_number = (%s) and oi.time1 = (%s);",
                                   [slot, date]
                                   )
                        tlist = cursor.fetchall()
                        tlist = convert(tlist)
                        connection.commit()
                    for elem in tlist:
                        tset.add(elem[0])
                occupied_list = tuple(tset)
                with connection.cursor() as cursor:
                    placeholders = ', '.join(['%s'] * len(occupied_list))
                    query = f"SELECT theater.theater_id, theater.district, theater.theater_capacity " \
                            f"FROM theater " \
                            f"WHERE theater.theater_id NOT IN ({placeholders});"
                    cursor.execute(query, occupied_list)
                    viewlist = cursor.fetchall()
                    viewlist = convert(viewlist)
                    connection.commit()
            elif choice == 'movies':
                with connection.cursor() as cursor:
                    cursor.execute("SELECT m.movie_id, m.movie_name, oi.theater_id, oi.time1, oi.slot_number, string_agg(p.predecessor_movie_id::text, ',') AS predecessors "
                                   "FROM movie m "
                                   "LEFT JOIN predecessors p ON m.movie_id = p.succeeds_movie_id "
                                   "INNER JOIN directs d ON m.movie_id = d.movie_id "
                                   "JOIN has_movie AS hm ON hm.movie_id = m.movie_id "
                                   "JOIN place AS pl ON pl.session_id = hm.session_id "
                                   "JOIN occupience_info AS oi ON oi.occupience_id = pl.occupience_id "
                                   "WHERE d.username = (%s) "
                                   "GROUP BY m.movie_id, m.movie_name, oi.theater_id, oi.time1, oi.slot_number "
                                   "ORDER BY m.movie_id ASC;",
                                   [active_username]
                    )
                    viewlist = cursor.fetchall()
                    viewlist = convert(viewlist)
                    viewlist = fix_time(viewlist, 3)
                    connection.commit()
            elif choice == 'audiences':
                movie_id = request.POST['audiences']
                with connection.cursor() as cursor:
                    cursor.execute("SELECT user1.username, user1.name1, user1.surname "
                                   "FROM user1 "
                                   "JOIN audience AS a ON a.username = user1.username "
                                   "JOIN bought_tickets AS bt ON bt.username = a.username "
                                   "JOIN movie_session AS mo ON mo.session_id = bt.session_id "
                                   "JOIN has_movie AS hm ON hm.session_id = mo.session_id "
                                   "JOIN movie ON movie.movie_id = hm.movie_id "
                                   "JOIN directs AS d ON d.movie_id = movie.movie_id "
                                   "WHERE d.username = (%s) AND movie.movie_id = (%s);",
                                   [active_username, movie_id]
                    )
                    viewlist = cursor.fetchall()
                    viewlist = convert(viewlist)
                    connection.commit()
            viewlist_json = json.dumps(viewlist)
            choice_json = json.dumps(choice)
            return render(request, "view_list_director.html", {'viewlist_json':viewlist_json, 'choice_json':choice_json})
        except:
            error_message = "Invalid Input!"
            return render(request, "view_list_director.html", {'error_message':error_message})

    return render(request, "view_list_director.html")

def add_movie(request):
    if active_user_type != "director":
        return redirect('/movie_app')
    if request.method == 'POST' and 'theater_id-2' in request.POST:
        theater_id = request.POST['theater_id-2']
        theater_name = request.POST['theater_name-2']
        theater_capacity = request.POST['theater_capacity']
        district = request.POST['theater_district']
        try:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO theater (theater_id,theater_name,theater_capacity,district) VALUES (%s, %s, %s, %s)",[theater_id,theater_name,theater_capacity,district])
                connection.commit()
                result_message = "Theater successfully created."
                return render(request, "add_movie.html",{'result_message_2':result_message,'theater_message': "ok"})
        except Exception as e:
                result_message = f"Unsuccessfull attempt with exception! {str(e)}"
                return render(request, "add_movie.html",{'result_message_2':result_message,'theater_message': "ok"})

    elif request.method == 'POST' and 'theater_id-2' not in request.POST:
        movie_id = request.POST['movie_id']
        movie_name = request.POST['movie_name']
        duration = request.POST['duration']
        theater_id = request.POST['theatre_id']
        time_slot = request.POST['time_slot']
        time = request.POST['time']
        time = time + ' 00:00:00'
        genre_list = request.POST['genre_list'].split(",")
        
        genre_ids = []

        exists_theater = False
        exists_movie = False
        exists_genre = True
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT EXISTS(SELECT 1 FROM theater WHERE theater_id = %s)", [theater_id])
                exists_theater = cursor.fetchone()[0]
                cursor.execute("SELECT EXISTS(SELECT 1 FROM movie WHERE movie_id = %s)", [movie_id])
                exists_movie = cursor.fetchone()[0]
                for genre in genre_list:
                    genre = genre.replace(" ", "")
                    cursor.execute("SELECT EXISTS(SELECT 1 FROM genre WHERE genre_name = %s)", [genre])
                    if cursor.fetchone()[0]:
                        cursor.execute("SELECT genre_id FROM genre WHERE genre_name = %s", [genre])
                        genre_ids.append(cursor.fetchone()[0])
                    else:
                        exists_genre = False
                        break
        except:
            result_message = 'Invalid input!'
            return render(request, "add_movie.html",{'result_message':result_message})
        
        if exists_genre and (not exists_movie) :
            if not exists_theater:
                result_message = 'Such theater does not exists!'
                return render(request, "add_movie.html",{'theater_message': "ok", 'result_message':result_message})   
            try:
                with connection.cursor() as cursor:
                    if int(time_slot) + int(duration) - 1 > 4:
                        result_message = "Error, valid slots are 1,2,3,4 (Think with duration)!"
                        return render(request, "add_movie.html",{'result_message':result_message})
                    time_slot_2 = time_slot
                    for i in range(int(duration)):
                        time_slot_2_insert = str(int(time_slot_2) + i)
                        cursor.execute("SELECT * FROM occupience_info WHERE time1 = (%s) AND slot_number = (%s) AND theater_id = (%s);",[time,time_slot_2_insert,theater_id])
                        result = cursor.fetchone()
                        if result is not None:
                            result_message = "Theater is occupied with given slot (Think with duration)!"
                            return render(request, "add_movie.html",{'result_message':result_message})
                    #insert_movie
                    cursor.execute("INSERT INTO movie (movie_id,movie_name,duration,overall_rating) VALUES (%s, %s, %s, %s)",[movie_id,movie_name,duration,None])
                    connection.commit()
                    #insert_genre
                    for genre_id in genre_ids:
                        cursor.execute("INSERT INTO genre_list (genre_id,movie_id) VALUES (%s, %s)",[genre_id,movie_id])
                        connection.commit()
                    #insert_directs
                    cursor.execute("INSERT INTO directs (username, movie_id) VALUES (%s, %s)",[active_username,movie_id])
                    connection.commit()
                    #insert_movie_session
                    session_id=0
                    cursor.execute("SELECT MAX(session_id) FROM movie_session")
                    row = cursor.fetchone()
                    if row:
                        session_id = row[0] + 1
                    cursor.execute("INSERT INTO movie_session (session_id) VALUES (%s)",[session_id])
                    connection.commit()
                    #insert_occupience_info
                    
                    for i in range(int(duration)):
                        time_slot_insert = str(int(time_slot) + i)
                        occupience_id=0
                        cursor.execute("SELECT MAX(occupience_id) FROM occupience_info")
                        row = cursor.fetchone()
                        if row:
                            occupience_id = row[0] + 1
                        cursor.execute("INSERT INTO occupience_info (occupience_id, time1, slot_number, theater_id) VALUES (%s, %s, %s, %s)",[occupience_id,time,time_slot_insert,theater_id])
                        connection.commit()
                        #insert_place
                        cursor.execute("INSERT INTO place (session_id, occupience_id) VALUES ( %s, %s)",[session_id,occupience_id])
                        connection.commit()
                    #insert_has_movie
                    cursor.execute("INSERT INTO has_movie (session_id, movie_id) VALUES ( %s, %s)", [session_id,movie_id])
                    connection.commit()
                result_message = "Succesfully created movie instance."
                return render(request, "add_movie.html",{'result_message':result_message})    

            except Exception as e:
                result_message = f"Unsuccessfull attempt with exception! {str(e)}"
                return render(request, "add_movie.html",{'result_message':result_message})
        else:
            result_message = "Unsuccessfull attempt! Invalid Input"
            return render(request, "add_movie.html",{'result_message':result_message})
    else:
        return render(request, "add_movie.html")

def add_predecessor(request):
    if active_user_type != "director":
        return redirect('/movie_app')
    if request.method == 'POST':
        movie_id = request.POST['movie_id']
        movie_id_predecessor = request.POST['movie_id_predecessor']

        exists_succ = False
        exists_pred = False

        #Check if both movies are directed by this director
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT EXISTS(SELECT 1 FROM directs WHERE username = %s AND movie_id = %s)",
                [active_username, movie_id])
            exists_succ = cursor.fetchone()[0]
            cursor.execute(
                "SELECT EXISTS(SELECT 1 FROM directs WHERE username = %s AND movie_id = %s)",
                [active_username, movie_id_predecessor])
            exists_pred = cursor.fetchone()[0]
        exist = exists_pred and exists_succ 

        if exist and movie_id_predecessor != movie_id :
            with connection.cursor() as cursor:
                cursor.execute("SELECT * "
                               "FROM predecessors "
                               "WHERE succeeds_movie_id = (%s) AND predecessor_movie_id = (%s);",
                               [movie_id_predecessor, movie_id]
                                )
                result = cursor.fetchone()
                connection.commit()
                if result is not None:
                    result_message = "Logical error, Reverse exists in the database!"
                    return render(request, "add_predecessor.html",{'result_message':result_message})
            try:
                with connection.cursor() as cursor:
                    cursor.execute("INSERT INTO predecessors (predecessor_movie_id,succeeds_movie_id) VALUES (%s, %s)",[movie_id_predecessor,movie_id])
                result_message = "Succesfully added predecessor."
                return render(request, "add_predecessor.html",{'result_message':result_message})
            except Exception as e:
                result_message = f"Unsuccessfull attempt! {str(e)}"
                return render(request, "add_predecessor.html",{'result_message':result_message})
        else:
            result_message = "Unsuccessfull attempt!"
            return render(request, "add_predecessor.html",{'result_message':result_message})

    else:
        return render(request, "add_predecessor.html")

def update_movie(request):
    if active_user_type != "director":
        return redirect('/movie_app')
    if request.method == 'POST':
        movie_id = request.POST['movie_id']
        new_movie_name = request.POST['new_movie_name']

        exists = False
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT EXISTS(SELECT 1 FROM directs WHERE username = %s AND movie_id = %s)",
                [active_username, movie_id]
            )
            exists = cursor.fetchone()[0]

        if exists:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "UPDATE movie SET movie_name = %s WHERE movie_id = %s",
                        [new_movie_name, movie_id]
                    )
                result_message = "Succesfully updated movie name."
                return render(request, "update_movie.html",{'result_message':result_message})
            except Exception as e:
                result_message = f"Unsuccessfull attempt!{str(e)}"
                return render(request, "update_movie.html",{'result_message':result_message})

        else:
            result_message = "Unsuccessfull attempt!"
            return render(request, "update_movie.html",{'result_message':result_message})
    else:
        return render(request, "update_movie.html")

# Audience User Functionalities
def audience_home(request):
    if active_user_type == "audience":
        return render(request,"audience_home.html")
    else:
        return redirect('/movie_app')    

def buy_ticket(request):
    if active_user_type != "audience":
        return redirect('/movie_app')
    if request.method == 'POST':
        session_id = request.POST['session_id']

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                "SELECT * FROM movie_session WHERE session_id = %s;",[session_id])
                exists_session = cursor.fetchone()
                connection.commit()
                if exists_session is None:
                    result_message = "No such session with given session_id."
                    return render(request, "buy_ticket.html",{'result_message':result_message})
                predecessor_movie_list = []
                cursor.execute("SELECT p.predecessor_movie_id " 
                                "FROM has_movie AS hm "
                                "JOIN movie AS m ON hm.movie_id = m.movie_id "   
                                "JOIN predecessors AS p ON p.succeeds_movie_id = m.movie_id " 
                                "WHERE hm.session_id = %s;", [session_id])
                predecessor_movie_list = cursor.fetchall()
                connection.commit()
                if len(predecessor_movie_list) == 0:
                    pm_list = []
                else:
                    predecessor_movie_list = convert(predecessor_movie_list)
                    pm_list =[]
                    for elm in predecessor_movie_list:
                        pm_list.append(elm[0])
                bought_movie_list =[]
                cursor.execute("SELECT hm.movie_id "
                                "FROM bought_tickets AS bt "
                                "JOIN has_movie AS hm ON hm.session_id = bt.session_id "
                                "WHERE bt.username = %s AND bt.session_id = %s;", [active_username, session_id]
                )
                bought_movie_list = cursor.fetchall()
                connection.commit()
                if len(bought_movie_list) == 0:
                    bt_list = []
                else:
                    bought_movie_list = convert(bought_movie_list)
                    bt_list =[]
                    for elm in bought_movie_list:
                        bt_list.append(elm[0])
                bt_list = set(bt_list)
                pm_list = set(pm_list)
                if not pm_list.issubset(bt_list):
                    result_message = "User should watch all predecessor movies of the associated movie with given session_id."
                    return render(request, "buy_ticket.html",{'result_message':result_message})
                cursor.execute("SELECT t.theater_capacity "
                                "FROM place AS p "
                                "JOIN occupience_info AS oi ON p.occupience_id = oi.occupience_id "
                                "JOIN theater AS t ON t.theater_id = oi.theater_id "
                                "WHERE p.session_id = %s", [session_id])
                capacity = int(cursor.fetchall()[0][0])
                connection.commit()
                cursor.execute("SELECT COUNT(*) "
                                "FROM bought_tickets AS bt "
                                "WHERE bt.session_id = %s "
                                "GROUP BY bt.session_id;", [session_id])
                result_current_seats = cursor.fetchall() 
                if len(result_current_seats) == 0:
                    current_seats = 0
                else:
                    current_seats = int(result_current_seats[0][0])
                if current_seats >= capacity:
                    result_message = "No more seats available for this session."
                    return render(request, "buy_ticket.html",{'result_message':result_message})
                cursor.execute("SELECT * "
                                "FROM bought_tickets as bt "
                                "WHERE bt.session_id = %s AND bt.username = %s", [session_id, active_username])
                has_bought = cursor.fetchone()
                if has_bought is not None:
                    result_message = "Already bought ticket for this session."
                    return render(request, "buy_ticket.html",{'result_message':result_message})

        except Exception as e:
            result_message = f"Unsuccessfull attempt!{str(e)}"
            return render(request, "buy_ticket.html",{'result_message':result_message})

        try:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO bought_tickets VALUES (%s, %s);", [active_username, session_id])
                result_message = "Succesfully bought ticket."
                return render(request, "buy_ticket.html",{'result_message':result_message})

        except Exception as e:
            result_message = f"Unsuccessfull attempt!{str(e)}"
            return render(request, "buy_ticket.html",{'result_message':result_message})

    else:
        return render(request, "buy_ticket.html")

def tickets(request):
    if active_user_type != "audience":
        return redirect('/movie_app')
    viewlist = []
    with connection.cursor() as cursor:
            cursor.execute("SELECT m.movie_id, m.movie_name, bt.session_id, r.rating, m.overall_rating "
                            "FROM movie AS m "
                            "JOIN has_movie AS hm ON hm.movie_id = m.movie_id "
                            "JOIN movie_session AS mo ON mo.session_id = hm.session_id "
                            "JOIN bought_tickets AS bt ON bt.session_id = mo.session_id "
                            "JOIN audience AS a ON a.username = bt.username "
                            "LEFT JOIN ratings AS r ON r.movie_id = m.movie_id "                         
                            "WHERE a.username = (%s);",
                            [active_username]
            )
            viewlist = cursor.fetchall()
            viewlist = convert(viewlist)
            connection.commit()
    viewlist_json = json.dumps(viewlist)
    return render(request, "tickets.html", {'viewlist_json':viewlist_json})

def list_movies(request):
    if active_user_type != "audience":
        return redirect('/movie_app')
    viewlist = []
    with connection.cursor() as cursor:
                cursor.execute("SELECT m.movie_id, m.movie_name, u.surname, rp.platform_name, oi.theater_id, oi.time1, oi.slot_number,  string_agg(p.predecessor_movie_id::text, ',') AS predecessors "
                               "FROM movie m "
                               "LEFT JOIN predecessors p ON m.movie_id = p.succeeds_movie_id "
                               "INNER JOIN directs d ON m.movie_id = d.movie_id "
                               "JOIN has_movie AS hm ON hm.movie_id = m.movie_id "
                               "JOIN place AS pl ON pl.session_id = hm.session_id "
                               "JOIN occupience_info AS oi ON oi.occupience_id = pl.occupience_id "
                               "JOIN director AS di ON di.username = d.username "
                               "JOIN user1 AS u ON u.username = di.username "
                               "JOIN registered AS reg ON reg.username = di.username "
                               "JOIN rating_platform AS rp ON rp.platform_id = reg.platform_id "
                               "GROUP BY m.movie_id, m.movie_name, u.surname, rp.platform_name, oi.theater_id, oi.time1, oi.slot_number;"
                )
                viewlist = cursor.fetchall()
                viewlist = convert(viewlist)
                viewlist = fix_time(viewlist, 5)
                connection.commit()
    viewlist_json = json.dumps(viewlist)
    return render(request, "list_movies.html", {'viewlist_json':viewlist_json})
    
def convert(viewlist):
    newlist = list()
    for e in viewlist:
        newlist.append(list(e))
    return newlist

def fix_time(viewlist, timeindex):
    for e in viewlist:
        e[timeindex] = e[timeindex].split(' ')[0]
    return viewlist
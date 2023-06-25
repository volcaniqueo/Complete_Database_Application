from django.urls import path

from . import views

urlpatterns = [
    path('', views.login_view, name='login'),

    # Database manager home page
    path("db_home/", views.db_home, name="db_home"),
    path("db_home/add_user/", views.add_user, name="add_user"),
    path("db_home/delete_audience/", views.delete_audience, name="delete_audience"),
    path("db_home/update_director/", views.update_director, name="update_director"),
    path("db_home/view_list/", views.view_list, name="view_list"),
    path("db_home/log_out/",views.log_out, name="db_log_out"),

    # Director home page
    path("director_home/", views.director_home, name="director_home"),
    path("director_home/add_movie/", views.add_movie, name="add_movie"),
    path("director_home/add_predecessor/", views.add_predecessor, name="add_predecessor"),
    path("director_home/update_movie/", views.update_movie, name="update_movie"),
    path("director_home/view_list/", views.view_list_director, name="view_list_director"),
    path("director_home/log_out/",views.log_out, name="director_log_out"),

    # Audience home page 
    path("audience_home/", views.audience_home, name="audience_home"),
    path("audience_home/buy_ticket/", views.buy_ticket, name="buy_ticket"),
    path("audience_home/tickets/", views.tickets, name="tickets"),
    path("audience_home/list_movies/", views.list_movies, name="list_movies"),
    path("audience_home/log_out/",views.log_out, name="audience_log_out"),

]
from django.urls import path
from . import views

app_name = 'exams'
urlpatterns = [
    path('', views.index, name='index'),
    path('config/', views.config, name='config'),
    path('add_exam/', views.add_exam, name='add_exam'),
    path('<int:exam_id>/', views.exam_page, name='exam_page'),
    path('<int:exam_id>/add_question', views.add_question, name='add_question'),
    path('<int:exam_id>/exam_result', views.exam_result, name='exam_result'),
    path('<int:exam_id>/delete_exam', views.delete_exam, name='delete_exam'),
    path('<int:exam_id>/<int:q_id>', views.q_page, name='q_page'),
    path('<int:exam_id>/<int:q_id>/delete_question', views.delete_question, name='delete_question'),
    path('<int:exam_id>/<int:q_id>/add_file', views.add_file, name='add_file'),
]
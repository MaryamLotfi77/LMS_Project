from django.urls import path
from . import views

urlpatterns = [

    path('assessments/', views.AssessmentListCreateView.as_view(), name='assessment-list-create'),
    path('assessments/<int:pk>/', views.AssessmentRetrieveUpdateDestroyView.as_view(), name='assessment-detail'),


    path('assessments/<int:assessment_pk>/questions/',
         views.QuestionListCreateView.as_view(),
         name='question-list-create'),
    path('assessments/<int:assessment_pk>/questions/<int:pk>/',
         views.QuestionRetrieveUpdateDestroyView.as_view(),
         name='question-detail'),
]
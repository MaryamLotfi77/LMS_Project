from rest_framework import generics
from .models import Assessment, Question
from .serializers import AssessmentSerializer, QuestionSerializer
from .permissions import IsAdminOrReadOnly
from django.shortcuts import get_object_or_404



# -------------------------------------------------------------------

class AssessmentListCreateView(generics.ListCreateAPIView):
    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer
    permission_classes = [IsAdminOrReadOnly]


class AssessmentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer
    permission_classes = [IsAdminOrReadOnly]


# -------------------------------------------------------------------

class QuestionListCreateView(generics.ListCreateAPIView):
    serializer_class = QuestionSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        assessment_pk = self.kwargs['assessment_pk']
        get_object_or_404(Assessment, pk=assessment_pk)
        return Question.objects.filter(assessment_id=assessment_pk)

    def perform_create(self, serializer):
        assessment_pk = self.kwargs['assessment_pk']
        assessment = get_object_or_404(Assessment, pk=assessment_pk)
        serializer.save(assessment=assessment)


class QuestionRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = QuestionSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        return Question.objects.all()

    def get_object(self):
        queryset = self.get_queryset()
        question = get_object_or_404(queryset, pk=self.kwargs['pk'])

        if 'assessment_pk' in self.kwargs:
            if question.assessment.pk != self.kwargs['assessment_pk']:
                # یا raises a different exception
                from rest_framework.exceptions import NotFound
                raise NotFound("Question not found in the specified assessment.")

        return question
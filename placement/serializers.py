
from rest_framework import serializers
from .models import Assessment, Question, Option

class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'text', 'is_correct']
        extra_kwargs = {
            'question': {'required': False}
        }



class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, required=False)

    class Meta:
        model = Question
        fields = [
            'id',
            'text',
            'question_type',
            'score_weight',
            'correct_answer_text',
            'options'  # فیلد تودرتو
        ]
        extra_kwargs = {'assessment': {'required': False}}

    def create(self, validated_data):
        options_data = validated_data.pop('options', [])
        question = Question.objects.create(**validated_data)

        for option_data in options_data:
            Option.objects.create(question=question, **option_data)

        return question

    def update(self, instance, validated_data):
        options_data = validated_data.pop('options', [])

        instance.text = validated_data.get('text', instance.text)
        instance.question_type = validated_data.get('question_type', instance.question_type)
        instance.score_weight = validated_data.get('score_weight', instance.score_weight)
        instance.correct_answer_text = validated_data.get('correct_answer_text', instance.correct_answer_text)
        instance.save()

        if options_data:
            instance.options.all().delete()
            for option_data in options_data:
                Option.objects.create(question=instance, **option_data)

        return instance



class AssessmentSerializer(serializers.ModelSerializer):
    questions_count = serializers.IntegerField(
        source='questions.count',
        read_only=True,
        label="تعداد سؤالات"
    )

    class Meta:
        model = Assessment
        fields = [
            'id',
            'title',
            'description',
            'target_level',
            'passing_score',
            'duration_minutes',
            'is_active',
            'questions_count'
        ]
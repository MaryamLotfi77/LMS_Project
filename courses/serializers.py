from rest_framework import serializers
from .models import Category, Course, Level, ClassSession
from django.core.exceptions import ValidationError


# ----------------------------------------------------------------------

class CategorySerializer(serializers.ModelSerializer):

    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'children', 'level', 'tree_id']
        read_only_fields = ['level', 'tree_id']

    def get_children(self, obj):
        if obj.children.exists():
            return CategorySerializer(obj.children.all(), many=True).data
        return None


# ----------------------------------------------------------------------

class CourseSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'category', 'category_name']
        read_only_fields = ['category_name']


# ----------------------------------------------------------------------

class LevelSerializer(serializers.ModelSerializer):

    course_title = serializers.CharField(source='course.title', read_only=True)
    prereq_level_number = serializers.IntegerField(source='prereq_level.level_number', read_only=True)

    def validate(self, data):
        if self.instance is not None:
            instance = self.instance
            for attr, value in data.items():
                setattr(instance, attr, value)
        else:
            instance = Level(**data)

        try:
            instance.full_clean()
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)
        return data


    class Meta:
        model = Level
        fields = [
            'id',
            'course', 'course_title',
            'level_number',
            'title',
            'prereq_level', 'prereq_level_number'
        ]
        read_only_fields = ['course_title', 'prereq_level_number']


# ----------------------------------------------------------------------

class ClassSessionSerializer(serializers.ModelSerializer):
    level_title = serializers.CharField(source='level.title', read_only=True)
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)

    current_enrollment_count = serializers.IntegerField(read_only=True)
    is_full = serializers.BooleanField(read_only=True)

    class Meta:
        model = ClassSession
        fields = [
            'id', 'level', 'level_title', 'instructor', 'instructor_name',
            'capacity', 'start_date', 'current_enrollment_count', 'is_full',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'current_enrollment_count', 'is_full', 'created_at', 'updated_at'
        ]



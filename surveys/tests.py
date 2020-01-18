from django.test import TestCase
from .forms import AnswerForm, AnswerFormSet
from .models import Question, Survey, LEVEL_CHOICES, Answer
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError


class SurveyModelTests(TestCase):
    @staticmethod
    def save_model_throws_value_error(form):
        try:
            form.save()
        except ValueError:
            return True
        return False

    def test_create(self):
        survey = Survey(name='test_13')
        self.assertFalse(self.save_model_throws_value_error(survey))


class QuestionModelTests(TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.survey = Survey(name='tt')

    def setUp(self):
        self.survey.save()

    def test_create(self):
        question = Question(level=0, survey=self.survey, question="Does this work?")
        question.save()


class AnswerModelTests(TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.survey = Survey(name='test_survey_6')
        self.questions = [Question(level=i, survey=self.survey, question="Does this work?") for i in range(10)]

    def setUp(self):
        self.survey.save()
        for q in self.questions:
            q.save()
        self.test_user = get_user_model().objects.create_user(
            email='andreas.milants@gmail.com',
            password='thisisapassword'
        )
        self.test_user.save()

    def test_create_valid(self):
        for ans, q in zip([0, -50, 50], self.questions):
            answer = Answer(question=q, answer=ans, user=self.test_user)
            answer.save()

    def test_create_invalid_answer(self):
        for ans, q in zip([-51, 51], self.questions):
            answer = Answer(question=q, answer=ans, user=self.test_user)
            self.assertRaises(IntegrityError, answer.save())

        def create_answer():
            Answer(question=self.questions[0], answer=ans, user=self.test_user)

        for ans, q in zip(['a'], self.questions):
            self.assertRaises(ValueError, create_answer())

        def create_answer_2():
            Answer(question=self.questions[0], answer=None, user=self.test_user)

        self.assertRaises(IntegrityError, create_answer_2())

# TODO form testing, linking sections

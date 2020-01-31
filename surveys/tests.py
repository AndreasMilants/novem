from django.test import TestCase
from .forms import AnswerForm, AnswerFormSet
from .models import Question, Survey, LEVEL_CHOICES, Answer


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
    def setUp(self):
        self.survey = Survey(name='tt')
        self.survey.save()

    def test_create(self):
        question = Question(level=0, survey=self.survey, question="Does this work?")
        question.save()


class AnswerFormTests(TestCase):
    def setUp(self):
        self.survey = Survey(name='test_survey')
        self.questions = [Question(level=i, survey=self.survey, question="Does this work?") for i in range(10)]
        self.survey.save()
        for q in self.questions:
            q.save()

    def test_valid_answer(self):
        answer_set = [0, -50, 50]
        for answer in answer_set:
            form = AnswerForm(data={'question': self.questions[0], 'answer': answer},
                              initial={'question': self.questions[0].id, 'answer': 0})
            self.assertTrue(form.is_valid())

    def test_invalid(self):
        answer_set = ['a', -51, 51]
        for answer in answer_set:
            form = AnswerForm(data={'question': self.questions[0], 'answer': answer},
                              initial={'question': self.questions[0].id, 'answer': 0})
            self.assertFalse(form.is_valid())

    def test_save(self):
        answer = 50
        form = AnswerForm(data={'question': self.questions[0], 'answer': answer},
                          initial={'question': self.questions[0].id, 'answer': 0})
        if form.is_valid():
            model = form.save(commit=False)
            self.assertEqual(model.answer, answer)
        else:
            self.assertTrue(False)


# TODO add tests for statistics
# TODO add tests for section administrator pages

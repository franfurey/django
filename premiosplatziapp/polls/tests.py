from django.test import TestCase
from django.utils import timezone
import datetime
from .models import Question, Choice
from django.urls.base import reverse

# Create your tests here.

class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_questions(self):
        """was_published_recently returns False for questions whose pub_date is in the future"""
        time = timezone.now() + datetime.timedelta(days = 30)
        future_question = Question(question_text = "Quien es el mejor CD de Platzi?" ,pub_date = time)
        self.assertIs(future_question.was_published_recently(), False)   

    def test_was_published_recently_with_past_questions(self):
        """was_published_recently returns False for questions whose pub_date are in the past"""
        time = timezone.now() - timezone.timedelta(days = 30)
        past_question = Question(question_text = "Quien es el mejor CD de Platzi?" ,pub_date = time)
        self.assertIs(past_question.was_published_recently(), False)


def create_question(question_text, days):
    """
    Create a question with the given "question_text", and published the given
    number of days offset to now (negative for questions published in the past,
    positive for questions that have yet to be published)
    """
    time = timezone.now() + datetime.timedelta(days = days)
    return Question.objects.create(question_text = question_text, pub_date = time)

def create_choices(choices_text):
    """
    Create a question with the given "question_text", and published the given
    number of days offset to now (negative for questions published in the past,
    positive for questions that have yet to be published)
    """
    return Choice.objects.create(choices_text = choices_text)


class QuestionIndeViewTests(TestCase):

    def test_no_questions(self):
        """If no question exist, an appropiate message is displayed"""
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context["latest_question_list"],[])


    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on the index page.
        """
        create_question("Future question", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])


    def test_past_questions(self):
        """
        Questions with a pub_date in the past are displayed on the index page. 
        """
        question = create_question("Past question", days =-30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(response.context['latest_question_list'], [question])
        # self.assertContains(response, "No polls are available")

    def test_future_question_and_past_question(self):
        """
        Even if both past and future question exist, only past questions are displayed
        """
        past_question = create_question(question_text= "Past Question", days = -30)
        future_question = create_question(question_text= "Future Question", days = 30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["latest_question_list"],
            [past_question]
        )
        

    def test_two_past_questions(self):
        """
        The questionns index page may display multiple questions. 
        """
        past_question1 = create_question(question_text= "Past Question 1", days = -30)
        past_question2 = create_question(question_text= "Future Question 2", days = -40)    
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["latest_question_list"],
            [past_question1, past_question2]
        )

    def test_two_future_questions(self):
        """
        
        """
        future_question1 = create_question(question_text= "future Question 1", days = 30)
        future_question2 = create_question(question_text= "Future Question 2", days = 40)          
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["latest_question_list"],
            []
        )


class QuestionDetailViewTests(TestCase):

    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 error not found
        """
        future_question = create_question(question_text="Future Question", days = 30)
        url = reverse("polls:detail", args= (future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        display the question's text
        """
        past_question = create_question(question_text="past Question", days = -30)
        url = reverse("polls:detail", args= (past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)



class QuestionResultViewTest(TestCase):

    def cannot_create_questions_witout_choices(self):
        """
        Any user can create a question without at least 
        a couple of possibles choices
        """
        question = create_question(question_text="Question Test", days = -2)
        choices = create_choices(choices_text="[1, 2, 3]")
        response = self.client.get(reverse("polls:results"))
        self.assertContains(response, [question.question_text, choices.choice_text])
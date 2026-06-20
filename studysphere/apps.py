from django.apps import AppConfig


# Cloudinary is used for media storage (book covers, profile pics, etc.)
# Make sure to set up your Cloudinary credentials in .env and configure settings.py accordingly.

# Setup for Celery (for background tasks like notifications) is also included, but you can start without it and add it later if needed.
# For Celery, you'll need to install Redis and run a Redis server locally, and then start the Celery worker with:
# celery -A studysphere worker --loglevel=info
# You can define periodic tasks in studysphere/tasks.py and configure them in settings.py using Celery Beat.
# For notifications, there has to be a way to make it send outside the app. You can use Django's built-in email backend for sending notifications, or integrate with a service like Twilio for SMS notifications.

# For exams and quizzes, It should be able to generate quizzes based on the uploaded materials. You can use a library like Quizlet API or create your own quiz generation logic based on the content of the uploaded books.
# Or you can allow users to create their own quizzes manually, and then share them with others. This would involve creating a Quiz model, a QuizForm for creating quizzes, and views/templates for taking and sharing quizzes.
# Or use AI to generate quizzes based on the content of the uploaded materials. This would involve integrating with an AI service like OpenAI's GPT-3 to analyze the content of the books and generate quiz questions based on that content.

# Integrate Tracking of PDFs read, so users can kknow where they left off in a book. This would involve creating a model to track user progress for each book, and updating that progress as they read through the PDF. You can use JavaScript to track the user's scroll position in the PDF viewer and send that information back to the server to update their progress.

# Integrate summary generation for uploaded materials. This would involve using an AI service like OpenAI's GPT-3 to analyze the content of the uploaded books and generate summaries for them. You can then display these summaries on the book detail page to give users a quick overview of the content before they decide to read it.

class StudysphereConfig(AppConfig):
    name = 'studysphere'

# chatbot/utils.py
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import re

# Download required NLTK data
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')


class ChatBotNLP:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))

        # Common patterns for show recommendations
        self.patterns = {
            'greeting': r'\b(hi|hello|hey|greetings)\b',
            'farewell': r'\b(bye|goodbye|see you|later)\b',
            'gratitude': r'\b(thanks|thank you|appreciate)\b',
            'recommendation': r'\b(recommend|suggest|show me|what|looking for)\b',
            'genre': r'\b(action|comedy|drama|thriller|sci-fi|horror|romance)\b',
            'preference': r'\b(like|love|enjoy|prefer|fan of)\b',
            'rating': r'\b(best|top|highest rated|popular)\b'
        }

        # Response templates
        self.responses = {
            'greeting': [
                "Hello! How can I help you find your next favorite show?",
                "Hi there! Looking for show recommendations?",
                "Welcome! What kind of shows do you enjoy?"
            ],
            'farewell': [
                "Goodbye! Hope you enjoy watching!",
                "See you later! Don't forget to check out those recommendations!",
                "Bye! Come back if you need more show suggestions!"
            ],
            'gratitude': [
                "You're welcome! Let me know if you need more recommendations!",
                "Glad I could help! Enjoy watching!",
                "No problem! Feel free to ask for more suggestions!"
            ],
            'general': [
                "Based on what you've told me, here are some shows you might enjoy:",
                "I think you'd really like these shows:",
                "Here are some recommendations that match your interests:"
            ]
        }

    def extract_genres(self, text):
        """Extract genre preferences from text"""
        genres = re.findall(self.patterns['genre'], text.lower())
        return list(set(genres))

    def extract_intent(self, text):
        """Determine the user's intent from their message"""
        intents = []
        for intent, pattern in self.patterns.items():
            if re.search(pattern, text.lower()):
                intents.append(intent)
        return intents

    def generate_response(self, text, shows=None):
        """Generate an appropriate response based on user input"""
        intents = self.extract_intent(text)
        genres = self.extract_genres(text)

        # Handle greetings
        if 'greeting' in intents:
            return {
                'message': nltk.random.choice(self.responses['greeting']),
                'requires_recommendation': False
            }

        # Handle farewells
        if 'farewell' in intents:
            return {
                'message': nltk.random.choice(self.responses['farewell']),
                'requires_recommendation': False
            }

        # Handle gratitude
        if 'gratitude' in intents:
            return {
                'message': nltk.random.choice(self.responses['gratitude']),
                'requires_recommendation': False
            }

        # Handle show recommendations
        if shows:
            response = nltk.random.choice(self.responses['general'])
            show_titles = [show.title for show in shows]
            if genres:
                response += f"\nI found these {', '.join(genres)} shows for you: {', '.join(show_titles)}"
            else:
                response += f"\nHere are some shows you might enjoy: {', '.join(show_titles)}"

            return {
                'message': response,
                'requires_recommendation': True
            }

        return {
            'message': "I'm not sure what kind of shows you're looking for. Could you tell me what genres you enjoy?",
            'requires_recommendation': False
        }
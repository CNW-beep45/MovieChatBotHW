import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import re
import random

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')


class EnhancedChatBotNLP:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))

        # Extended patterns for show recommendations
        self.patterns = {
            'greeting': r'\b(hi|hello|hey|greetings|howdy|good morning|good afternoon|good evening)\b',
            'farewell': r'\b(bye|goodbye|see you|later|farewell|thanks bye|cya)\b',
            'gratitude': r'\b(thanks|thank you|appreciate|grateful|awesome|cool|nice)\b',
            'recommendation': r'\b(recommend|suggest|show me|what|looking for|find|search|want to watch)\b',
            'genre': r'\b(action|comedy|drama|thriller|sci-fi|science fiction|horror|romance|documentary|animation|family|fantasy|adventure|crime|mystery|western|history|war|biography|music)\b',
            'preference': r'\b(like|love|enjoy|prefer|fan of|into|favorite)\b',
            'rating': r'\b(best|top|highest rated|popular|good|great|excellent|awesome)\b',
            'recency': r'\b(new|recent|latest|this year|2024|2023|current)\b',
            'actor': r'\b(starring|actor|actress|cast|with)\b',
            'director': r'\b(directed by|director|filmmaker)\b',
            'negative': r'\b(not|don\'t|dislike|hate|boring|bad)\b',
            'question': r'\b(who|what|when|where|why|how)\b',
            'help': r'\b(help|assist|guide|explain|confused)\b'
        }

        # Extended response templates
        self.responses = {
            'greeting': [
                "Hello! How can I help you find your next favorite movie?",
                "Hi there! Looking for movie recommendations?",
                "Welcome! What kind of movies do you enjoy watching?",
                "Hey! I'm your movie recommendation assistant. What are you in the mood for?"
            ],
            'farewell': [
                "Goodbye! Hope you enjoy watching!",
                "See you later! Don't forget to check out those recommendations!",
                "Bye! Come back if you need more movie suggestions!",
                "Take care! Enjoy your movie night!"
            ],
            'gratitude': [
                "You're welcome! Let me know if you need more recommendations!",
                "Glad I could help! Enjoy watching!",
                "No problem! Feel free to ask for more suggestions!",
                "Happy to help! Let me know how you like the movies!"
            ],
            'help': [
                "I can help you find movies based on genre, actors, directors, or ratings. Just tell me what you're looking for!",
                "You can ask me for movie recommendations by mentioning genres you like, actors you enjoy, or even the type of mood you're in.",
                "Need movie suggestions? Just tell me what genres you enjoy or ask for something like 'recommend a good sci-fi movie'."
            ],
            'general': [
                "Based on what you've told me, here are some movies you might enjoy:",
                "I think you'd really like these movies:",
                "Here are some recommendations that match your interests:",
                "Check out these movies that fit what you're looking for:"
            ],
            'no_genre': [
                "I'm not sure what kind of movies you're looking for. Could you tell me what genres you enjoy?",
                "To help you better, could you share what types of movies you prefer?",
                "What genres or types of movies are you interested in?",
                "Tell me about your favorite movies or genres, and I can suggest similar ones!"
            ],
            'negative_response': [
                "I understand those aren't your favorites. What kinds of movies do you prefer instead?",
                "Got it - you're not into that. Tell me what you do enjoy watching!",
                "Thanks for letting me know what you don't like. What genres do you usually enjoy?"
            ]
        }

        # Map common genre variations to standard genres
        self.genre_mapping = {
            'sci-fi': 'science fiction',
            'scifi': 'science fiction',
            'rom-com': 'romantic comedy',
            'romcom': 'romantic comedy',
            'romantic comedy': 'romance',
            'docu': 'documentary',
            'docs': 'documentary',
            'true story': 'biography',
            'biographical': 'biography'
        }

        # Common actors and directors for enhanced recognition
        # This could be expanded or connected to TMDB data
        self.actors = [
            'tom hanks', 'jennifer lawrence', 'leonardo dicaprio', 'meryl streep',
            'denzel washington', 'scarlett johansson', 'brad pitt', 'viola davis',
            'robert downey jr', 'emma stone', 'will smith', 'cate blanchett'
        ]

        self.directors = [
            'steven spielberg', 'christopher nolan', 'martin scorsese', 'quentin tarantino',
            'greta gerwig', 'james cameron', 'ava duvernay', 'denis villeneuve',
            'jordan peele', 'chloe zhao', 'ryan coogler', 'taika waititi'
        ]

    def extract_genres(self, text):
        """Extract genre preferences from text with improved handling"""
        # Convert to lowercase for better matching
        text_lower = text.lower()

        # First try to match standard genres
        genres = re.findall(self.patterns['genre'], text_lower)

        # Check for genre variations and map to standard genres
        for variant, standard in self.genre_mapping.items():
            if variant in text_lower and standard not in genres:
                genres.append(standard)

        # Remove duplicates while preserving order
        return list(dict.fromkeys(genres))

    def extract_actors(self, text):
        """Extract actor names from text"""
        text_lower = text.lower()
        found_actors = []

        for actor in self.actors:
            if actor in text_lower:
                found_actors.append(actor)

        # Could be enhanced with NER (Named Entity Recognition)
        return found_actors

    def extract_directors(self, text):
        """Extract director names from text"""
        text_lower = text.lower()
        found_directors = []

        for director in self.directors:
            if director in text_lower:
                found_directors.append(director)

        return found_directors

    def detect_sentiment(self, text):
        """Detect if the user has positive or negative sentiment about genres"""
        text_lower = text.lower()

        has_negative = bool(re.search(self.patterns['negative'], text_lower))
        has_preference = bool(re.search(self.patterns['preference'], text_lower))

        if has_negative and has_preference:
            # Look for genres that user might not like
            genres = self.extract_genres(text)
            disliked_genres = []

            # Simple approach - check if negative word is near genre word
            for genre in genres:
                # Check if negative word is within a few words of genre
                genre_pos = text_lower.find(genre)
                if genre_pos > -1:
                    context = text_lower[max(0, genre_pos - 20):min(len(text_lower), genre_pos + 20)]
                    if re.search(self.patterns['negative'], context):
                        disliked_genres.append(genre)

            return {
                'negative': has_negative,
                'disliked_genres': disliked_genres,
                'liked_genres': [g for g in genres if g not in disliked_genres]
            }

        return {
            'negative': has_negative,
            'disliked_genres': [],
            'liked_genres': self.extract_genres(text) if has_preference else []
        }

    def extract_intent(self, text):
        """Determine the user's intent from their message with improved accuracy"""
        text_lower = text.lower()
        intents = []

        for intent, pattern in self.patterns.items():
            if re.search(pattern, text_lower):
                intents.append(intent)

        # Handle special cases
        if 'recommendation' in intents and 'question' in intents:
            # User is likely asking for a recommendation
            intents.append('asking_recommendation')

        if 'rating' in intents and 'recency' in intents:
            # User wants recent, well-rated content
            intents.append('recent_top_rated')

        return intents

    def generate_response(self, text, shows=None):
        """Generate an appropriate response based on user input"""
        intents = self.extract_intent(text)
        genres = self.extract_genres(text)

        print(f"Generating response for intents: {intents}, genres: {genres}")

        # Handle greetings
        if 'greeting' in intents:
            return {
                'message': random.choice(self.responses['greeting']),
                'requires_recommendation': False
            }

        # Handle farewells
        if 'farewell' in intents:
            return {
                'message': random.choice(self.responses['farewell']),
                'requires_recommendation': False
            }

        # Handle gratitude
        if 'gratitude' in intents and len(intents) == 1:  # Only gratitude
            return {
                'message': random.choice(self.responses['gratitude']),
                'requires_recommendation': False
            }

        # When we have shows to recommend
        if shows and len(shows) > 0:
            # Generate different response based on detected genres
            response = random.choice(self.responses['general'])
            show_titles = [show.title for show in shows]

            if genres:
                response += f"\nI found these {', '.join(genres)} shows for you: {', '.join(show_titles)}"
            else:
                response += f"\nHere are some shows you might enjoy: {', '.join(show_titles)}"

            return {
                'message': response,
                'requires_recommendation': True
            }

        # Check for genre keyword but no specific genre mentioned
        if 'genre' in intents and not genres:
            return {
                'message': "I'd love to recommend movies in your favorite genre. Could you tell me what genres you enjoy?",
                'requires_recommendation': False
            }

        # Check for recommendation intent
        if 'recommendation' in intents:
            if not genres:
                return {
                    'message': "I can suggest some great movies for you. What genres do you usually enjoy watching?",
                    'requires_recommendation': False
                }

        # Default response for when we can't determine the intent clearly
        return {
            'message': "I'm not sure what kind of movies you're looking for. Could you tell me what genres you enjoy?",
            'requires_recommendation': False
        }
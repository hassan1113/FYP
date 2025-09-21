import random
from datetime import datetime, timedelta

class SuggestionEngine:
    def __init__(self):
        self.suggestions_db = {
            'Happy': {
                'activities': [
                    "Share your happiness! Call a friend or family member",
                    "Channel this energy into a creative project",
                    "Go for a walk in nature to maintain this positive mood",
                    "Write down what made you happy today in a gratitude journal"
                ],
                'wellness': [
                    "Practice gratitude meditation to amplify positive feelings",
                    "Do some light stretching or yoga to maintain good energy"
                ],
                'productivity': [
                    "This is a great time to tackle challenging tasks",
                    "Use this positive energy to organize your workspace"
                ]
            },
            'Sad': {
                'activities': [
                    "Listen to uplifting music or your favorite comfort playlist",
                    "Watch a funny movie or comedy show",
                    "Call someone you trust and talk about your feelings",
                    "Take a warm bath or shower to comfort yourself"
                ],
                'wellness': [
                    "Try deep breathing exercises: 4 counts in, 6 counts out",
                    "Practice self-compassion meditation",
                    "Write your feelings in a journal without judgment"
                ],
                'social': [
                    "Reach out to a supportive friend or family member",
                    "Consider joining an online support community"
                ]
            },
            'Angry': {
                'activities': [
                    "Go for a vigorous walk or run to release tension",
                    "Try punching a pillow or doing jumping jacks",
                    "Listen to heavy music that matches your energy, then transition to calmer tunes"
                ],
                'wellness': [
                    "Practice the 4-7-8 breathing technique",
                    "Try progressive muscle relaxation",
                    "Count to 10 slowly before reacting to anything"
                ],
                'productivity': [
                    "Clean or organize something - channel anger into productivity",
                    "Avoid making important decisions right now"
                ]
            },
            'Neutral': {
                'activities': [
                    "This is a good time to try something new",
                    "Explore a new hobby or interest",
                    "Organize your goals and plans for the week"
                ],
                'wellness': [
                    "Practice mindfulness meditation",
                    "Do some gentle stretching"
                ],
                'productivity': [
                    "Perfect time for routine tasks and planning",
                    "Review your recent achievements and set new goals"
                ]
            },
            'Fear': {
                'activities': [
                    "Write down your specific fears and challenge them with facts",
                    "Watch a comforting movie or show you've seen before",
                    "Call a trusted friend who helps you feel safe"
                ],
                'wellness': [
                    "Try box breathing: 4 counts in, hold 4, out 4, hold 4",
                    "Practice grounding: name 5 things you can see, 4 you can touch, 3 you can hear",
                    "Progressive muscle relaxation from head to toe"
                ],
                'productivity': [
                    "Break tasks into very small, manageable steps",
                    "Set a timer for just 5 minutes of work on something simple"
                ]
            },
            'Disgust': {
                'activities': [
                    "Clean or organize your immediate environment",
                    "Take a shower or bath with refreshing scents",
                    "Change your scenery - go to a different room or outside"
                ],
                'wellness': [
                    "Practice acceptance meditation",
                    "Focus on pleasant sensory experiences (nice smells, textures)"
                ],
                'productivity': [
                    "Work on tasks requiring analytical thinking",
                    "Channel the energy into constructive criticism or reviews"
                ]
            },
            'Surprise': {
                'activities': [
                    "Journal about what surprised you and what you learned",
                    "Share your experience with someone you trust",
                    "Use this energy to try something new today"
                ],
                'wellness': [
                    "Take a few deep breaths to center yourself",
                    "Practice mindfulness to fully process the surprise"
                ],
                'productivity': [
                    "Brainstorm creative solutions to problems",
                    "Use this alertness for learning something new"
                ]
            }
        }
        
        self.quotes = {
            'Happy': [
                "Keep shining bright! Your positive energy is contagious.",
                "Happiness is not a destination, it's a way of travel.",
                "Your smile is your superpower today!"
            ],
            'Sad': [
                "It's okay to not be okay. This feeling will pass.",
                "You are stronger than you think, and this too shall pass.",
                "Every storm runs out of rain. Better days are coming."
            ],
            'Angry': [
                "Take a deep breath. You have the power to choose your response.",
                "Anger is like a storm - intense but temporary.",
                "Your peace of mind is worth more than proving you're right."
            ],
            'Fear': [
                "Courage is feeling fear and doing it anyway.",
                "This moment is just one page in your story, not the whole book.",
                "You've overcome difficult things before, and you can do it again."
            ],
            'Neutral': [
                "Today is full of possibilities waiting to be discovered.",
                "Sometimes the middle ground is where wisdom lives.",
                "Balance gives you the foundation to build anything."
            ],
            'Disgust': [
                "Your reactions are information, not commands.",
                "You can choose which thoughts to focus on.",
                "This feeling will pass, just like clouds in the sky."
            ],
            'Surprise': [
                "Life's surprises often lead to the greatest discoveries.",
                "The unexpected moments often teach us the most.",
                "Embrace the unknown - that's where growth happens."
            ]
        }
    
    def get_suggestions(self, emotion, context=None, previous_suggestions=None):
        if emotion not in self.suggestions_db:
            emotion = 'Neutral'
        
        emotion_suggestions = self.suggestions_db[emotion]
        suggestions = []
        
        # Get suggestions from each category
        for category, suggestions_list in emotion_suggestions.items():
            suggestion = random.choice(suggestions_list)
            suggestions.append({
                'type': category,
                'content': suggestion,
                'emotion': emotion
            })
        
        return suggestions
    
    def get_personalized_quote(self, emotion):
        if emotion not in self.quotes:
            emotion = 'Neutral'
        
        return random.choice(self.quotes[emotion])
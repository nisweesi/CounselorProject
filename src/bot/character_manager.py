def select_character():
    print("\nSelect Bot's Character:")
    print("1. Optimistic")
    print("2. Neutral")
    print("3. Pessimistic")
    while True:
        try:
            choice = input("Enter choice (1-3): ")
            return {
                '1': 'optimistic',
                '2': 'neutral',
                '3': 'pessimistic'
            }[choice]
        except KeyError:
            print("Invalid choice. Please enter 1, 2, or 3.")

def get_personality_tone(character_type):
    return {
        "pessimistic": "realistic but not overly negative",
        "optimistic": "positive and encouraging",
        "neutral": "balanced and objective"
    }[character_type]

class Personalizer:
    def __init__(self, personality):
        self.preferences = {}

    def add_preference(self, category, preference):

        if category in self.preferences:
            self.preferences[category].append(preference)
        else:
            self.preferences[category] = [preference]

    def remove_preference(self, category):
        self.preferences.pop(category)

    def modify_preference(self, category, preference):
        self.preferences.update(category, preference)


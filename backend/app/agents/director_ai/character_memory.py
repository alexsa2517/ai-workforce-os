class CharacterMemory:

    def __init__(self):
        self.characters = {}


    def add_character(self,name,data):
        self.characters[name]=data


    def get_character(self,name):
        return self.characters.get(name)

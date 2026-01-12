# NPC entity
class NPC:
    def __init__(self, name, age, location, profession, traits, childhood_backstory, adult_backstory):
        self.name = name
        self.age = age
        self.location = location
        self.profession = profession
        self.traits = traits
        self.childhood_backstory = childhood_backstory
        self.adult_backstory = adult_backstory
    
    def to_prompt_text(self):
        """Format NPC information as a single text block for LLM input."""
        return f"""Character Profile: {self.name}

Age: {self.age}
Location: {self.location}
Profession: {self.profession}
Traits: {', '.join(self.traits) if isinstance(self.traits, list) else self.traits}

Childhood Backstory:
{self.childhood_backstory}

Adult Backstory:
{self.adult_backstory}"""

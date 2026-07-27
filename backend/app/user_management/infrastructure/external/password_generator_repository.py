from user_management.application.services.password_generator_service import IPasswordGeneratorService
import random

class PasswordGeneratorRepository(IPasswordGeneratorService):
    ADJECTIVES = ["Blue", "Golden", "Silver", "Bright", "Smart", ...]
    NOUNS = ["Mountain", "River", "Eagle", "Tiger", "Forest", ...]
    @staticmethod
    def generate_password() -> str:
        adjective = random.choice(PasswordGeneratorRepository.ADJECTIVES)
        noun = random.choice(PasswordGeneratorRepository.NOUNS)
        number = random.randint(1000, 9999)
        symbol = random.choice("!@#$%^&*")
        
        return f"{adjective}{noun}{number}{symbol}"
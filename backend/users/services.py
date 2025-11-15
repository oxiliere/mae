from uuid import UUID
from django.db import transaction
from users.models import User



class UserService:
    
    def get_user(self, user_id: UUID) -> User:
        return User.objects.get(id=user_id)


from password_strength import PasswordStats


PASSWORD_ENTROPY_BITS = 0.75 # TODO: add this settings

def is_strong_password(password):
    stats = PasswordStats(password)
    return stats.strength() >= PASSWORD_ENTROPY_BITS

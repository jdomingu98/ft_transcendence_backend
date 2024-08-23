def generate_user_mock(name, email, password, repeat_password):
    return {
        "username": name,
        "email": email,
        "password": password,
        "repeat_password": repeat_password,
    }

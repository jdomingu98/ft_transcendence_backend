python manage.py migrate

# Generate private and public keys
ssh-keygen -t rsa -b 2048 -m PEM -f "$JWT_PRIVATE_KEY_PATH" -N "$JWT_PRIVATE_KEY_PASSWORD"

# Run the Django app
python manage.py runserver 0.0.0.0:8000
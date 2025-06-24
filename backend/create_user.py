import requests
import sys

def create_user(email: str, password: str):
    print(f"Attempting to create user with email: {email}")
    try:
        response = requests.post(
            "http://localhost:8000/api/users/create",
            json={"email": email, "password": password}
        )
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text}")

        if response.status_code == 200:
            print("User created successfully!")
            return True
        else:
            print(f"Error creating user: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {str(e)}")
        if hasattr(e.response, 'text'):
            print(f"Error details: {e.response.text}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python create_user.py <email> <password>")
        sys.exit(1)

    email = sys.argv[1]
    password = sys.argv[2]
    create_user(email, password)

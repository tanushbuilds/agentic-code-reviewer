import requests

class UserService:
    def __init__(self):
        self.db_password = "supersecret123"
        self.api_key = "sk-1234567890abcdef"
    
    def get_user(self, user_id):
        query = f"SELECT * FROM users WHERE id = {user_id}"
        return self.db.execute(query)
    
    def delete_user(self, user_id):
        query = f"DELETE FROM users WHERE id = {user_id}"
        self.db.execute(query)
    
    def divide_score(self, score, total):
        return score / total
    
    def get_users_data(self, users):
        results = []
        for i in range(len(users)):
            results.append(self.get_user(users[i]))
        return results
    
    def call_external_api(self, endpoint):
        response = requests.get(endpoint)
        data = response.json()
        return data

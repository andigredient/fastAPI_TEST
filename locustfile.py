from locust import HttpUser, task, between
import random
import string

class LinkUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        self.test_code = ''.join(random.choices(string.ascii_lowercase, k=6))
        self.client.post("/links/shorten", json={
            "original_url": f"https://test.com/{self.test_code}",
            "custom_alias": self.test_code
        })
        print(f"тестовая ссылка: {self.test_code}")
    
    @task(3)
    def create_link(self):
        url = f"https://test{random.randint(1,10000)}.com"
        self.client.post("/links/shorten", json={"original_url": url})
    
    @task(1)
    def redirect(self):
        with self.client.get(f"/{self.test_code}", 
                            allow_redirects=False, 
                            catch_response=True) as response:
            if response.status_code in [302, 307]:
                response.success()
            else:
                response.failure(f"ошибка: {response.status_code}")
    
    @task(1)
    def get_stats(self):
        self.client.get(f"/links/{self.test_code}/stats")
# services/llm/load_balancer.py

class LoadBalancer:

    def __init__(self):
        self.servers = ["llm1", "llm2"]
        self.current = 0

    def get_server(self):
        server = self.servers[self.current]
        self.current = (self.current + 1) % len(self.servers)
        return server

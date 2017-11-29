from q_learning import QAgent

spec = {
    "name":"QAgent",
    "source":"https://raw.githubusercontent.com/FirefoxMetzger/mastersThesis/master/RLUnit/worker/agents/QAgent.py",
    "num_trials":10
}

class Agent(QAgent):
    def __init__(self):
        super(Agent, self).__init__()
        
        self.alpha = 0.4
        self.gamma = 0.5
        
        self = QAgent()
        
    def destroy(self):
        self = QAgent()

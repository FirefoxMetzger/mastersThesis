from q_learning import QAgent

class Agent(QAgent):
    def __init__(self):
        super(Agent, self).__init__()
        
        self.alpha = 0.4
        self.gamma = 0.5
        
        self = QAgent()
        
    def destroy(self):
        self = QAgent()

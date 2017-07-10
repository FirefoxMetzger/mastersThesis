import json

class EpisodeComplete(object):
    experiment_id = 0
    episode_number = 0
    
    def __init__(self, j):
        self.__dict__ = json.loads(j)

from abc import ABCMeta, abstractmethod


class BaseStorage(metaclass=ABCMeta):
    """Creates references to other databases"""

    @abstractmethod
    def delete_game_state(self, game_name, channel_id):
        """Deletes current game"""
        pass

    @abstractmethod
    def get_all_game_states(self, game_name):
        """Retrieves entire database"""
        pass

    @abstractmethod
    def load_game_state(self, game_name, channel_id):
        pass

    @abstractmethod
    def save_game_state(self, game_name, channel_id, game_state):
        pass








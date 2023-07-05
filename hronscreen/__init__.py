from otree.api import *
import sys
sys.path.append('..')
from frisbee_server import FRISBEE_SERVER
from frisbee.otree_extension import thingspeak
FRISBEE_SERVER.start_server()


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'hronscreen'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass


# FUNCTIONS
def get_all_connected_clients_info(players):
    number_of_players = len(players)

    # Caution: Right now get_connected_clients blocks code execution if no client has connected yet.
    # As soon as the first client is connected, get_connected_clients_info can return a value.
    connected_clients_info = FRISBEE_SERVER.get_connected_clients_info()

    number_of_connected_participants = len(connected_clients_info)

    # Get All Clients
    while number_of_connected_participants != number_of_players:
        connected_clients_info = FRISBEE_SERVER.get_connected_clients_info()
        number_of_connected_participants = len(connected_clients_info)

    return connected_clients_info

# PAGES
class MyPage(Page):

    @staticmethod
    def live_method(player: Player, data):
        channel_id = player.participant.ch_settings['id']
        write_api_key = player.participant.ch_settings['api_keys'][1]['api_key']

        return {player.id_in_group: int(thingspeak.read_last_entry(write_api_key, channel_id)['field1'])}

class ResultsWaitPage(WaitPage):
    title_text = 'Please wait.'
    body_text = 'You will be redirected automatically.'
    # Probably makes sense to wait for all participants.
    # In doing so we have to execute get_connected_clients_info not that much/on multiple different occasions.
    wait_for_all_groups = True

    @staticmethod
    def after_all_players_arrive(subsession: Subsession):
        # connected_clients_info = FRISBEE_SERVER.get_connected_clients_info()
        players = subsession.get_players()
        connected_clients_info = get_all_connected_clients_info(players)
        # Save client info in participant vars
        for player in players:
            # client_info = [client_info for client_info in connected_clients_info
            # if client_info.get("participant_label") == player.participant.label]
            for client_info in connected_clients_info:
                if client_info.get("participant_label") == player.participant.label:
                    player.participant.vars['ch_settings'] = client_info['thingspeak_ch_settings']
                    break
        FRISBEE_SERVER.start_recording(to_all=True)


class Results(Page):
    pass


page_sequence = [ResultsWaitPage, MyPage, Results]

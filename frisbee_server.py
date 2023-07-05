from frisbee.otree_extension import server_ws, thingspeak
# FRISBEE INTEGRATION
# Configuration of the ThingSpeak Channels that will be created during the experiment
CHANNEL_CONFIG = thingspeak.ChannelConfig(
    api_key='F2G8QCFK1CSPNPNP',
    description='An experiment xyz.',
    field1='field1',
    fieldX={},
    name='Experiment Name',
    public_flag=False,
    tags=['tag1'],
    use_participant_specific_preface=True
)
# Configuration of the Frisbee
FRISBEE_SERVER = server_ws.FrisbeeCom(
    host='127.0.0.1',
    port=8001,
    participant_label_file='_rooms/demo_participants.txt',
    channel_config=CHANNEL_CONFIG
)
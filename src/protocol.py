#parse JSON msg

import json

def parse_msg(raw):
    #raw -> dict
    try:
        return json.loads(raw)
    except:
        return None 
    
def mk_play(card, suit=None):
    return json.dumps({"type":"Play", "card":card, "suits":suit})

def mk_draw():
    return json.dumps({"type":"Draw"})
# Standard Library Imports
import uuid
from datetime import datetime
import logging
import traceback
# 3rd Party Imports
# Local Imports
from Utils import get_gmaps_link, get_move_damage, get_move_dps, get_move_duration,\
    get_move_energy, get_pokemon_gender, get_pokemon_size, get_applemaps_link, get_pkmn_name, get_form_name

log = logging.getLogger('WebhookStructs')


################################################## Webhook Standards  ##################################################


# RocketMap Standards
class RocketMap:
    def __init__(self):
        raise NotImplementedError("This is a static class not meant to be initiated")

    @staticmethod
    def make_object(data):
        try:
            kind = data.get('type')
            if kind == 'pokemon':
                return RocketMap.pokemon(data.get('message'))
            elif kind == 'pokestop':
                return RocketMap.pokestop(data.get('message'))
            elif kind == 'gym':
                log.debug('I AINT DOIN NOTHING ABOUT REGULAR GYM POSTS')
                #return RocketMap.gym(data.get('message'))
            elif kind == 'gym_details':
                return RocketMap.gym_details(data.get('message'))
            elif kind in ['captcha', 'scheduler']:  # Unsupported Webhooks
                log.debug("{} webhook received. This webhooks is not yet supported at this time.".format({kind}))
            elif kind == 'location':
                return RocketMap.location(data.get('message'))
            else:
                log.error("Invalid type specified ({}). Are you using the correct map type?".format(kind))
        except Exception as e:
            log.error("Encountered error while processing webhook ({}: {})".format(type(e).__name__, e))
            log.debug("Stack trace: \n {}".format(traceback.format_exc()))
        return None

    @staticmethod
    def pokemon(data):
        #log.debug("Converting to pokemon: \n {}".format(data))
        # Get some stuff ahead of time (cause we are lazy)
        quick_id = check_for_none(int, data.get('move_1'), '?')
        charge_id = check_for_none(int, data.get('move_2'), '?')
        lat, lng = data['latitude'], data['longitude']
        # Generate all the non-manager specifics
        pkmn = {
            'type': "pokemon",
            'id': data['encounter_id'],
            'pkmn_id': int(data['pokemon_id']),
            'disappear_time': datetime.utcfromtimestamp(data['disappear_time']),
            'lat': float(data['latitude']),
            'lng': float(data['longitude']),
            'cp': check_for_none(int, data.get('cp'), '?'),
            'level': check_for_none(int, data.get('pokemon_level'), '?'),
            'iv': '?',
            'atk': check_for_none(int, data.get('individual_attack'), '?'),
            'def': check_for_none(int, data.get('individual_defense'), '?'),
            'sta': check_for_none(int, data.get('individual_stamina'), '?'),
            'quick_id': quick_id,
            'quick_damage': get_move_damage(quick_id),
            'quick_dps': get_move_dps(quick_id),
            'quick_duration': get_move_duration(quick_id),
            'quick_energy': get_move_energy(quick_id),
            'charge_id': charge_id,
            'charge_damage': get_move_damage(charge_id),
            'charge_dps': get_move_dps(charge_id),
            'charge_duration': get_move_duration(charge_id),
            'charge_energy': get_move_energy(charge_id),
            'height': check_for_none(float, data.get('height'), 'unkn'),
            'weight': check_for_none(float, data.get('weight'), 'unkn'),
            'gender': get_pokemon_gender(check_for_none(int, data.get('gender'), '?')),
            'size': 'unknown',
            'tiny_rat': '',
            'big_karp': '',
            'gmaps': get_gmaps_link(lat, lng),
            'applemaps': get_applemaps_link(lat, lng),
            'rating_attack': data.get('rating_attack'),
            'rating_defense': data.get('rating_defense'),
            'form': check_for_none(int, data.get('form'), ''),
            'previous_id': check_for_none(int, data.get('previous_id'), ''),
            'worker_level': check_for_none(int, data.get('worker_level'), '?'),
            'catch_prob_1': check_for_none(float, data.get('catch_prob_1'), '?'),
            'catch_prob_2': check_for_none(float, data.get('catch_prob_2'), '?'),
            'catch_prob_3': check_for_none(float, data.get('catch_prob_3'), '?'),
            'verified': check_for_none(str, data.get('verified'), '?')
        }
        if pkmn['atk'] != '?' or pkmn['def'] != '?' or pkmn['sta'] != '?':
            pkmn['iv'] = float(((pkmn['atk'] + pkmn['def'] + pkmn['sta']) * 100) / float(45))
        else:
            pkmn['atk'], pkmn['def'], pkmn['sta'] = '?', '?', '?'

        if pkmn['height'] != 'unkn' or pkmn['weight'] != 'unkn':
            pkmn['size'] = get_pokemon_size(pkmn['pkmn_id'], pkmn['height'], pkmn['weight'])
            pkmn['height'] = "{:.2f}".format(pkmn['height'])
            pkmn['weight'] = "{:.2f}".format(pkmn['weight'])

        if pkmn['pkmn_id'] == 19 and pkmn['size'] == 'Tiny':
            pkmn['tiny_rat'] = 'Tiny'

        if pkmn['pkmn_id'] == 129 and pkmn['size'] == 'Big':
            pkmn['big_karp'] = 'Big'

        rating_attack = pkmn['rating_attack']
        pkmn['rating_attack'] = rating_attack.upper() if rating_attack else '-'
        rating_defense = pkmn['rating_defense']
        pkmn['rating_defense'] = rating_defense.upper() if rating_defense else '-'

        if pkmn['form']:
            pkmn['form'] = '[' + get_form_name(int(pkmn['form'])) + ']'

        if pkmn['previous_id']:
            pkmn['previous_id'] = '(' + get_pkmn_name(int(pkmn['previous_id'])) + ')'

        if pkmn['catch_prob_1']:
            pkmn['catch_prob_1'] = pkmn['catch_prob_1'] * 100
            pkmn['catch_prob_1'] = int(round(pkmn['catch_prob_1'], 3))

        if pkmn['catch_prob_2']:
            pkmn['catch_prob_2'] = pkmn['catch_prob_2'] * 100
            pkmn['catch_prob_2'] = int(round(pkmn['catch_prob_2'], 3))

        if pkmn['catch_prob_3']:
            pkmn['catch_prob_3'] = pkmn['catch_prob_3'] * 100
            pkmn['catch_prob_3'] = int(round(pkmn['catch_prob_3'], 3))

        if pkmn['verified'] == 'True':
            pkmn['verified'] = 'Times Verified'
        else:
            pkmn['verified'] = 'Times Unknown'

        return pkmn

    @staticmethod
    def pokestop(data):
        log.debug("Converting to pokestop: \n {}".format(data))
        if data.get('lure_expiration') is None:
            log.debug("Un-lured pokestop... ignoring.")
            return None
        stop = {
            'type': "pokestop",
            'id': data['pokestop_id'],
            'expire_time':  datetime.utcfromtimestamp(data['lure_expiration']),
            'lat': float(data['latitude']),
            'lng': float(data['longitude']),
            'name': check_for_none(str, data.get('name'), '?'),
            'description': check_for_none(str, data.get('description'), '?'),
            'lurl': check_for_none(str, data.get('url'), ''),
            'deployer': check_for_none(str, data.get('deployer'), '?')
        }
        stop['gmaps'] = get_gmaps_link(stop['lat'], stop['lng'])
        stop['applemaps'] = get_applemaps_link(stop['lat'], stop['lng'])
        return stop

    @staticmethod
    def gym(data):
        log.debug("Converting to normal gym: \n {}".format(data))
        gym = {
            'type': "gym",
            'id': data.get('gym_id',  data.get('id')),
            "team_id": int(data.get('team_id',  data.get('team'))),
            "points": str(data.get('gym_points')),
            "guard_pkmn_id": data.get('guard_pokemon_id'),
            'lat': float(data['latitude']),
            'lng': float(data['longitude'])
        }
        gym['gmaps'] = get_gmaps_link(gym['lat'], gym['lng'])
        gym['applemaps'] = get_applemaps_link(gym['lat'], gym['lng'])
        return gym

    @staticmethod
    def gym_details(data):
        log.debug("Converting to gym-details: \n {}".format(data))
        defenders = ""
        for pokemon in data.get('pokemon'):
            defenders += "**[{0} CP:{1}]** Trained By **[{2} Lv:{3}]**\n".format(get_pkmn_name(pokemon['pokemon_id']), pokemon['cp'], pokemon['trainer_name'], pokemon['trainer_level'])
        gym_details = {
            'type': "gym",
            'id': data.get('gym_id',  data.get('id')),
            'team_id': int(data.get('team_id',  data.get('team'))),
            "points": str(data.get('gym_points')),
            "guard_pkmn_id": data.get('guard_pokemon_id'),
            'defenders': defenders,
            'lat': float(data['latitude']),
            'lng': float(data['longitude']),
            'name': check_for_none(str, data.get('name'), '?'),
            'description': check_for_none(str, data.get('description'), '?'),
            'gurl': check_for_none(str, data.get('url'), '')
        }
        # log.warning("PARSED GYM INFORMATION: \n {}".format(gym_details))
        gym_details['gmaps'] = get_gmaps_link(gym_details['lat'], gym_details['lng'])
        return gym_details

    @staticmethod
    def location(data):
        data['type'] = 'location'
        data['id'] = str(uuid.uuid4())
        return data



# Ensure that the value isn't None but replacing with a default
def check_for_none(type_, val, default):
    return type_(val) if val is not None else default

########################################################################################################################

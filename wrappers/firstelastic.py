from typing import Union, List, Dict

import requests


class FRCES(object):
    """
    Helper for fetching FRC data from FIRST's ElasticSearch instance and returning data in a tbapy compatible format.
    """

    def __init__(self, year: int):
        """
        Sets up access to the FIRST Elasticsearch. 
        Pre-fetches a map of event keys to event IDs for the specified year.
        
        :param year: Int year to fetch events for.
        """

        # todo: url config
        self.URL_BASE = 'http://es01.usfirst.org'
        self.EVENT_LIST_URL = '/events/_search?size=1000&source={"query":{"query_string":{"query":"(event_type:FRC)%%20AND%%20(event_season:%s)"}}}'  # (year)
        self.EVENT_TEAMS_URL = '/teams/_search?size=1000&source={"_source":{"exclude":["awards","events"]},"query":{"query_string":{"query":"events.fk_events:%s%%20AND%%20profile_year:%s"}}}'  # (first_eid, year)
        self.session = requests.session()
        self.current_year = year
        self.event_key_map = self._get_event_key_to_id_map(year)

    def _get(self, endpoint: str) -> Union[List, Dict]:
        """
        Helper method: GET data from given URL
        
        :param endpoint: String for endpoint to get data from.
        :return: Requested data in JSON format.
        """
        return self.session.get(self.URL_BASE + endpoint).json()

    def _get_event_key_to_id_map(self, year: int) -> Dict[str, str]:
        """
        Builds a dictionary mapping of normal FRC event keys to FIRST Event IDs used in ES.
        
        :param year: Int year to fetch events for.
        :return: Dictionary containing the event key to ID map.
        """
        event_list = [hit['_source'] for hit in self._get(self.EVENT_LIST_URL % year)['hits']['hits']]
        event_key_map = {}
        for event in event_list:
            event_key = str(year) + event['event_code'].lower()
            event_key_map[event_key] = event['id']

        return event_key_map

    def get_event_teams(self, event_key: str, simple: bool = False, keys: bool = False) -> Union[List[str], List[Dict]]:
        """
        Get list of teams at an event. 
        NOTE: Home championships are not calculated.
        
        :param event_key: Event key to get data on.
        :param simple: Get only vital data.
        :param keys: Return list of team keys only rather than full data on every team.
        :return: List of string keys or team objects.
        """

        """Map of FIRST ES field names onto TBA names"""
        field_map = {'website': 'team_web_url',
                     'team_number': 'team_number_yearly',
                     'state_prov': 'team_stateprov',
                     'rookie_year': 'team_rookieyear',
                     'postal_code': 'team_postalcode',
                     'nickname': 'team_nickname',
                     'name': 'team_name_calc',
                     'country': 'countryCode',
                     'city': 'team_city'
                     }

        if event_key in self.event_key_map:
            first_event_id = self.event_key_map[event_key]
            raw_list = [hit['_source'] for hit in
                        self._get(self.EVENT_TEAMS_URL % (first_event_id, self.current_year))['hits']['hits']]

            team_list = []

            for team in raw_list:
                team_obj = {'motto': None,
                            'location_name': None,
                            'key': 'frc' + str(team['team_number_yearly']),
                            'gmaps_place_id': None,
                            'address': None,
                            'lng': None,
                            'lat': None}

                if 'location' in team.keys():
                    team_obj['lng'] = team['location'][0]['lon']
                    team_obj['lat'] = team['location'][0]['lat']

                for field in field_map:
                    if field_map[field] in team.keys():
                        team_obj[field] = team[field_map[field]]
                team_list.append(team_obj)

            if keys:
                return [team['key'] for team in team_list]

            if simple:
                simple_fields = ['city', 'country', 'key', 'name', 'nickname', 'state_prov', 'team_number']
                return [{key: val for key, val in team.items() if key in simple_fields} for team in team_list]

            return team_list
        else:
            return []

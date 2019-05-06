import requests

class FRCES(object):
    """
    Helper for fetching FRC data from FIRST's ElasticSearch instance and returning data in a tbapy compatible format.
    """
    
    def __init__(self, year):
        """
        Sets up access to the FIRST Elasticsearch. 
        Pre-fetches a map of event keys to event IDs for the specified year.
        
        :param year: Int year to fetch events for.
        """
        self.URL_BASE = 'http://es01.usfirst.org'
        self.EVENT_LIST_URL = '/events/_search?size=1000&source={"query":{"query_string":{"query":"(event_type:FRC)%%20AND%%20(event_season:%s)"}}}'  # (year)
        self.EVENT_TEAMS_URL = '/teams/_search?size=1000&source={"_source":{"exclude":["awards","events"]},"query":{"query_string":{"query":"events.fk_events:%s%%20AND%%20profile_year:%s"}}}'  # (first_eid, year)
        self.session = requests.session()
        self.currentYear = year
        self.eventKeyMap = self._getEventKeyToIdMap(year)
    
    def _get(self, endpoint):
        """
        Helper method: GET data from given URL
        
        :param endpoint: String for endpoint to get data from.
        :return: Requested data in JSON format.
        """
        return self.session.get(self.URL_BASE + endpoint).json()
    
    def _getEventKeyToIdMap(self, year):
        """
        Builds a dictionary mapping of normal FRC event keys to FIRST Event IDs used in ES.
        
        :param year: Int year to fetch events for.
        :return: Dictionary containing the event key to ID map.
        """
        eventList = [hit['_source'] for hit in self._get(self.EVENT_LIST_URL % (year))['hits']['hits']]
        eventKeyMap = {}
        for event in eventList:
            eventKey = str(year) + event['event_code'].lower()
            eventKeyMap[eventKey] = event['id']
        
        return eventKeyMap
    
    def event_teams(self, event, simple=False, keys=False):
        """
        Get list of teams at an event. 
        NOTE: Home championships are not calculated.
        
        :param event: Event key to get data on.
        :param simple: Get only vital data.
        :param keys: Return list of team keys only rather than full data on every team.
        :return: List of string keys or team objects.
        """
        
        """Map of FIRST ES field names onto TBA names"""
        fieldMap = {'website': 'team_web_url',
                   'team_number': 'team_number_yearly',
                   'state_prov': 'team_stateprov',
                   'rookie_year': 'team_rookieyear',
                   'postal_code': 'team_postalcode',
                   'nickname': 'team_nickname',
                   'name': 'team_name_calc',
                   'country': 'countryCode',
                   'city': 'team_city'}
        
        if event in self.eventKeyMap:
            firstEventId = self.eventKeyMap[event]
            rawList = [hit['_source'] for hit in self._get(self.EVENT_TEAMS_URL % (firstEventId, self.currentYear))['hits']['hits']]
            
            teamList = []
            
            for team in rawList:
                teamObj = {'motto': None,
                           'location_name': None,
                           'key': 'frc' + str(team['team_number_yearly']),
                           'gmaps_place_id': None,
                           'address': None,
                           'lng': None,
                           'lat': None}
            
                if 'location' in team.keys():
                     teamObj['lng'] = team['location'][0]['lon']
                     teamObj['lat'] = team['location'][0]['lat']
                
                for field in fieldMap:
                    if fieldMap[field] in team.keys():
                        teamObj[field] = team[fieldMap[field]]
                teamList.append(teamObj)
            
            if keys:
                return [team['key'] for team in teamList]
            
            if simple:
                simpleFields = ['city', 'country', 'key', 'name', 'nickname', 'state_prov', 'team_number']
                return [{key: val for key, val in team.items() if key in simpleFields} for team in teamList]
            
            return teamList
        else:
            return []

# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker, ValidationAction, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from dotenv import dotenv_values
import requests
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import pandas as pd
from word2number import w2n


geolocator = Nominatim(user_agent="rasa_chat")
reverse = RateLimiter(geolocator.reverse, min_delay_seconds=0.1)
API_KEY = dotenv_values()["API_KEY"]

class ActionBeginningSearch(Action):
    def name(self) -> Text:
        return "action_beginning_search"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Utter message before making search
        dispatcher.utter_message(text=f'Looking for {tracker.get_slot("place_type")} in \
            {", ".join(tracker.get_slot("address"))} with a search radius of {tracker.get_slot("radius")} km')
        return []


class ActionPlacesSearch(Action):
    def __init__(self) -> None:
        # Defining dictionary for mapping to category ids
        self.code_dict = {'restaurants':'13065', 'coffee houses':'13032', 'both restaurants and coffee houses':'13065,13032'}
    
    def name(self) -> Text:
        return "action_places_search"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Getting parameter values from slots
        categories = self.code_dict[tracker.get_slot('place_type')]
        location = tracker.get_slot('lat_lon')
        radius = int(float(tracker.get_slot('radius'))*1000)
        
        # Setting headers to pass to the API call
        headers = {
            "Accept": "application/json",
            "Authorization": API_KEY
        }
        
        params = {'ll':location, 'radius':radius, 'categories':categories}
        url = 'https://api.foursquare.com/v3/places/search'
        
        try:
            # Making the API call
            r = requests.get(url, params=params, headers=headers)
            
            # Parsing the returned json to get desired values
            results = {'name':[], 'lat':[], 'lon':[], 'distance':[]}
            
            for result in r.json()['results']:
                results['name'].append(result['name'])
                results['lat'].append(result['geocodes']['main']['latitude'])
                results['lon'].append(result['geocodes']['main']['longitude'])
                results['distance'].append(result['distance'] / 1000)
            
            df = pd.DataFrame(results)
            
            # We get the latitude and values from the FOURSQUARE API, and we convert them to addresses by reverse geocoding using geopy Nominatim
            df['address'] = df.apply(lambda x: reverse((x['lat'], x['lon']) ).address , axis=1)
            
            # Format the dataframe to bot response
            bot_response = '\n\n'.join(df.apply(lambda x: f"Name: {x['name']}\nAddress: {x['address']}\nDistance: {x['distance']} km", axis=1))
        except:
            # In case we run into an error we return this response
            bot_response = 'No results returned. Try with a different location or larger radius.'
        
        dispatcher.utter_message(text = bot_response)
        return []


class ValidatePredefinedSlots(ValidationAction):
    def validate_address(
        self,
        slot_value: List,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        
        try:
            # Get the latitude and longitude of the address by geocoding using geopy Nominatim
            location = geolocator.geocode(', '.join(slot_value))
            
            if location is None:
                # If the location isn't recognized by geopy Nominatim we return the following message and set the slot value to none
                dispatcher.utter_message(template="utter_wrong_address")
                return {"address": None}
            else:
                # If all is right we keep the address slot value as is. We also set the value of the lat_lon slot using the latitude and longitude value of the current address
                return {"address": slot_value, 'lat_lon': f'{location.latitude},{location.longitude}'}
        except:
            # In case we run into an error we return the following message
            dispatcher.utter_message(text='Facing server issues. Please try again later')

    def validate_radius(
        self,
        slot_value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        
        try:
            # if the user gave a valid number as input we should be able to convert to numeric form
            number =  int(float(w2n.word_to_num(slot_value))*1000 )
            
            # The radius should be between 0 to 100 km
            if number > 100000:
                dispatcher.utter_message(text='Maximum radius is 100 km. Setting radius to 100 km.')
                return {'radius': str(100)}
            elif number < 100:
                dispatcher.utter_message(text='Minimum radius is 0.1 km. Setting radius to 0.1 km.')
                return {'radius': str(0.1)}
            else:
                return {'radius': str(number/1000)}
        except:
            # if user gave input that cannot be converted into a number, then we return the following messsage
            dispatcher.utter_message(template="utter_wrong_radius")
            return {"radius": None}

class ValidatePlacesSearchForm(FormValidationAction):
    def name(self) -> Text:
        return 'validate_places_search_form'
    
    def validate_address(
        self,
        slot_value: List,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        
        try:
            # Get the latitude and longitude of the address by geocoding using geopy Nominatim
            location = geolocator.geocode(', '.join(slot_value))
            
            if location is None:
                # If the location isn't recognized by geopy Nominatim we return the following message and set the slot value to none
                dispatcher.utter_message(template="utter_wrong_address")
                return {"address": None}
            else:
                # If all is right we keep the address slot value as is. We also set the value of the lat_lon slot using the latitude and longitude value of the current address
                return {"address": slot_value, 'lat_lon': f'{location.latitude},{location.longitude}'}
        except:
            # In case we run into an error we return the following message
            dispatcher.utter_message(text='Facing server issues. Please try again later')
    
    def validate_radius(
        self,
        slot_value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        
        try:
            # if the user gave a valid number as input we should be able to convert to numeric form
            number =  int(float(w2n.word_to_num(slot_value))*1000 )
            
            # The radius should be between 0 to 100 km
            if number > 100000:
                dispatcher.utter_message(text='Maximum radius is 100 km. Setting radius to 100 km.')
                return {'radius': str(100)}
            elif number < 100:
                dispatcher.utter_message(text='Minimum radius is 0.1 km. Setting radius to 0.1 km.')
                return {'radius': str(0.1)}
            else:
                return {'radius': str(number/1000)}
        except:
            # if user gave input that cannot be converted into a number, then we return the following messsage
            dispatcher.utter_message(template="utter_wrong_radius")
            return {"radius": None}


# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker, ValidationAction, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import requests
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import pandas as pd
from word2number import w2n
# import random


geolocator = Nominatim(user_agent="rasa_chat")
reverse = RateLimiter(geolocator.reverse, min_delay_seconds=0.1)

class ActionBeginningSearch(Action):
    def name(self) -> Text:
        return "action_beginning_search"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message(text=f'Looking for {tracker.get_slot("place_type")} in \
            {", ".join(tracker.get_slot("address"))} with a search radius of {tracker.get_slot("radius")} km')
        return []

class ActionPlacesSearch(Action):
    def __init__(self) -> None:
        self.code_dict = {'restaurants':'13065', 'coffee houses':'13032', 'both restaurants and coffee houses':'13065,13032'}
    
    def name(self) -> Text:
        return "action_places_search"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        categories = self.code_dict[tracker.get_slot('place_type')]
        # location = geolocator.geocode(', '.join(tracker.get_slot('address')))
        location = tracker.get_slot('lat_lon')
        radius = int(float(tracker.get_slot('radius'))*1000)
        
        headers = {
            "Accept": "application/json",
            "Authorization": "fsq3y8UCI0XNTY5e67xYbHMAqx7CCJZ7x1or+mAj6lBFwqY="
        }

        params = {'ll':location, 'radius':radius, 'categories':categories}
        url = 'https://api.foursquare.com/v3/places/search'
        
        try:
            r = requests.get(url, params=params, headers=headers)

            results = {'name':[], 'lat':[], 'lon':[], 'distance':[]}
            for result in r.json()['results']:
                results['name'].append(result['name'])
                results['lat'].append(result['geocodes']['main']['latitude'])
                results['lon'].append(result['geocodes']['main']['longitude'])
                results['distance'].append(result['distance'] / 1000)

            df = pd.DataFrame(results)

            df['address'] = df.apply(lambda x: reverse((x['lat'], x['lon']) ).address , axis=1)
            
            bot_response = '\n\n'.join(df.apply(lambda x: f"Name: {x['name']}\nAddress: {x['address']}\nDistance: {x['distance']} km", axis=1))
        except:
            bot_response = 'No results returned. Try with a different location or larger radius.'
        
        # if random.random() > 0.2:
        #     bot_response = f'I got something,{categories}, {location.address}, {radius}'
        # else:
        #     bot_response = 'No results returned. Try with a different location or larger radius.'
        
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
            location = geolocator.geocode(', '.join(slot_value))
            
            if location is None:
                dispatcher.utter_message(template="utter_wrong_address")
                return {"address": None}
            else:
                return {"address": slot_value, 'lat_lon': f'{location.latitude},{location.longitude}'}
        except:
            dispatcher.utter_message(text='Facing server issues. Please try again later')

    def validate_radius(
        self,
        slot_value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        try:
            number =  int(float(w2n.word_to_num(slot_value))*1000 )
            if number > 100000:
                dispatcher.utter_message(text='Maximum radius is 100 km. Setting radius to 100 km.')
                return {'radius': str(100)}
            elif number < 100:
                dispatcher.utter_message(text='Minimum radius is 0.1 km. Setting radius to 0.1 km.')
                return {'radius': str(0.1)}
            else:
                return {'radius': str(number/1000)}
        except:
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
            location = geolocator.geocode(', '.join(slot_value))
            dispatcher.utter_message(text = f'{slot_value}')
            if location is None:
                dispatcher.utter_message(template="utter_wrong_address")
                return {"address": None}
            else:
                # SlotSet('lat_lon', f'{location.latitude},{location.longitude}')
                return {"address": slot_value, 'lat_lon': f'{location.latitude},{location.longitude}'}
        except:
            dispatcher.utter_message(text='Facing server issues. Please try again later')
    
    def validate_radius(
        self,
        slot_value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        try:
            number =  int(float(w2n.word_to_num(slot_value))*1000 )
            if number > 100000:
                dispatcher.utter_message(text='Maximum radius is 100 km. Setting radius to 100 km.')
                return {'radius': str(100)}
            elif number < 100:
                dispatcher.utter_message(text='Minimum radius is 0.1 km. Setting radius to 0.1 km.')
                return {'radius': str(0.1)}
            else:
                return {'radius': str(number/1000)}
        except:
            dispatcher.utter_message(template="utter_wrong_radius")
            return {"radius": None}

# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []

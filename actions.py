from __future__ import unicode_literals

from typing import Dict,Text,Any,List,Union,Optional

from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction
from rasa_sdk.events import SlotSet
from rasa_sdk import ActionExecutionRejection
from rasa_core.constants import REQUESTED_SLOT
class RestaurantForm(FormAction):
    
    def name(self) -> Text:
        return "restaurant_form"
    
    @staticmethod
    
    def required_slots(tracker: Tracker) -> List[Text]:
        return ["cuisine","num_people","outdoor_seating","preferences","feedback"]
    
    def slot_mapping(self) -> Dict[Text,Union[Dict, List[Dict]]]:
        
        return {
                "cuisine":self.from_entity(entity="cuisine",not_intent="chitchat"),
                "num_people":[self.from_entity(entity="num_people",intent=["inform","request_restaurant"]),
                              self.from_entity(entity="number"),],
                "outdoor_seating":[
                        self.from_entity(entity="seating",intent=["inform"]),
                        self.from_intent(intent="affirm",value=True),
                        self.from_intent(intent="deny",value =False),
                        
                        ],
                "preferences":[
                        self.from_intent(intent="deny",value = "no additional preferences"),
                        self.from_text(not_intent ="affirm"),
                        ],
                "feedback":[self.from_entity(entity="feedback"),self.from_text()],
                }
    @staticmethod
    
    def cuisine_db() -> List[Text]:
        
        return ["carribean","chinese","french","greek","indian","italian","mexican",]
    @staticmethod
    def is_int(string: Text) -> bool:
        
        try:
            int(string)
            return True
        except ValueError:
            return False
    
def validate(self, dispatcher:CollectingDispatcher, tracker:Tracker, domain: Dict[Text, Any]) -> List[Dict]:
    
    slot_values =self.extract_other_slots(dispatcher, tracker, domain)
    
    slot_to_fill =tracker.get_slot(REQUESTED_SLOT)
    if slot_to_fill:
        slot_values.update(self.extract_requested_slot(dispatcher, tracker,domain))
        if not slot_values:
            raise ActionExecutionRejection(self.name(),"Failed to validate slot {0}""with action {1}""".format(slot_to_fill,
                                                         self.name()))
        for slot,value in slot_values.items():
            if slot =='cuisine':
                if value.lower() in self.cuisine_db():
                    slot_values[slot]= value
                else:
                    dispatcher.utter_template("utter_wrong_cuisine", tracker)
                    slot_values[slot] =None
            if slot == 'num_people':
                if self.is_int(value) and int(value):
                    slot_values[slot]= value
                else:
                    dispatcher.utter_template("utter_wrong_num_people",tracker)
                    slot_values[slot] =value
            if slot =='outdoor_seating':
                if type(value)== str:
                    if 'out' in value:
                        slot_values[slot] =True
                    elif 'in' in value:
                        slot_values[slot] =False
                    else:
                        dispatcher.utter_template("utter_wrong_outdoor_seating",tracker)
                        slot_values[slot]=None
        return [SlotSet(slot, value) for slot, value in slot_values.items()]
            
            
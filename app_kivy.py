from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.dropdown import DropDown
from kivy.uix.scrollview import ScrollView
from kivy.uix.relativelayout import RelativeLayout
import paho.mqtt.client as paho
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle


class ConnectScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = RelativeLayout()

        self.error_label = Label(text='', size_hint=(None, None), pos_hint={'center_x': 0.5, 'center_y': 0.3})
        self.layout.add_widget(self.error_label)

        
        topic_label = Label(text='TORQUE CHECKING MACHINE', size_hint=(None, None), pos_hint={'center_x': 0.5, 'center_y': 0.9})
        self.layout.add_widget(topic_label)

        self.topic_dropdown = DropDown()
        self.topic_button = Button(text='', size_hint=(0.3, None), pos_hint={'center_x': 0.5, 'center_y': 0.6}, markup=True)
        self.topic_button.bind(on_release=self.topic_dropdown.open)
        self.topic_dropdown.bind(on_select=lambda instance, x: setattr(self.topic_button, 'text', x))

        topics = ["Cycle_step", "Topic2", "Topic3"]
        for topic in topics:
            btn = Button(text=topic, size_hint=(1, None), height=44)
            btn.bind(on_release=lambda btn: self.topic_dropdown.select(btn.text))
            self.topic_dropdown.add_widget(btn)

        self.layout.add_widget(Label(text='Select Topic', size_hint=(None, None), pos_hint={'center_x': 0.2, 'center_y': 0.6}, markup=True))
        self.layout.add_widget(self.topic_button)

        self.connect_button = Button(text='Connect', size_hint=(0.3, None), pos_hint={'center_x': 0.5, 'center_y': 0.4}, markup=True)
        self.connect_button.size = (100, 60)
        self.connect_button.bind(on_press=self.connect)

        self.layout.add_widget(self.connect_button)

        self.add_widget(self.layout)

    def connect(self, instance):
        selected_topic = self.topic_button.text
        if selected_topic == 'Select Topic':
            self.error_label.text = "Please select a valid topic"
            return

        self.error_label.text = ""

        self.manager.transition.direction = 'left'
        self.manager.current = 'display'

        self.topic = selected_topic
        self.client = paho.Client("client-001")
        self.client.on_message = self.on_message
        self.client.connect("broker.emqx.io")
        self.client.subscribe(self.topic)
        self.client.loop_start()

    def on_message(self, client, userdata, message):
        data = message.payload.decode("utf-8")
        
        # Split the received data by comma
        data_list = data.split(',')
        
        # Check if the data_list has enough items to access by name
        if len(data_list) >= 7:
            # Access specific items by index (assuming seven items)
            item1 = data_list[0]
            item2 = data_list[1]
            item3 = data_list[2]
            item4 = data_list[3]
            item5 = data_list[4]
            item6 = data_list[5]
            item7 = data_list[6]
            
            # Create a dictionary with item names and values
            item_data = {
                "Machine Status": item1,
                "Emergency Status": item2,
                "Part No.": item3,
                "Cycle time": item4,
                "Required Torque": item5,
                "Measured Torque": item6,
                "Serviceable or Non-Serviceable": item7
            }
            
            # Update the display in the 'DisplayScreen' with the item data
            App.get_running_app().root.get_screen('display').update_display(item_data)
        else:
            # Handle the case where there are not enough items in the received data
            formatted_data = "Received data does not contain enough items"
            App.get_running_app().root.get_screen('display').update_display(formatted_data)

class DisplayScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=20)
        self.blocks = {}  # Store blocks in a dictionary

        # Create blocks for each item
        for item_name in ["Machine Status", "Emergency Status", "Part No.", "Cycle time", "Required Torque", "Measured Torque", "Serviceable or Non-Serviceable"]:
            block = BoxLayout(orientation='horizontal', spacing=10)
            label = Label(text=item_name + ": ", size_hint_x=None, width=300, valign='top')
            value_label = Label(text='', valign='top')
            block.add_widget(label)
            block.add_widget(value_label)
            self.blocks[item_name] = value_label
            self.layout.add_widget(block)

        
        self.add_widget(self.layout)

    def update_display(self, item_data):
        # Update block widgets with item data
        for item_name, value_label in self.blocks.items():
            value = item_data.get(item_name, '')
            value_label.text = value

class MaxbyteApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(ConnectScreen(name='connect'))
        sm.add_widget(DisplayScreen(name='display'))
        return sm

        layout = BoxLayout(orientation='vertical')
        layout.canvas.before.clear()
        with layout.canvas.before:
            Color(1, 1, 1, 1)  # White color (RGBA)
            Rectangle(pos=self.pos, size=self.size)
        
        layout.add_widget(sm)
        return layout

if __name__ == '__main__':
    MaxbyteApp().run()

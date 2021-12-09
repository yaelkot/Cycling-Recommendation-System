import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen

kv = Builder.load_file("my.kv")

class grid(Widget):

    start_location = ObjectProperty(None)
    time_duration = ObjectProperty(None)
    num_recommendations = ObjectProperty(None)


    def btn(self):
        print("start location:", self.start_location.text, "time duration: ", self.time_duration.text, "number of recommendations: ", self.num_recommendations.text)
        self.start_location = ""
        self.time_duration = ""
        self.num_recommendations = ""


class app(App):

    def build(self):
        return grid()
        # return kv

if __name__ == "__main__":
    app().run()

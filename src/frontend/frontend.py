from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.lang import Builder

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

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.network.urlrequest import UrlRequest
from kivy.graphics import Rectangle, Color

kv = Builder.load_file("my.kv")


class Popups(FloatLayout):
    pass


class grid(Widget):

    start_location = ObjectProperty(None)
    time_duration = ObjectProperty(None)
    num_recommendations = ObjectProperty(None)

    def show_popup(self, title):
        show = Popups()
        popupWindow = Popup(title=title, content=show, size_hint=
        (0.5,0.6))
        popupWindow.open()
        # Attach close button press with popup.dismiss action
        # content.bind(on_press = popup.dismiss)

    def btn(self):
        if any(char.isdigit() for char in self.start_location.text) or not self.time_duration.text.isdigit() or not self.num_recommendations.text.isdigit():
            self.show_popup(title="Wrong Input")
        #http reguest with the given parameters
        else:
            lst = self.start_location.text.split(" ")
            start_stat = lst[0]
            for word in lst[1:]:
                start_stat = start_stat + "+" + word
            str_url = "http://127.0.0.1:5000/?startlocation=" + start_stat
            str_url += "&timeduration=" + self.time_duration.text + "&k=" + self.num_recommendations.text
            req = UrlRequest(url=str_url)
            if req.error != None:
                pass
            elif req.result != None:
                pass
        self.start_location.text = ""
        self.time_duration.text = ""
        self.num_recommendations.text = ""


class app(App):

    def build(self):
        return grid()

if __name__ == "__main__":
    app().run()

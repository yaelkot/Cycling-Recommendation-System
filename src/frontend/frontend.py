from src.backend.mybackend import Database
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.uix.popup import Popup

"""It building the kv file. The file has grid with GridLayout into it that they are the main window. 
It also has in Grid Canvas for background and button for recommendations.
There is Popups that represent the window of popup and has AsyncImage and Label that build in run time according 
to user input.
@:return instance of kv file with all the properties, objects that built from them. """
kv = Builder.load_file("my.kv")


"""
It loading the csv file and connect frontend to the server using the backend.
@:return instance of Database class in backend.mybackend.py.
"""
db = Database('BikeShare.csv')


"""
It used to be the window that we can put widgets on it and even one on the other.
@:return class of Popups that inherited from FloatLayout
"""
class Popups(FloatLayout):
    pass


"""
This class inherited from Widget and the window of the main page of the app.
@:return class of Popups that inherited from Widget and could.
"""
class grid(Widget):

    """
    @:param  start_location: start location of the riding that given by the user
    @:param  time_duration: time duration of the riding that given by the user
    @:param  num_recommendations: number of recommendations of the end stations of riding that given by the user
    """
    start_location = ObjectProperty(None)
    time_duration = ObjectProperty(None)
    num_recommendations = ObjectProperty(None)


    """
    @:param title: title of popup 
    @:param stations: list of recommended end stations if there are  
    This function according to the given title build in run time pop up window accordingly.
    Each pop up window has different image, label and their parameters.
    """
    def show_popup(self, title, stations=None):
        show = Popups()
        pop_window = Popup(title=title, content=show, size_hint=(0.5,0.6))
        #if the type of one of the inputs is wrong
        if title == "Wrong Input":
            show.ids.img.size_hint = (0.5,0.67)
            show.ids.img.pos_hint = {"x":0.245, "top":0.69}
            show.ids.text_message.text = "Your input was wrong. \n     Please try again"
            show.ids.img.source = '../Images/falling_child_from_bike.gif'
        #if name of Start Station is not in the database
        elif title == "Wrong Start Station":
            show.ids.text_message.text = "The start location is not exsits"
            show.ids.img.size_hint = (0.9,0.95)
            show.ids.img.pos_hint = {"x":0.05, "top":0.95}
            show.ids.img.source = '../Images/start.jpg'
        #if there are end stations that match to user's start station and duration time
        else:
            end_stations = "\n\nWe recommand you to travel: \n"
            for station in stations:
                end_stations = end_stations + "         " + station + "\n"
            show.ids.text_message.text = end_stations
            show.ids.img.source = '../Images/map-of-new-york-and-new-jersey.jpg'
            show.ids.img.size_hint = (0.5,0.55)
            show.ids.img.pos_hint = {"x":0.245, "top":0.55}
        pop_window.open()


    """
    This function is binding to the button of recommends in the main window of app.
    It takes user's input and act accordingly to the senior.
    """
    def btn(self):
        #if the input is incorrect by type, so choose to build the accordanly popup
        if any(char.isdigit() for char in self.start_location.text) or not self.time_duration.text.isdigit() or not self.num_recommendations.text.isdigit():
            self.show_popup(title="Wrong Input")
        #if the input is correct by type
        else:
            recommondation = db.get_places(self.start_location.text, self.time_duration.text, self.num_recommendations.text)
            #if start staion is not in db, so choose to build the accordanly popup
            if len(recommondation) == 0:
                self.show_popup(title="Wrong Start Station")
            #if start staion is in db, so choose to build the accordanly popup
            else:
                self.show_popup(title="End Stations", stations=recommondation)
        #reset text input fields
        self.start_location.text = ""
        self.time_duration.text = ""
        self.num_recommendations.text = ""


"""
This class inherited from App: should be like App
@:return instance of class that build the main window of the app
"""
class app(App):

    def build(self):
        return grid()


"""
@:return main that started the application
"""
if __name__ == "__main__":
    app().run()

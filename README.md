# phonesurveytool

Is an open source project enabling organizations collect data on projects utilizing SMS and WhatsApp survey’s. The tool was built to enable social impact organization who are using Kobo Collect or ODK as “hands-on” surveying tools to collect data more rapidly and efficiently. The project is still in an early stage of development, use with caution and ensure you back-upp all of your data. The section below explain the code and guides you to set up the phonesurveytool web application and gets you started with Twilio.

## Roadmap

The project was developed as a part of a project at DTU and has been customized for a couple of organizations needing it for implementations with various development projects. There is no current development ongoing on the phonesurveytool but in the future I might work on customization features such as
* -Account management
* -Messaging authority
* -Gateway customization (Twilio/Africa’sTalking and more)
For now several of these things are hardcoded.

## Documentation

The web app is built on Python Flask and utilizes a Mongodb backend. Some experiments have been conducted utilizing TensorFlow Learn to build a simple question/response chatbot enabling users to get more dynamic responses. The section below goes into detail on the structure of the application

### Structure

** Setup **

The init file sets up the web application and loads all the configuartions and blueprints. If you are to add more pages/section this is where they should be loaded

The .flaskenv sets the name of the application and most importantly sets the debug value to true. IF or WHEN you launch for production this must be changed to false.

You should create a .env file which contains the data needed to be loaded into the configuration in the init file above. The file should look like:

![alt text](https://github.com/johanjuulj/phonesurveytool/blob/main/Screenshot%20from%202023-05-30%2009-52-42.png)


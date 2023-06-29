# phonesurveytool

Is an open source project enabling organizations collect data on projects utilizing SMS and WhatsApp survey’s. The tool was built to enable social impact organization who are using Kobo Collect or ODK as “hands-on” surveying tools to collect data more rapidly and efficiently. The project is still in an early stage of development, use with caution and ensure you back-upp all of your data. The section below explain the code and guides you to set up the phonesurveytool web application and gets you started with Twilio.

## Roadmap

The project was developed as a part of a project at DTU and has been customized for a couple of organizations needing it for implementations with various development projects. There is no current development ongoing on the phonesurveytool but in the future I might work on customization features such as

- Account management
- Messaging authority
- Gateway customization (Twilio/Africa’sTalking and more)
- Chatbot functionality - Adding simple chatbot funtionality for Q&A purposes to educate the user.
- Proper unit test and integration test implementation
  For now several of these things are hardcoded.

## Documentation

The web app is built on Python Flask and utilizes a Mongodb backend. Some experiments have been conducted utilizing TensorFlow Learn to build a simple question/response chatbot enabling users to get more dynamic responses. The section below goes into detail on the structure of the application

### Structure

**Setup**

The init file sets up the web application and loads all the configuartions and blueprints. If you are to add more pages/section this is where they should be loaded

The .flaskenv sets the name of the application and most importantly sets the debug value to true. IF or WHEN you launch for production this must be changed to false.

You should create a .env file which contains the data needed to be loaded into the configuration in the init file above. Please input a unique secret key for security in the .env file the other input values are further explained below in the documentation. The file should look like:

![alt text](https://github.com/johanjuulj/phonesurveytool/blob/main/Screenshot%20from%202023-05-30%2009-52-42.png)

requirements.txt file contains all the dependencies that needs to be install prior to running the app.

**routes**
The main directory containts all the routes for the webapplication divided into "routes" for main/misc routes, notification routes and survey routes. These are the three main categories of routes throughout the application.

**static folder**
The static folder contains all the CSS for the web application and the minimal amount of javascript code.

**templates folder**
The templates folder contiains all the "views"/pages displayed. Future work could entail making some of them more dynamic by adding some JS functionality.

## Deployment

First steps to deploy is to ensure you have updated the .env file as explained above and exected the installation of dependencies through pip is described above
To deploy this project run

**Setup Kobo**

In your Kobo Collect account go to the security page and copy the token as shown below

![alt text](https://github.com/johanjuulj/phonesurveytool/blob/main/Kobo_Setup.png)

Copy that into the .env file under AUTH_KOBO_Token

**Setup Twilio**
First you need to create a Twilio account. For more information on account types check https://www.twilio.com/docs/messaging/build-your-account

Or go straight to sign-up https://www.twilio.com/try-twilio

In testing please go under "sandbox" and find the datapoints TWILIO_SID & AUTH_TOKEN these are to be inserted into the .env file prior to launching the web application.

**Setup MongoDB**

Setup and MongoDB account and connect it to your prefered cloud hosting service. For more indepth information see https://www.mongodb.com/free-cloud-database

After completing the setup please find the MongoDB URI and insert it into the .env file.

**Install Dependencies**
With the .env file correctly setup you need to install the libraries and packages the web application relies on.
Run the following command in your terminal to install everything with pip:

```
pip install -r requirements.txt
```

Note that the current version of tensorflow doesn't match with Python 3.11

### Launch Test Environment

```
  flask run
```

Your web application should now be working on your localhost

### Launch Production Environment

First decide on a cloud hosting solution to launch the web-application on. I suggest using the same as you are using to host your database.

Note: the chatbot functionality and corresponding folders/documents should be moved to another branch and should be ignorred for now. This includes data.pickle checkpoint model.tflearn+ and everything in the chatbot & model folders.

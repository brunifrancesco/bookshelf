#Magnet

Magnet is a personal digital library. It keep traces of your read books, performing a very basic text mining features which consist of retrieving useful information you don't provide (cover, description, kind of book) and achieves a text analisys, highlighting the most relevant features book by book, using some NLP tecquniques. 

The final aim of Magnet is suggesting reading, based on the previous read books, using the *linked open data*.
Any help to afford this task is then well appreciated. 
Magnet was born as a *weekend experiment*; thus a lot can be done to get it working better. 


##Where *Magnet* comes from?
I'm more interested in exctrating text features, like a Magnet whose attract iron from useless stuff. 
This digital library is just a way to retrieve enough data to perform some basical tasks about text mining/classification and reccomandation system.

##What exactly Magnet do
Magnet allows you to store the read book using in a MongoDB instance. Please see the *settings.py* to change how Magnet will be connected to your Mongo instance.
Once user sign up/log in, a list of read books appears in the private area with a supersimple form to add new book. 
In order to accomplish this operation, a query to Google Books API is implemented in order to get some useful details to be shown in te apposite area, while a basic text analysis (just in italian at this time, using the *pattern* module) is made to find out relevan *POS* patterns. 
Please refer the code for details or let me know for clarifications.

##How to test Magnet locally
Even if Magnet is online at www.magnet.ovh, you can test Magnet locally. 
Since it is implemented on top of the *Django* framework and MongoDB, you need to follow this guide to make it working. 

1. Install Mongo and run it in background or as a service;
2. Install *virtualenv* and run
	
		virtualenv --distribute magnet
3. Cd in the *magnet* folder and clone the repo;
4. Activate the repo

		source bin/activate
	
4. Install dependencies using the requirements.txt file in the magnet root directory (this may take some time..):
			
			pip install -r requirements.txt
5. Run

		python manage runserver

6. Point your browser to *http://localhost:8000* and enjoy the app. 


##Insights
Magnet insights (visible pointing to /insights) have been computed using the Mongo Aggregation Framework.
			
			

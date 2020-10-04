# python-docker-web-template
Please take a look at the [demo](http://134.0.119.196/)
1. First of all the app collects data (forecast) from Open Weather API .

2. When data are received, a docker container starts to format them and sends to MongoDB (it is also docker-container).

3. Nginx captures your request and sends it to Flask.

4. After that Flask app collects the data from DB and prepares MATPLOTLIB figure and shows it.

If you would like to take a look to the code, please go to GitHub.

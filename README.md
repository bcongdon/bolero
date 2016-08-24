# bolero
> :dancer: Construct your personal API

## Installation
### Local Installation
1. Install [Postgres](https://wiki.postgresql.org/wiki/Detailed_installation_guides) and have it running locally.
2. Clone the bolero repo with:

	```sh
	git clone https://github.com/bcongdon/bolero
	cd bolero
	```

3. Create and activate a virtualenv with Python3 

	```sh
	virtualenv -p python3 venv
	source venv/bin/activate
	```
4. Install bolero's pip dependencies

	```sh
	# Install bolero's pip dependencies
	pip install -r requirements.txt
	```

5. Run the startup script.
	
	```sh
	./start.py
	```
	
### Heroku Deployment
TODO

## Trackers
Trackers live in `bolero/trackers/` and provide both models and API scrapers for various services like Wunderlist and Fitbit.
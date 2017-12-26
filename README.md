# bolero
> :dancer:  Construct your personal API

Bolero backs up and cleans personal data, and allows you to expose that data as a personal RESTful API.

## Methodology

Consuming APIs to access your personal data is a pain. API wrappers make this work less tedious, but each service still has it's own authentication mechanism and data schema. Bolero abstracts away the API layer of downloading your data. Simply authenticate a Bolero tracker with each of your services, and access your data locally via RESTful API or SQL database.

Bolero aims to provide a platform on which you can build your own quantified self visualizations and data munging experiments. Get fast, reliable, and immediate access to the lifetime all the data you store online.

## Installation
### Local Installation
1. Install [Postgres](https://wiki.postgresql.org/wiki/Detailed_installation_guides) and have it running locally.
2. Clone the bolero repo with:

	```sh
	git clone https://github.com/bcongdon/bolero
	cd bolero
	```

4. Install bolero's dependencies using [Pipenv](https://github.com/pypa/pipenv)

	```sh
	# Install bolero's pip dependencies
	pipenv install
	```

5. Run the startup script.
	
	```sh
	./start.py
	```

### Heroku Deployment
TODO

## Trackers
Trackers live in `bolero/trackers/` and provide both models and API scrapers for various services.

### Supported Services:

* Fitbit
* MyFitnessPal
* Nokia Health (formerly Withings)
* Todoist
* Twitter
* Wunderlist

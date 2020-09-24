streambikes
==============================

Testing real time weather and bike APIs and online learning with Plotly Dash 
You need api keys from [JCDecaux](https://developer.jcdecaux.com/#/opendata/vls?page=getstarted) and [OpenWeatherAPI](https://openweathermap.org/api/hourly-forecast) to run the project.
To run in docker:
- launch docker 
- Add your API keys in `src/settings/api_keys.yml`
- run :
  ```bash
  docker secret create api_keys src/settings/api_keys.yml
  ```
  ```bash
  docker-compose build
  ```
  ```bash
  docker-compose up
  ```

Run for dev:

```bash
make create_environments
```

Activate the environment

Install packages

```bash
make requirements
```

If you are developing :

```bash
make requirements-dev
```

To run the dash app: 
export API keys as environment variables :

```bash
export DECAUX_API="yourbikeapikey"
export WEATHER_API="yourweatherapikey"
```

```bash
dash run src/application/dashapp.py
```

Project Organization
------------
```
├── docker-compose.yml          <- Dash + Redis services docker compose 
├── Dockerfile                  <- Dash application docker file
├── Makefile                    <- Makefile with commands like `make data` or `make train`
├── LICENSE
├── README.md               
├── data                        <- data (essentially empty because we use online learning)
├── docs                        <- project documentation
├── requirements-dev.txt        <- python developpement modules requirements (tests, linting, etc)
├── requirements.txt            <- python packages requirements
├── mypy.ini                    <- mypy static type checking settings
├── setup.py                    <- makes project pip installable (pip install -e .) so src can be imported
├── src                         <- Source code for use in this project.
│   ├── __init__.py
│   ├── application             <- Scripts to create a Plotly Dash app to present results
│   │   ├── dashapp.py
│   │   └── data_for_dash.py
│   ├── data                    <- Scripts to download or generate data (calls APIs)
│   │   ├── __init__.py
│   │   └── collect_data.py
│   ├── features                <- Scripts to turn raw data into features for modeling
│   │   ├── __init__.py
│   │   └── build_features.py
│   ├── models                  <- Scripts for online learning (train and predict at the same time)
│   │   ├── __init__.py
│   │   └── online_model.py
│   └── settings                <- settings folder that manages changes between dev/staging(CI)/ and prod settings
│       ├── __init__.py
│       ├── api_keys.template
│       └── conf.py
├── tests
│   ├── __init__.py
│   ├── conftest.py
│   └── unit_tests
│       ├── application
│       ├── data
│       ├── features
│       ├── models
│       └── settings
└── tox.ini                     <- tox file with settings for running tox; see tox.readthedocs.io
```

--------

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>

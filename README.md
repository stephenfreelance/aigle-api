# Aigle API

## Deploy

### Set up docker

1. Create local volume to persist db data:

```
docker volume create aigle_data
```

2. Create `.env` and `.env.compose` from templates
3. Build and run docker containers:

```
docker build -f Dockerfile -t aigle_api_app_container .
docker-compose --env-file .env -f docker-compose.yml up --force-recreate -d db app
```

## Django

### Add an app

```
python manage.py startapp my_app
```

### Authentication

Authentication in this project is managed with [djoser](https://djoser.readthedocs.io/en/latest/getting_started.html)
You can create a user by running command:

```
python manage.py create_super_admin --email myemail@email.com --password mypassword
```

### Development

#### Set-up

This project is meant to be used with Python 3.12.3.

1. Create a virtual environment and activate it (here an example with `venv`)

```
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies

```
pip3 install -r requirements.txt
```

3. Create `.env` and `.env.compose` file and replace values

```
cp .env.template .env
cp .env.compose.template .env.compose
```

4. Run local server

```
source .env && source venv/bin/activate && make start
```

During the development, a graphic interface is provided by Django to test the API: make `GET`, `POST`,... requests easily. It is accessible by default on http://127.0.0.1:8000/

I recommend to use an extension like [Requestly](https://chromewebstore.google.com/detail/requestly-intercept-modif/mdnleldcmiljblolnjhpnblkcekpdkpa) to add the token generated in the header and access to protected routes.

### Commands

Some commands need to be run to seed data necessary for the app to works well.

```
# import all collectivites
python manage.py import_georegion
python manage.py import_geodepartment
python manage.py import_geocommune

# import hérault
python manage.py import_georegion --insee-codes 76
python manage.py import_geodepartment --insee-codes 34
python manage.py import_geocommune

# insert tiles: for montpellier and its surroundings
python manage.py create_tile --x-min 265750 --x-max 268364 --y-min 190647 --y-max 192325

# import parcels
python manage.py import_parcels
```

### Custom zones

Custom zones are big objects so we need to pre-compute and store in database associated zones for each detections. To do so, there is a command BUT this command is not really performant when updating a lot of objects. So here is a SQL request to create links between detections and custom zones:
```
insert
	into
	core_detectionobject_geo_custom_zones(
	detectionobject_id,
	geocustomzone_id
)
select
	distinct
	dobj.id as detectionobject_id,
	{custom_zone_id} as geocustomzone_id
from
	core_detectionobject dobj
join core_detection detec on
	detec.detection_object_id = dobj.id
where
	ST_Intersects(
		detec.geometry,
		(
		select
			geozone.geometry
		from
			core_geozone geozone
		where
			id = {custom_zone_id}
		)
	)
```

### Emails

To send emails locally, you'll need to install local certificates, [here is how to do it in MacOS](https://korben.info/ssl-sslcertverificationerror-ssl-certificate_verify_failed-certificate-verify-failed-unable-to-get-local-issuer-certificate-_ssl-c1129.html)

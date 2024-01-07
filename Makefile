SECRET_KEY=secret@123
DEBUG=1
USE_DEV_APPS=1
ALLOWED_HOSTS=127.0.0.1, localhost
STATIC_URL=static/
STATIC_ROOT=
MEDIA_URL=
MEDIA_ROOT=media/
CACHE_BACKEND=django.core.cache.backends.redis.RedisCache
CACHE_LOCATION=redis://127.0.0.1:6379
USE_POSTGRES=1
PG_NAME=
PG_USER=
PG_PASSWORD=
PG_HOST=
PG_PORT=

env_line = $(if ${$1},"$1=${$1}","# $1=")

create_env:
	rm .env -f
	@echo "\n# SECURITY:" >> .env
	@echo $(call env_line,SECRET_KEY,) >> .env
	@echo $(call env_line,ALLOWED_HOSTS,) >> .env

	@echo "\n# DEV:" >> .env
	@echo $(call env_line,DEBUG,) >> .env
	@echo $(call env_line,USE_DEV_APPS,) >> .env

	@echo "\n# FILES:" >> .env
	@echo $(call env_line,STATIC_URL,) >> .env
	@echo $(call env_line,STATIC_ROOT,) >> .env
	@echo $(call env_line,MEDIA_URL,) >> .env
	@echo $(call env_line,MEDIA_ROOT,) >> .env

	@echo "\n# DATABASE:" >> .env
	@echo $(call env_line,USE_POSTGRES,) >> .env
	@echo $(call env_line,PG_NAME,) >> .env
	@echo $(call env_line,PG_USER,) >> .env
	@echo $(call env_line,PG_PASSWORD,) >> .env
	@echo $(call env_line,PG_HOST,) >> .env
	@echo $(call env_line,PG_PORT,) >> .env

	@echo "\n# CACHE:" >> .env
	@echo $(call env_line,CACHE_BACKEND,) >> .env
	@echo $(call env_line,CACHE_LOCATION,) >> .env
	@echo "Created!"

migrate:
	python manage.py migrate

docker_image_build:
	sudo docker build --progress=plain -t equibook .

docker_container_rmf:
	sudo docker container rm -f equibook_app

docker_container_run:
	sudo docker container run -d --name equibook_app -p 8000:8000 equibook 


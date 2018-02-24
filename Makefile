# run to launch a docker container that mounts the complete repo
# DO NOT RUN from inside docker... it will cause a container
# inside a container (inside a container, inside a container,...)
start_docker:
	docker run --rm -d -p 7777:8888 -v `pwd`:/home/jovyan/work --name kaggle_ncaa jupyter/scipy-notebook

install:
	pip install -r requirements.txt

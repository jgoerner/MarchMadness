start_docker:
	docker run --rm -d -p 7777:8888 -v `pwd`:/home/jovyan/work --name kaggle_ncaa jupyter/scipy-notebook

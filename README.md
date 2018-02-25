# MarchMadness
This "wrapper" repository is used to build up the computational environment (e.g. jupyter, postgresql, ...).<br> 
The actual content of the repository can be [found here](https://github.com/jgoerner/MarchMadness/tree/master/MarchMadness)

# Requirements
- [docker](https://docs.docker.com/install/)
- [docker-compose](https://docs.docker.com/compose/install/)
- a valid `jupyter.env` file containing access keys & tokens (send me a note)

# Setup of the environment
0. put the `jupyter.env` into `./config` (build will fail if you don't)
1. build the composed images via `docker-compose build`
2. run the application via `docker-compose up -d`
3. get the ContainerID of the jupyter container via `docker ps | grep jupyter_container`
4. get the Jupyter token via `docker logs <paste jupyter container id here>` (substitute port *8888* with *7777*)
5. paste the Jupyter-Token URL into your web browser of choice and start doing awesome stuff :-)

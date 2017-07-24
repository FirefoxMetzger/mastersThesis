FROM jupyter/scipy-notebook
USER jovyan
RUN conda install -n python2 --yes -c conda-forge peewee
RUN conda install -n python2 --yes -c bioconda mysqlclient

ENV PYTHONPATH=$PYTHONPATH:/home/jovyan/dlc
ENV DB_ADDRESS=mysql://root:password@mysql/reinforcement_learning
ADD jupyter/dlc/ ./dlc

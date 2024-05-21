# Use official miniconda image as the base image
FROM continuumio/miniconda3 as miniconda3

# Set the working directory
WORKDIR /usr/local/src

# Install python libraries
COPY ./environment.yml /usr/local/src/environment.yml
RUN conda update conda
RUN conda env update --name base --file /usr/local/src/environment.yml

# Set volume
VOLUME [ "/usr/local/src" ]

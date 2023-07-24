#!/bin/bash

#docker build . -t langchain:latest
docker run -d \
	--rm \
	--name langchain-devel \
	--env OPENAI_API_KEY=${OAI_KEY} \
	-p 8080:8080 \
	-v $(pwd)/demo_app:/usr/src/app \
	-v $(pwd)/chromadb:/chromadb langchain-devel

#FROM https://stackoverflow.com/questions/70155930/how-to-update-source-code-without-rebuilding-image-each-time
#docker run -d --name langchain-dev -it --rm -p 8080:8080 -v $(pwd):/usr/src/app langchain-dev



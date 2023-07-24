#!/bin/bash

docker build . -t langchain-devel:latest
#docker run -d --name langchain --env OPENAI_API_KEY=${OAI_KEY} -p 8080:8080 langchain


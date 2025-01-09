#!/bin/bash

conda create -n chatbot_pooh python=3.12 -qy
conda activate chatbot_pooh

pip install -r requirements.txt -q

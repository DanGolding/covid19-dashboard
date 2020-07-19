FROM python:3.8-slim-buster

RUN apt-get update
RUN apt-get -y install build-essential

RUN mkdir -p /root/.streamlit
RUN bash -c 'echo -e "\
[general]\n\
email = \"\"\n\
" > /root/.streamlit/credentials.toml'
# The $PORT environment variable is used to be compatible with Heroku
RUN bash -c 'echo -e "\
[server]\n\
enableCORS = false\n\
port = $PORT\n\
" > /root/.streamlit/config.toml'

COPY /src ./src
COPY requirements.txt ./requirement.txt
COPY setup.py ./setup.py
RUN pip3 install .

CMD ["streamlit", "run", "src/covid19_dashboard/dashboard.py"]

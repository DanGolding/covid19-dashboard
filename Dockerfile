FROM python:3.8-slim-buster

RUN mkdir -p /root/.streamlit
RUN bash -c 'echo -e "\
[general]\n\
email = \"\"\n\
" > /root/.streamlit/credentials.toml'
RUN bash -c 'echo -e "\
[server]\n\
enableCORS = false\n\
" > /root/.streamlit/config.toml'

RUN mkdir covid19
COPY src covid19/src
COPY requirements.txt covid19/requirements.txt
COPY dev_requirements.txt covid19/dev_requirements.txt
COPY setup.py covid19/setup.py
RUN pip3 install ./covid19

# The $PORT environment variable is used to be compatible with Heroku
CMD streamlit run covid19/src/covid19_dashboard/dashboard.py --server.port $PORT

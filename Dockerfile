FROM debian:bullseye

RUN apt-get update && apt-get install -y \
    python3 python3-pip \
    fonts-liberation libappindicator3-1 libasound2 libatk-bridge2.0-0
RUN apt-get update && apt-get install -y \
    libnspr4 libnss3 lsb-release xdg-utils libxss1 libdbus-glib-1-2 \
    curl unzip wget
RUN apt-get update && apt-get install -y libgbm1 libu2f-udev xvfb firefox-esr

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONUNBUFFERED=1

ENV APP_HOME /usr/src/app
WORKDIR /$APP_HOME

COPY . $APP_HOME/

RUN pip3 install selenium streamlit webdriver-manager pyvirtualdisplay

EXPOSE 8501
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "clipping_gnews2.py", "--server.port=8501", "--server.address=0.0.0.0"]
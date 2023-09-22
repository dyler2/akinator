FROM python:latest


RUN git clone https://github.com/dyler2/akinator.git /akinator
WORKDIR /akinator
RUN python -m pip install --upgrade pip
RUN python -m pip install --no-cache-dir -r akinator/requirements.txt
CMD python3 akinator-bot.py

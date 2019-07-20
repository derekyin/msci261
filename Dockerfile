FROM python:latest
ADD *.py /code/
ADD requirements.txt /code/
WORKDIR /code
RUN pip install -r requirements.txt
EXPOSE 80
CMD ["gunicorn", "-b", "0.0.0.0:80", "server:app"]

# Python
FROM python:3.4-alpine
# ADD /code/requirements.txt /requirements.txt
COPY code/ /prod/
WORKDIR /prod/
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
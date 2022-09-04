FROM python:3.9
WORKDIR /by
COPY . /by/
RUN pip install --no-cache-dir --upgrade -r /by/requirements.txt
WORKDIR /by/source
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]

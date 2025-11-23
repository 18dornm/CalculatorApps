FROM python:3.13.9-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 7860
CMD ["python", "main.py"]
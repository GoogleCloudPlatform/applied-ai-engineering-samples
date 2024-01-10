FROM python:3.9
EXPOSE 8080
WORKDIR /app
COPY . ./
RUN pip install -r requirements.txt
ENTRYPOINT ["streamlit", "run", "mock-ui.py", "--server.port=8080", "--server.address=0.0.0.0"]

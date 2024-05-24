# Image
FROM python:3.8
LABEL maintainer="Kah Ho Phong"

# Setup env
COPY techtrends /techtrends
WORKDIR /techtrends
EXPOSE 3111

# Install dependencies
RUN pip install -r requirements.txt
RUN python init_db.py

# Run on container start
CMD [ "python", "app.py" ]

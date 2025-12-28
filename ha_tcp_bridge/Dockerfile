ARG BUILD_FROM
FROM $BUILD_FROM

# Install Python dependencies (requests for HA API calls)
RUN pip3 install --no-cache-dir requests

# Copy application
COPY server.py /
COPY run.sh /
RUN chmod +x /run.sh

CMD [ "/run.sh" ]

FROM neo4j:5.21

# Install APOC plugin
ENV NEO4J_PLUGINS='["apoc"]'

# Ensure directory exists
RUN mkdir -p /conf

# Copy custom configuration if needed
# COPY conf/neo4j.conf /conf/neo4j.conf

# Allow connections from outside the container
ENV NEO4J_dbms_default__listen__address=0.0.0.0
ENV NEO4J_dbms_connector_bolt_listen__address=0.0.0.0:7687
ENV NEO4J_dbms_connector_http_listen__address=0.0.0.0:7474

# Expose ports (HTTP, HTTPS, Bolt)
EXPOSE 7474 7473 7687

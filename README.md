# Start the topology as defined in http://debezium.io/docs/tutorial/
docker-compose up

# Start MySQL connector
curl -i -X POST -H "Accept:application/json" -H  "Content-Type:application/json" http://localhost:8083/connectors/ -d @register-mysql.json

# Consume messages from a Debezium topic
docker-compose exec kafka /kafka/bin/kafka-console-consumer.sh \
    --bootstrap-server kafka:9092 \
    --from-beginning \
    --property print.key=true \
    --topic mysql1.inventory.customers

# Modify records in the database via MySQL client
docker-compose exec mysql bash -c 'mysql -u $MYSQL_USER -p$MYSQL_PASSWORD inventory'

Or connect using a GUI, credentials are in the docker-compose.yml file

# Shut down the cluster
docker-compose down

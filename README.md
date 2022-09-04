# LILA Games

Objective:
1. Design a REST microservice to fetch most played multiplayer mode given area code.
2. Service should be scalable and able to handler huge number of concurrent users.

Endpoint:
 - GET: hostname:port/stats?area_code=111
 - POST: hostname:port/events/
 - POST: hostname:port/generate_data/

Design:
1. Most active users can be calculated using events. Upon receiving login event from a user for an areacode and 
multiplayer mode we will consider user as an active user for the mode and area combination.
2. Similarly, for a LOGOUT event the user will not be considered as active user.
3. Generally, to calculate most played multiplayer mode given an areacode we will have to
 fire queries to filter area code and then group together similar multiplayer mode 
 and calculate the total counts of each mode. As this information is frequently requested, 
 it will require constant DB queries and will impact performance. 
4. To avoid constant DB queries we can store the already generated frequency counts in cache and return on
 subsequent requests. The data can have TTL to expire it after n seconds. 
5. With this approach, we can have almost realtime data(based on TTL value) and avoid frequent queries.
6. Ex: If we have TTL of 60 sec then for an area code, we will be hitting DB 1 request/1min.

Scaling and High Performance(Serving millions of users):
1. AsyncIO is used for IO from cache(Redis) and DB(PostgresSQL). IO call will be concurrent and performance is improved.
2. Using cache we have reduced Read query load on DB and already computed results are served to users. Based on business requirements, the expiry time for results(30 secs) can be decided depending on consistency of counts. 
Ex: For an area code, 2 query/1 min = 2 * 1 * 60 * 24 = 2880 queries/day will be executed given every 30 sec a get request is received for an areacode. 
3. Using orchestartor like Kubernetes, Docker-swarm the api_server service with Nginx(Load Balancing) will be used to scale based on API hits.
4. Redis, Postgres are highly scalable and can be instantly scaled based on db/cache load.

Assumption: 
1. LOGIN and LOGOUT events will be sent to the service. 
2. Results of GET API will have 30 sec delay.

Schema Design:
1. Table for storing all events: 
   - AreaModeEvents 
       1. event_id = Integer, primary_key=True, autoincrement=True
       2. area_code = String(255), index=True
       3. multiplayer_mode = String(255), index=True
       4. user_id = String(255)
       5. events_name = String(255)
       6. epoch_timestamp =  Timestamp
   - AreaModeEventsAgg
       1. area_code = String(255), index=True
       2. multiplayer_mode = String(255), index=True
       3. current_count = Integer
2. AreaModeEvents will store all events for a given area_code, mulitplayer_mode and user_id. 
3. AreaModeEventsAgg will store agg count of current users logged in at any moment for an area_code and multiplayer_mode.
4. AreaModeEventsAgg will be updated when events are received and stored in AreaModeEvents table.

Cache:
1. Stores data in hashmap. For an area code, it will store list of modes and its count sorted.
### Steps to run:
1. Git clone the repo.
2. Ensure docker is installed and working.
3. From LILA_GAMES directory, do docker-compose up -d --build
4. docker-compose ps to check if services are running
5. Credentials for postgres
   - Username : postgres
   - password : postgres
   - DB : test_db
6. Logs are available for api server at /by/logs inside host
7. OPENAPI docs are available at <hostname>:<port>/docs


## Project Structure
```
├── database
│   └── postgres
├── postgres-data
└── services
    ├── source
      ├── config
      ├── handlers
    │ ├── models
    │ ├── schema
      └── services

```
 - Config folder has the db related functions. 
 - Handlers(Controller) are specific files to handle login for an endpoint.
 - Models stores the ORM model.
 - Schema has the pydantic models
 - Services has specific usecase related to objects. Ex. Redis object. 
 - Unittest has testcase and testdata.
 - Database can have database related scripts or configs, not used currently.

## Function testcases
1. Validate GET requests
2. Validate POST requests for events.
3. Schema related validations
4. Validate count of matching events in db and as returned via API.

## Future Improvements
1. Events for LOGIN/LOGOUT will come individually and there will be too many API hits and similarly 
many DB write and updates. Event queues like kafka,SQS, RabbitMQ can be used to store such events and bulk insert/write operation
can be done to improve performance.



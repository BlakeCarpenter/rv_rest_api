# Python Includes
from __future__ import print_function
import sys
from flask import Flask, request, jsonify
import pprint
from haversine import haversine

# Local Includes
from rv_utility import db_connect, db_cursor

app = Flask(__name__)

@app.route('/teapot')
def teapot():
	return '', 418

# List all cities in a state
# GET /state/{state}/cities
@app.route('/state/<state>/cities', methods=['GET'])
def fetch_cities_by_state(state):
	# Setup
	dbh = db_connect()
	cursor = db_cursor(dbh)
	retrieve_query = '''SELECT c.id, c.name 
						FROM   rv_states s 
						       left join rv_cities c 
						              ON s.id = c.state_id 
						WHERE  s.name = %s 
						        OR s.abbreviation = %s 
						ORDER  BY c.name '''

	cursor.execute(retrieve_query, (state, state))
	ret_list = []
	for(c_id, c_name) in cursor:
		# Returns array of values, hack it to a string
		ret_list.append({'city_id': c_id, 'city_name': c_name})
	return jsonify(ret_list)


# Return a list of cities the user has visited
# GET /user/{user}/visits
# Allow to create rows of data to indicate they have visited a particular city.
# POST /user/{user}/visits
# {
# 	"city": "Chicago",
# 	"state": "IL"
# }
@app.route('/user/<user>/visits', methods=['GET','POST'])
def handle_user_visits_request(user):
	if request.method == 'GET':
		# Setup
		dbh = db_connect()
		cursor = db_cursor(dbh)
		retrieve_query = '''SELECT c.name, c.id
							FROM   rv_visits v 
							       left join rv_users u 
							              ON v.user_id = u.id 
							       left join rv_cities c 
							              ON v.city_id = c.id 
							WHERE  u.id = %s
							GROUP BY c.id '''

		# Apparently important to have the trailing comma if you have only one substitute string (needs a list/tuple)
		cursor.execute(retrieve_query, (user, ))
		ret_list = []
		for(c_name, c_id) in cursor:
			print(c_name, file=sys.stderr)
			ret_list.append({'city_name': c_name, 'city_id': c_id})
		return jsonify(ret_list)
	if request.method == 'POST':
		# Setup

		# JSON data setup
		# Fail if we weren't passed json content header
		if request.is_json is False:
			return jsonify({'error': 'Content must be passed as JSON'}), 400 # No idea what code should be passed here, can't find consensus
		json_data = request.get_json()
		city = json_data['city']
		state = json_data['state']

		# DB setup
		dbh = db_connect()
		cursor = db_cursor(dbh)

		# Set up our DB queries
		check_query = '''SELECT c.id 
						FROM   rv_states s 
						       LEFT JOIN rv_cities c 
						              ON c.state_id = s.id 
						WHERE  c.name = %s 
						       AND s.abbreviation = %s
						LIMIT 1'''

		insert_query = '''INSERT INTO rv_visits (city_id, user_id) 
							VALUES  (%s, %s)'''

		# Verify that we have a valid city which is in our db
		cursor.execute(check_query, (city, state))
		entry = cursor.fetchone()
		city_id = entry[0]
		# Error handle if we didn't get an id back
		if city_id is None:
			return jsonify({'error':'Could not validate city'}), 409
		
		# Now that we know we have a valid city we can add the visit to the database
		cursor.execute(insert_query, (city_id, user))
		dbh.commit()
		if cursor.lastrowid is not None:
			return jsonify({'id': cursor.lastrowid, 'city_id': city_id, 'user_id': user}), 201
		return jsonify({'error': 'Database error'}), 500


# Allow a user to remove an improperly pinned visit.
# DEL /user/{user}/visit/{visit}
@app.route('/user/<user>/visit/<visit>', methods=['DELETE'])
def remove_visit_by_user(user, visit):
	# Setup
	dbh = db_connect()
	cursor = db_cursor(dbh)
	del_query = '''	DELETE FROM rv_visits 
					WHERE  user_id = %s 
					       AND id = %s '''

	cursor.execute(del_query, (user, visit))
	dbh.commit()
	return '', 200


# Return a list of states the user has visited
# GET /user/{user}/visits/states
@app.route('/user/<user>/visits/states', methods=['GET'])
def get_visited_states_by_user(user):
	dbh = db_connect()
	cursor = db_cursor(dbh)
	retrieve_query = '''SELECT DISTINCT s.id, s.name 
						FROM   rv_visits v 
						       LEFT JOIN rv_users u 
						              ON v.user_id = u.id 
						       LEFT JOIN rv_cities c 
						              ON v.city_id = c.id 
						       LEFT JOIN rv_states s 
						              ON c.state_id = s.id 
						WHERE  u.id = %s'''

	cursor.execute(retrieve_query, (user, ))
	ret_list = []
	for(s_id, s_name) in cursor:
		ret_list.append({'id': s_id, 'state': s_name})
	return jsonify(ret_list)

# Funs stuff with lat/long, suggest most frequently visited city in miles range
# Lesson, should've stored lat/long as numbers
@app.route('/city/<city>/suggest/<distance>', methods=['GET'])
def suggest_location(city, distance):
	# Setup
	dbh = db_connect()
	cursor = db_cursor(dbh)

	# Get our initial city data
	retrieve_base_city_query = '''SELECT 0+latitude, 0+longitude FROM rv_cities WHERE id = %s LIMIT 1'''
	cursor.execute(retrieve_base_city_query, (city, ))
	if cursor.rowcount != 1:
		return jsonify({'error':'Could not find base city'}), 404
	base_entry = cursor.fetchone()
	base_lat = base_entry[0]
	base_long = base_entry[1]

	# Retrieve data falling in the appropriate latitude
	retrieve_all_in_lat_query = '''SELECT c.name, 
									       0+c.latitude, 
									       0+c.longitude, 
									       Count(v.id) AS visits 
									FROM   rv_cities c 
									       LEFT JOIN rv_visits v 
									              ON c.id = v.city_id 
									WHERE  c.id != %s 
									       AND c.latitude BETWEEN ( %s - %s / 70 ) AND 
									                              ( %s + %s / 70 ) 
									GROUP  BY c.id '''
	cursor.execute(retrieve_all_in_lat_query, (city, base_lat, distance, base_lat, distance))

	# Set up needed comp data
	base_city = (base_lat, base_long)
	most_visited_city = ''
	most_visits = 0
	closest_city = 'No cities found in the given range'
	clostest_distance = 12450 # Literally the other side of the planet

	# We have our data, make it mean something
	for(c_name, c_lat, c_long, c_visits) in cursor:
		# Get distance
		city_loc = (c_lat, c_long)
		miles_between = haversine(base_city, city_loc, miles=True)

		# Comp by visits
		if c_visits > most_visits:
			most_visits = c_visits
			most_visited_city = c_name

		# Comp by distance
		if miles_between < clostest_distance:
			clostest_distance = miles_between
			closest_city = c_name

	# If we have a most visited city in range, return, otherwise go with closest
	return jsonify({"suggested_city": most_visited_city if most_visits > 0 else closest_city})


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)
from flask import Flask, jsonify, request, abort
from flasgger import Swagger
import psycopg2
import os
from functools import wraps

app = Flask(__name__)

#Swagger template (enforces API key)
swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "CCH App Chores API",
        "description": "API for managing chores and names",
        "version": "1.0.5"
    },
    "securityDefinitions": {
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key"
        }
    },
    "security": [
        {
            "ApiKeyAuth": []
        }
    ]
}

swagger = Swagger(app, template=swagger_template)

# gets API key from environment variable and checks if it matches the one in the request
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != os.getenv('API_KEY'):
            abort(401, description="Invalid or missing API key")
        
        return f(*args, **kwargs)
    return decorated_function

#connects to the database using the DATABASE_URL environment variable
def get_db_connection():
    conn = psycopg2.connect(
        os.getenv('DATABASE_URL'),
        sslmode='require'
    )
    return conn

# Test endpoint to check if the API is running
@app.route('/')
def hello_world():
    """
    Test endpoint to check if the API is running
    ---
    responses:
      200:
        description: Returns a simple message
    """
    return 'Add "/apidocs" to the URL to access the API documentation.'

#Endpoint to get all chores from the database
@app.route('/chores', methods=['GET'])
@require_api_key
def get_chores():
    """
    Test endpoint to Get all chores from the database
    ---
    security:
      - ApiKeyAuth: []
    responses:
      200:
        description: A list of chores
        schema:
          type: array
          items:
            type: object
            properties:
              date:
                type: string
                example: "2025-02-05"
              name:
                type: string
                example: "Jack"
              description:
                type: string
                example: "Take out the trash"
      401:
        description: Unauthorized - Invalid or missing API key
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetch all chores sorting by date
    cursor.execute('SELECT date, name, description FROM chores ORDER BY date ASC;')
    chores = cursor.fetchall()
    
    chore_list = []
    for chore in chores:
        chore_list.append({
            'date': chore[0],
            'name': chore[1],
            'description': chore[2]
        })
    
    cursor.close()
    conn.close()
    
    return jsonify(chore_list)

#Endpoint to get all chores that correspond to a provided name
@app.route('/chores/<name>', methods=['GET'])
@require_api_key
def get_named_chores(name):
    """
    Get chores from the database that correspond to a name
    ---
    parameters:
      - in: path
        name: name
        type: string
        required: true
        description: The name of the person whose chores you want to retrieve
    security:
      - ApiKeyAuth: []
    responses:
      200:
        description: A list of chores
        schema:
          type: array
          items:
            type: object
            properties:
              date:
                type: string
                example: "2025-02-05"
              name:
                type: string
                example: "Jack"
              description:
                type: string
                example: "Take out the trash"
      401:
        description: Unauthorized - Invalid or missing API key
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetch chores corresponding to name sorting by date
    cursor.execute("SELECT date, name, description FROM chores WHERE name = %s ORDER BY date ASC;", (name,))

    chores = cursor.fetchall()

    chore_list = []
    for chore in chores:
        chore_list.append({
            'date': chore[0],
            'name': chore[1],
            'description': chore[2]
        })
    
    cursor.close()
    conn.close()

    if not chores:
      return jsonify({'message': 'No chores found'}), 404
    else:
      return jsonify(chore_list)

#Endpoint to get a chore that corresponds to a provided name and date
@app.route('/chores/<name>/date/<path:date>', methods=['GET'])
@require_api_key
def get_named_dated_chores(name, date):
    """
    Get chore from the database that corresponds to a name and date
    ---
    parameters:
      - in: path
        name: name
        type: string
        required: true
        description: The name of the person whose chore you want to retrieve
      - in: path
        name: date
        type: string
        required: true
        description: The date of the chore you want to retrieve (MM-DD-YYYY format)(don't pad with zeros)
    security:
      - ApiKeyAuth: []
    responses:
      200:
        description: A list of chores
        schema:
          type: array
          items:
            type: object
            properties:
              date:
                type: string
                example: "2025-02-05"
              name:
                type: string
                example: "Jack"
              description:
                type: string
                example: "Take out the trash"
      401:
        description: Unauthorized - Invalid or missing API key
      401:
        description: Chore not found
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetch chore corresponding to name and date sorting by date
    cursor.execute('SELECT description FROM chores WHERE name = %s AND "date" = %s', (name, date))

    chore = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if not chore:
        return jsonify([{"description": "No chore today"}]), 200

    return jsonify([{"description": chore[0]}]), 200

#Endpoint to get all names from the database
@app.route('/names', methods=['GET'])
@require_api_key
def get_names():
    """
    Get all names from the database
    ---
    security:
      - ApiKeyAuth: []
    responses:
      200:
        description: A list of names
        schema:
          type: array
          items:
            type: string
            example: "Jack"
      401:
        description: Unauthorized - Invalid or missing API key
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetch all names
    cursor.execute('SELECT name FROM names;')
    names = cursor.fetchall()
    
    names_list = []
    for name in names:
        names_list.append({
            'name': name[0],
        })
    
    cursor.close()
    conn.close()
    
    return jsonify(names_list)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
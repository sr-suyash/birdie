
from datetime import datetime
from bson.json_util import dumps
from flask import Flask, request
from pymongo import Connection
from bson.objectid import ObjectId
from werkzeug.routing import Rule


app = Flask(__name__)
app.url_map.add(Rule('/', endpoint='birds'))
app.url_map.add(Rule('/birds/', endpoint='birds'))
app.url_map.add(Rule('/birds/<id>', endpoint='birds'))

bird_post_mandatory_fields = ['name', 'family', 'continents']

@app.endpoint('/')
@app.endpoint('birds')
@app.endpoint('birds/<id>')
def birds():
    try:
        conn = Connection(host='localhost', port=27017)
        db_handler = conn['birds_db']
        if request.method == 'GET':
            if request.args.get('id'):
                print request.args.get('id'), type(request.args.get('id'))
                birds = db_handler.birds.find({'_id': ObjectId(request.args.get('id')), 'visible':'true'})
            else:
                birds = db_handler.birds.find({'visible':'true'})
            conn.close()
            return dumps(list(birds))
        elif request.method == 'DELETE':
            db_handler.birds.remove({'_id': ObjectId(request.args.get('id'))})
            conn.close()
            return ''
        elif request.method == 'POST':
            name = request.form.get('name', '')
            family = request.form.get('family', '')
            continents = request.form.get('continents', [])
            visible = request.form.get('visible', 'false')
            if not name or not family or not continents:
                conn.close()
                return 'missing mandatory field - %s' % ' '.join([i for i in bird_post_mandatory_fields if not request.form.get(i)])

            added = str(datetime.utcnow().date())
            bird_data = {
                'name': name,
                'family': family,
                'continents': continents,
                'visible': visible,
                'added': added
            }
            db_handler.birds.insert(bird_data, safe=True)
            conn.close()
            return ''
    except Exception, e:
        return e


if __name__ == '__main__':
    app.run(debug = True)

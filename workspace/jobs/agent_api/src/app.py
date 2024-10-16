import dotenv
import utils
from flask import Flask, Response
from flask_restful import Resource, Api
import json

app = Flask(__name__)
api = Api(app)

class Info(Resource):
    def get(self):
        context = dotenv.dotenv_values('/opt/agent/context.env')
        data = {
            "update_seq": utils.get_update_seq(),
            "agent_id": utils.get_agent_id(),
            "cluster_id": utils.get_cluster_id(),
            "agent_ip": context.get("AGENT_IP"),
            'roles': utils.get_roles()
        }
        # Manually pretty-print the JSON response
        pretty_json = json.dumps(dict(sorted(data.items())), indent=4)
        return Response(pretty_json, mimetype='application/json')

class Job(Resource):
    def get(self):
        jobs = {'jobs': utils.get_jobs()}
        pretty_json = json.dumps(jobs, indent=4)
        return Response(pretty_json, mimetype='application/json')

class Context(Resource):
    def get(self):
        context = dotenv.dotenv_values('/opt/agent/context.env')
        pretty_json = json.dumps({'context': context}, indent=4)
        return Response(pretty_json, mimetype='application/json')

api.add_resource(Job, '/_local/jobs')
api.add_resource(Context, '/_local/context')
api.add_resource(Info, '/')

if __name__ == "__main__":
    app.run(debug=True)

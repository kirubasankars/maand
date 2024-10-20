import dotenv
import utils
from flask import Flask, Response
from flask_restful import Resource, Api
import json

app = Flask(__name__)
api = Api(app)

# Resource to fetch system information
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
        # Pretty-print JSON response
        return Response(json.dumps(data, indent=4, sort_keys=True), mimetype='application/json')

# Resource to fetch jobs
class Job(Resource):
    def get(self):
        jobs = {'jobs': utils.get_jobs()}
        # Pretty-print JSON response
        return Response(json.dumps(jobs, indent=4), mimetype='application/json')

# Resource to fetch context data
class Context(Resource):
    def get(self):
        context = dotenv.dotenv_values('/opt/agent/context.env')
        # Pretty-print JSON response
        return Response(json.dumps({'context': context}, indent=4), mimetype='application/json')

@app.route('/metrics')
def metrics():
    return Response("", mimetype='text/plain')


# Registering API routes
api.add_resource(Job, '/_local/jobs')
api.add_resource(Context, '/_local/context')
api.add_resource(Info, '/')

if __name__ == "__main__":
    app.run(debug=True)

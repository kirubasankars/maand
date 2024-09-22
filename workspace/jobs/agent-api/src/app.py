import dotenv

import utils

from flask import Flask
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)


class Info(Resource):
    def get(self):
        context = dotenv.dotenv_values('/opt/agent/context.env')
        return dict(sorted({
            "update_seq": utils.get_update_seq(),
            "agent_id": utils.get_agent_id(),
            "cluster_id": utils.get_cluster_id(),
            "agent_ip": context.get("AGENT_IP")
        }.items()))


class Role(Resource):
    def get(self):
        return {'roles': utils.get_roles()}


class Job(Resource):
    def get(self):
        return {'jobs': utils.get_jobs()}


class Context(Resource):
    def get(self):
        context = dotenv.dotenv_values('/opt/agent/context.env')
        return {'context': context}


api.add_resource(Role, '/_local/roles')
api.add_resource(Job, '/_local/jobs')
api.add_resource(Context, '/_local/context')
api.add_resource(Info, '/')

if __name__ == "__main__":
    app.run()

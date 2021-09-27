from flask import Flask, json, request
from echoService import onReceive
from Message import Message, fromJSON, toJSON

#companies = [{"id": 1, "name": "Company One"}, {"id": 2, "name": "Company Two"}]

api = Flask(__name__)

@api.route('/echo', methods=['POST'])
def post_echo():
  message_json = str(request.get_json(force=True)).replace("\'", "\"")

  message_obj = fromJSON(message_json)

  echo_return = onReceive(message_obj)
  
  return_json = toJSON(echo_return)

  print(type(return_json))
  print(return_json)
  
  return return_json

if __name__ == '__main__':
    api.run()
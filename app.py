from flask import Flask
from flask import request
from flask import Response
import json
import boto3
import re
import datetime

# arn:aws:lambda:eu-west-1:095485643790:function:RNV

app = Flask(__name__)

long_output = True
dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
table = dynamodb.Table('HVVData')


@app.route('/ausstieg', methods=['GET', 'POST'])
def fahrten():
    fahrt = table.scan()['Count'] - 1
    time = 100
    line = "U1"
    response = table.get_item(
        Key={
            'Fahrt': fahrt
        }
    )
    uuid = response['Item']['startTime']
    endTime = str(datetime.datetime.now() - datetime.datetime(response['Item']['startTime']))
    startTime = response['Item']['startTime']
    fromStation = get_from_Station(time)
    endStation = get_end_Station(time)
    cost = calculate_prize(time)
    color = get_color(line)
    table.put_item(
        Item={
            'Fahrt': fahrt,
            'UUID': uuid,
            'startTime': startTime,
            'endTime': endTime,
            'fromStation': fromStation,
            'endStation': endStation,
            'cost': cost,
            'color': color
        }
    )
    data = json.dumps(build_return_json(), indent=4)
    print(data)
    return data, 200, {'Content-Type': 'application/json; charset=utf-8'}


@app.route("/einstieg", methods=['POST'])
def get_resp():
    incoming_data = request.get_json()
    incoming_data.get("station")
    fahrt = table.scan()['Count']
    uuid = incoming_data.get("uuid")
    line = "U1"
    endTime = str(0)
    startTime = str(datetime.datetime.now())
    fromStation = incoming_data.get("station")
    line = incoming_data.get("station").split()[0]
    print(uuid + fromStation)
    endStation = None
    cost = None
    color = get_color(line)
    table.put_item(
        Item={
            'Fahrt': fahrt,
            'UUID': uuid,
            'startTime': startTime,
            'endTime': endTime,
            'fromStation': fromStation,
            'endStation': endStation,
            'cost': cost,
            'color': color,
            'linie': line
        }
    )
    data = json.dumps(build_return_json(), indent=4)
    print(data)
    return data, 200, {'Content-Type': 'application/json; charset=utf-8'}


def get_end_Station(time):
    if time < 100:
        endStation = "S+U Sternschanze"
    elif time < 200:
        endStation = "S Reeperbahn"
    else:
        endStation = "S Alte Wöhr"
    return endStation


def get_color(line):
    if line == "U1":
        color = "#006ab3"
    elif line == "U2":
        color = "#e1211a"
    elif line == "U3":
        color = "#fd0"
    else:
        color = "#0098a1"
    return color


def build_return_json():
    return_json = {'currentTravel': {
    'fromStation': "U Wedding",
    'startTime': "1506125583823",
    'line': "U1"}, 'pastTravels': []}
    for x in range(0, table.scan()['Count']):
        response = table.get_item(
            Key={
                'Fahrt': x
            }
        )
        current_item = {'Fahrt': int(re.findall("\d+", str(response['Item']['Fahrt']))[0]), 'UUID': response['Item']['UUID'], 'startTime': response['Item']['startTime'], 'endTime': response['Item']['endTime'], 'fromStation': response['Item']['fromStation'], 'endStation': response['Item']['endStation'], 'cost': int(re.findall("\d+", str(response['Item']['cost']))[0]), 'color': response['Item']['color']}
        return_json['pastTravels'].append(current_item)
    return return_json


def get_from_Station(time):
    if time < 100:
        fromStation = "S Barmbek"
    elif time < 200:
        fromStation = "S Landwehr"
    else:
        fromStation = "U Schlump"
    return fromStation


def calculate_prize(time):
    prize = 0
    if time < 100:
        prize = 100
    elif time < 200:
        prize = 200
    else:
        prize = 300
    return prize


@app.route("/", methods=['POST'])
def inital():
    incoming_data = request.data.decode('utf-8')
    incoming_data = json.loads(incoming_data)
    respond_json = json.dumps(respond_json, ensure_ascii=False)
    resp = Response(respond_json)
    return resp


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)

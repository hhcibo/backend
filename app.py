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


@app.route('/status', methods=['GET', 'POST'])
def status():
    item = "-"
    table.put_item(
        Item={
            '-': item
        }
    )
    response = table.get_item(
        Key={
            '-': item,
        }
    )
    return response


@app.route("/mobile", methods=['GET'])
def get_resp():
    fahrt = table.scan()['Count']
    uuid = "uuid"
    time = 100
    line = "U1"
    endTime = str(datetime.datetime.now())
    startTime = str(datetime.datetime.now() - datetime.timedelta(hours=0, minutes=0, seconds=time))
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
    #print(response['Item']['Fahrt'])
    #print(response['Item']['UUID'])
    #print(int(re.findall("\d+", str(response['Item']['Fahrt']))[0]))
    #print(table.scan()['Count'])
    #print(table.scan())
    data = json.dumps(build_return_json(), indent=4)
    print(data)
    #prize = calculate_prize(uuid)
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
        color = "blue"
    elif line == "U2":
        color = "yellow"
    else:
        color = "red"
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


def get_route(uuid, time):
    uuid = "sample_UUID"
    time = 200
    table.put_item(
        Item={
            'UUID': uuid,
            'Time': time
        }
    )
    return


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
    app.run(debug=True)

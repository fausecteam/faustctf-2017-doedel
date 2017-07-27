# DildO Excitement Data Extraction Library

Doedel is a new kind of IOT device for your personal masturbatory pleasure. This Document describes the server implmentaion.

## Design Goals

Since every person is different, we have put great effort in designing the device and protocols to be able to adapt to every users different habits and preferences.

The device is equipped with sensors that can detect how pleasurable a vibration patters, by measurung the users hormonal levels. Based on these information the server selects the best fitting pattern.

## Data Format

All messages are encoded in Extensible Data Notation (see https://github.com/edn-format/edn). All requests are hashes containing at least a :request-type. All responses are also hashes, containing at least a :response-type.

TODO: describe all requests and responses.

## Interfaces

On port 1666 the devices interface with the server and on port 1667 status reports can be requested.

## Security

When users register, they submit a security-token. Using this token, one can verify, that the device is talking to the correct server, as only this one can send the token back.

# Digi-Honk
### Vehicle to Vehicle Communication Utilizing Beacon Stuffing
Development of an algorithm for enabling autonomous vehicles to rapidly communicate 
in a connectionless way using the pre-existing WiFi standard.

## Project Aspect Overview
### A List of the Technologies Explored by this Project
* Beacon Stuffing
* Connectionless Communication
* Utilizing the Pre-existing Infrastructure WiFi
* Four Way Intersection Problem With Autonomous Vehicles

## TODO
The list of tasks left to complete can be found [here](TODO.md).

## Packages
* `iotpy`
    * Writes timestamps to the ESP for it to broadcast
    * Scans the available WiFi signals
    * Reads from the ESP
* `com.faverolles`
    * Interfaces with the python package
        * Provides API to call python scripts within `iotpy`
    * Logic what happens when the vehicle comes to a stop at a four way stop
    * Logic to sort the list of available _`DGhonk-timestamp`_ signals
    * Logic for a vehicle to wait it's turn based on first stop arrival time.
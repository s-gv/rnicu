sensor-cloud
============

This webapp assists in prototyping sensors that push data to the cloud. It provides a service on Google's App Engine to which anyone can push sensor data or any (tag,date,value) tuples for that matter. You can then visualize that data in a browser or get that data in CSV form to play around in tools such as MATLAB.

This helps folks working on sensors to focus on the sensors themselves and stay away from server-side programming during initial prototyping.

How-to-use
----------

- You may either use the service hosted at http://sensor-cloud.appspot.com or clone this repo and host it using your own app engine account. 
- To push data to the service, decide on a tag name which identifies your sensor and issue POST requests to the server. Send a POST request to 'https://sensor-cloud.appspot.com/upload' with parameters 'tag', 'time' in milliseconds since epoch (Jan 1, 1970) and 'value' as a decimal number. See 'samples/sensor_simulate.py', a sample script that posts psuedo-random data to the server.
- Data stored in the service can be accessed via the browser.

Contact
-------

Send an e-mail to sagar.writeme AT gmail.com if you have any questions.

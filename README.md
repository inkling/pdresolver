# pdresolver

`pdresolver` is a python library that watches PagerDuty for new incidents caused by 
third-party services. If these incidents are resolved by the third-party services, 
it resolves the corresponding PagerDuty incidents as well.

Currently, `pdresolver` only implements support for [Wormly](http://wormly.com), a third-party uptime monitoring service. 

## Dependencies

* Python (only tested on Python 2.6.5)
* [Requests](http://docs.python-requests.org/en/latest/) >= 1.1.0
  
## Installation

1. Clone the repo
2. Run `pip install -r requirements.txt` to install requests.

## Configuration

1. Create a json file with your PagerDuty API key, subdomain, and requester_id. You can look at the `sample/conf.json` file for an example of the format.
2. Configure your services. You can use the given wormly service, or you can write you own. See the section on [Extending](#Extending).

## Usage

    chmod +x pdresolver
    ./pdresolver <args>

Command line arguments:
* `--log-file` 

  Where to put the log file. Defaults to `/var/log/pdresolver.log`.

* `--conf-file`

  Where to find the configuration file. Defaults to `/etc/pdresolver/conf.json`.
* `--interval`

  The interval to poll pagerduty. Defaults to 45 seconds 

* `--pagerduty-api-key`

  API key for PagerDuty. Must have ability to poll incidents, poll services and resolve incidents. May be specified in the key file.

* `--pagerduty-requester-id`

  Requester ID for PagerDuty. When incidents are resolved, a Requester ID must be provided 
  to link the resolution action with a user account. May be specified in the key file.

* `--pagerduty-subdomain`

  Subdomain for PagerDuty. Your account should be set up at <--pagerduty-subdomain>.pagerduty.com . May be specified in the key file.

## Extending

`pdresolver` is extendable by adding another `.py` file to `./services/` and
implementing a subclass of `Service` that should do one thing: take a [PagerDuty
incident](http://developer.pagerduty.com/documentation/rest/incidents/show) as a
Python dict and return True if the third-party service claims that the incident 
is still occurring. For any service to work, **the name of the service in PagerDuty 
must match the name of the Service subclass in `pdresolver`, which must also must
match the name of the class, and the name of the file**. (Case-insensitive.)

If you need configuration settings for your service, you can put these values in 
your `conf.json` file, and then access them in your service.

Here's an example of a sample service.

`conf.json`

    {
      ...
      "foo" : {
        "bar" : "baz"
      }
    }
    
`services/foo.py`

    from lib.service import Service
    
    class Foo(Service):
        def incident_is_occurring(self, incident):
            print self.keys['bar'] #will print baz
            return false

## Contributing

We welcome contributions. Please submit a pull request and we'll take a look at it.

## Credits

1. [Peter Sobot](https://github.com/psobot)
2. [Stephen Martinis](https://github.com/moowiz2020)

# nginx-behavior

Project to test nginx undocumented behaviors.

Examples:

* How nginx handle `Cache-Control` `max-age` and `s-maxage`?
* Which is the precedence of `proxy_cache_valid` directive and these cache headers?
* Request cookies change how cache is handled?
* Response `Set-Cookie` avoid cache?

## How to run it

Start nginx and httpbin defined in docker-compose:

    $ docker-compose up -d
    
Install Python dependencies:

    $ pip install -r requirements.txt
    
Run pytest tests:

    $ pytest test.py

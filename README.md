Installing a Flask webapp on a Digital Ocean VPS (or Linode, etc.)
==================================================================

Here I sum up how to install a Flask webapp on a Digital Ocean VPS that
has Ubuntu Linux on it. The following topics will be covered:
* server configuration
* the big picture
* Nginx
* a simple Flask app in a virtual environment served by gunicorn
* gunicorn is started automatically with an upstart script

server configuration
--------------------
See <https://github.com/jabbalaci/DigitalOceanNotes> for more info.

the big picture
---------------
So, you have a Flask app that works well on your local machine and you want to
share it with the world. Instead of a PaaS (like Heroku for instance) you want
to host it on a virtual private server (VPS). How to do it?

When you buy the VPS and receive its IP and root password, spend some time
with its basic configuration. I wrote about it here: <https://github.com/jabbalaci/DigitalOceanNotes>.

Then, we will need a real web server that will serve the pages of our
Flask application. Our choice will be Nginx. Nginx will listen on the
standard http port (80) and forward every request to port 9000.

On port 9000 an application server namely gunicorn will run. This application
server will run our Python application. Nginx will handle static files (like
CSS, images, etc.) itself. If our Python app is called, then Nginx forwards the
request to Gunicorn who executes your Flask app, returns the result to Nginx,
who will return that result to the client.

If gunicorn dies for some reason, we want it to restart automatically. An
upstart script will do exactly this.

Nginx
-----
Install Nginx:

    $ sudo apt-get install nginx

If you use UFW (firewall), then don't forget to open port 80:

    $ sudo ufw status verbose    # verify what's open
    $ sudo ufw allow 80/tcp      # open port 80

Verify if nginx is running:

    $ sudo service nginx status
    $ sudo service nginx start    # start nginx (if it was not running)

Verify it in your browser. Visit `http://1.2.3.4` (instead of `1.2.3.4` use
the IP address of your VPS).

Flask app
---------
Let's put Nginx aside for a while and concentrate on our Flask app. Here,
in this repo you can find a simple sample app that I will use for the
demonstration. It was written in Python 3.

My Flask app will be here: `/home/demo/projects/ave_caesar`. Its virtual
environment is located in a dedicated folder here: `/home/demo/.virtualenvs/ave_caesar`.

Create a virtual environment for the project, activate the environment and
install the requirements. Start the app with `./main.py` and open it in
your browser: `http://1.2.3.4:9000`. If you use UFW, make port 9000 open.
You should see an image and a text below it. If it's OK, then stop `main.py`
(it is running in debug mode and the host is '0.0.0.0', which means that
anybody can visit your app). Debug mode is absolutely not recommended in a
production environment.

The next step will be to run our app with Gunicorn instead of the built-in
dev server of Flask. While the virt. env. is active, install `gunicorn` and
`gevent`:

    $ pip install gunicorn gevent

And now start the application with Gunicorn (the virt. env. is still activated):

    $ ./01_start_with_gunicorn.py

Again, visit `http://1.2.3.4:9000`. You should see the same page, however
this time it's served by Gunicorn! If it's OK, then stop gunicorn (press Ctrl-C).

Configure Nginx to forward to port 9000
---------------------------------------
Now let's configure Nginx to forward requests that arrive to port 80 to
port 9000.

The prompt `#` indicates the root prompt, while `$` is the prompt of normal
users.

    # cd /etc/nginx
    # cd sites-available
    # vi flask

Add the following content:

    upstream app_server {
        server 127.0.0.1:9000 fail_timeout=0;
    }

    server {
        listen 80 default_server;
        listen [::]:80 default_server ipv6only=on;

        client_max_body_size 4G;
        server_name _;

        keepalive_timeout 5;

        # your Flask project's static files - amend as required
        location /static {
            alias /home/demo/projects/ave_caesar/static;
        }

        location / {
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header Host $http_host;
            proxy_redirect off;
            proxy_pass http://app_server;
        }
    }

Here `app_server` is a unique ID. Thus, if you want to serve later another
webapp, and you make a copy of this file, rename `app_server` to something else
in the copy.

What does this config file do? When something arrives at port 80, redirect it
to port 9000.

Add a symbolic link to `sites-enabled` that points on this file:

    # cd /etc/nginx/sites-enabled
    # rm default    # remove the default
    # ln -s ../sites-available/flask
    # ls -al

Restart nginx:

    # service nginx restart
    # service nginx status

Let's test if redirection from port 80 -> port 9000 works
---------------------------------------------------------
Before moving to Upstart, let's test if the redirection works. Go to the
project folder of the webapp, activate the virt. env., and start gunicorn
like before:

    $ ./01_start_with_gunicorn.py

The address `http://1.2.3.4:9000` should work. But now remove the port and
try simply `http://1.2.3.4`. You may have to clear the cache, force reload
the page (Ctrl-r), but you should see our basic app. And this goes through
Nginx!

If it works, then stop gunicorn. If you have UFW, at this point you can
hide again port 9000 if you want.

What next?
----------
We are close to victory. In the previous section we started gunicorn manually.
But we want gunicorn to start automatically upon boot. An Upstart script will
do exactly that:

    # vi /etc/init/gunicorn.conf

Add the following content:

    description "Gunicorn daemon for a Flask project"

    start on (local-filesystems and net-device-up IFACE=eth0)
    stop on runlevel [!12345]

    # If the process quits unexpectadly trigger a respawn
    respawn

    setuid demo
    setgid demo

    script
        . "/home/demo/.virtualenvs/ave_caesar/bin/activate"
        cd /home/demo/projects/ave_caesar
        exec gunicorn --config /etc/gunicorn.d/gunicorn.py  main:app
    end script

The webapp is in the HOME folder of the user `demo`, who is in the group `demo`.
The app will run under his/her name, that's what the lines `setuid` and
`setgid` mean. How to verify:

    $ cd /home/demo/projects
    $ ls -al
    drwxr-xr-x  5 demo demo 4096 Mar 21 20:27 ave_caesar

See? It's `demo` and `demo`.

In the "script" block you specify commands that are executed by the "sh" shell.
Not by "bash" but by "sh". Why is it so important? Because "source" in "sh" is
unknown! It's "." in "sh", and if you write "source", the script fails. So,
what does the "script" block do? First, activate the virt. env. of the
webapp. Second, enter the project directory. Third, start the app with
gunicorn. Note that `gunicorn` is executed in the virt. env.! You don't need
to install it globally with `sudo`! Additional settings are in the
`/etc/gunicorn.d/gunicorn.py` file that we will see in the next section.

additional settings of gunicorn
-------------------------------
Let's create `/etc/gunicorn.d/gunicorn.py`:

    # vi /etc/gunicorn.d/gunicorn.py

If the folder `/etc/gunicorn.d` doesn't exist, then create it first.

Add the following content:

    """gunicorn WSGI server configuration."""
    from multiprocessing import cpu_count
    from os import environ

    def max_workers():
        return cpu_count() * 2 + 1

    max_requests = 1000
    worker_class = 'gevent'
    workers = max_workers()

    name = 'ave_caesar'
    bind = '127.0.0.1:9000'
    pidfile = 'gunicorn_from_upstart.pid'

    accesslog = 'gunicorn_access.log'
    errorlog = 'gunicorn_error.log'

The process `gunicorn` will listen on port 9000. The accesslog and errorlog
files are useful for debugging and monitoring. The PID of the gunicorn process
will be written in a file. All these three files will be written to the root
folder of the webapp.

start the upstart script
------------------------
Now let's try to start the upstart script:

    # service gunicorn start    # wait a bit, then check the status
    # service gunicorn status

If it runs for the first time, you can drink a champagne :) If gunicorn didn't
start, then check out its log file. Open a new terminal and start monitoring
its end:

    # tail -f /var/log/upstart/gunicorn.log

With these error messages it will be much easier to find the problem.

502 Bad Gateway
---------------
It means there is a problem between the communication of Nginx and Gunicorn.

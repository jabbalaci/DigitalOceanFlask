Installing a Flask webapp on a Digital Ocean VPS (or Linode, etc.)
==================================================================

Here I sum up how to install a Flask webapp on a Digital Ocean VPS that
has Ubuntu Linux on it. The following topics will be covered:
* server configuration
* the big picture
* Nginx
* a simple Flask app in a virtual environment served by gunicorn
* gunicorn is started automatically upon boot

Originally I wrote these notes for Ubuntu 14.04, but later it was updated
for Ubuntu 16.04. Both versions are available:

* [Ubuntu 14.04](ubuntu_14_04.md) -- gunicorn is started with upstart
* [Ubuntu 16.04](ubuntu_16_04.md) -- gunicorn is started with systemd

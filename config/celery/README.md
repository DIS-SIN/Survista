# Celery Configuration for production server

These are the script files needed to configure celery for daemonization in production environments. The initd_celery.sh must go to:

```sh
/etc/init.d/celeryd
```

To do this use the mv command

```sh
$ sudo mv ./celery/initd_celery.sh /etc/init.d/celeryd
```

You need to also put the default_celery.sh file in /etc/default/celeryd. This file contains the nessecary variables needed to configure the celery workers.

```sh
$ sudo mv ./celery/default_celery.sh /etc/default/celeryd
```

Note

You will have to manually create the celery user which will run the workers and the usergroup that it belongs to. The user should be unpriveledged for security reasons.

```sh
$ sudo groupadd celery
$ sudo adduser celery
#make a memorable password
$ sudo usermod -aG celery celery
```

Note you may also choose to run the worker as the current user however this may be unsecure. To do this go to the default_celery.sh file and delete the following

```sh
CELERYD_USER="celery"
CELERYD_GROUP="celery"
```

Once you have completed these steps start the workers

```sh
$ system celeryd start
```

If this fails try the following

```sh
$ sudo /etc/init.d/celeryd start
```

I am currently working on containerizing this app so that these complexities can be avoided and the behaviour is unified no matter where deployed. If you are experiencing issues please do open an issue and I will try and respond ASAP. 
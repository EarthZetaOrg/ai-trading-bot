# Using earthzetaorg with Docker

## Install Docker

Start by downloading and installing Docker CE for your platform:

* [Mac](https://docs.docker.com/docker-for-mac/install/)
* [Windows](https://docs.docker.com/docker-for-windows/install/)
* [Linux](https://docs.docker.com/install/)

Once you have Docker installed, simply prepare the config file (e.g. `config.json`) and run the image for `earthzetaorg` as explained below.

## Download the official earthzetaorg docker image

Pull the image from docker hub.

Branches / tags available can be checked out on [Dockerhub](https://hub.docker.com/r/earthzetaorgorg/earthzetaorg/tags/).

```bash
docker pull earthzetaorgorg/earthzetaorg:develop
# Optionally tag the repository so the run-commands remain shorter
docker tag earthzetaorgorg/earthzetaorg:develop earthzetaorg
```

To update the image, simply run the above commands again and restart your running container.

Should you require additional libraries, please [build the image yourself](#build-your-own-docker-image).

!!! Note Docker image update frequency
    The official docker images with tags `master`, `develop` and `latest` are automatically rebuild once a week to keep the base image uptodate.
    In addition to that, every merge to `develop` will trigger a rebuild for `develop` and `latest`.

### Prepare the configuration files

Even though you will use docker, you'll still need some files from the github repository.

#### Clone the git repository

Linux/Mac/Windows with WSL

```bash
git clone https://github.com/earthzetaorg/earthzetaorg.git
```

Windows with docker

```bash
git clone --config core.autocrlf=input https://github.com/earthzetaorg/earthzetaorg.git
```

#### Copy `config.json.example` to `config.json`

```bash
cd earthzetaorg
cp -n config.json.example config.json
```

> To understand the configuration options, please refer to the [Bot Configuration](configuration.md) page.

#### Create your database file

Production

```bash
touch tradesv3.sqlite
````

Dry-Run

```bash
touch tradesv3.dryrun.sqlite
```

!!! Note
    Make sure to use the path to this file when starting the bot in docker.

### Build your own Docker image

Best start by pulling the official docker image from dockerhub as explained [here](#download-the-official-docker-image) to speed up building.

To add additional libraries to your docker image, best check out [Dockerfile.technical](https://github.com/earthzetaorg/earthzetaorg/blob/develop/Dockerfile.technical) which adds the [technical](https://github.com/earthzetaorg/technical) module to the image.

```bash
docker build -t earthzetaorg -f Dockerfile.technical .
```

If you are developing using Docker, use `Dockerfile.develop` to build a dev Docker image, which will also set up develop dependencies:

```bash
docker build -f Dockerfile.develop -t earthzetaorg-dev .
```

!!! Note
    For security reasons, your configuration file will not be included in the image, you will need to bind mount it. It is also advised to bind mount an SQLite database file (see the "5. Run a restartable docker image" section) to keep it between  updates.

#### Verify the Docker image

After the build process you can verify that the image was created with:

```bash
docker images
```

The output should contain the earthzetaorg image.

### Run the Docker image

You can run a one-off container that is immediately deleted upon exiting with the following command (`config.json` must be in the current working directory):

```bash
docker run --rm -v `pwd`/config.json:/earthzetaorg/config.json -it earthzetaorg
```

!!! Warning
    In this example, the database will be created inside the docker instance and will be lost when you will refresh your image.

#### Adjust timezone

By default, the container will use UTC timezone.
Should you find this irritating please add the following to your docker commands:

##### Linux

``` bash
-v /etc/timezone:/etc/timezone:ro

# Complete command:
docker run --rm -v /etc/timezone:/etc/timezone:ro -v `pwd`/config.json:/earthzetaorg/config.json -it earthzetaorg
```

##### MacOS

There is known issue in OSX Docker versions after 17.09.1, whereby `/etc/localtime` cannot be shared causing Docker to not start. A work-around for this is to start with the following cmd.

```bash
docker run --rm -e TZ=`ls -la /etc/localtime | cut -d/ -f8-9` -v `pwd`/config.json:/earthzetaorg/config.json -it earthzetaorg
```

More information on this docker issue and work-around can be read [here](https://github.com/docker/for-mac/issues/2396).

### Run a restartable docker image

To run a restartable instance in the background (feel free to place your configuration and database files wherever it feels comfortable on your filesystem).

#### Move your config file and database

The following will assume that you place your configuration / database files to `~/.earthzetaorg`, which is a hidden directory in your home directory. Feel free to use a different directory and replace the directory in the upcomming commands.

```bash
mkdir ~/.earthzetaorg
mv config.json ~/.earthzetaorg
mv tradesv3.sqlite ~/.earthzetaorg
```

#### Run the docker image

```bash
docker run -d \
  --name earthzetaorg \
  -v ~/.earthzetaorg/config.json:/earthzetaorg/config.json \
  -v ~/.earthzetaorg/user_data/:/earthzetaorg/user_data \
  -v ~/.earthzetaorg/tradesv3.sqlite:/earthzetaorg/tradesv3.sqlite \
  earthzetaorg --db-url sqlite:///tradesv3.sqlite --strategy MyAwesomeStrategy
```

!!! Note
    db-url defaults to `sqlite:///tradesv3.sqlite` but it defaults to `sqlite://` if `dry_run=True` is being used.
    To override this behaviour use a custom db-url value: i.e.: `--db-url sqlite:///tradesv3.dryrun.sqlite`

!!! Note
    All available bot command line parameters can be added to the end of the `docker run` command.

### Monitor your Docker instance

You can use the following commands to monitor and manage your container:

```bash
docker logs earthzetaorg
docker logs -f earthzetaorg
docker restart earthzetaorg
docker stop earthzetaorg
docker start earthzetaorg
```

For more information on how to operate Docker, please refer to the [official Docker documentation](https://docs.docker.com/).

!!! Note
    You do not need to rebuild the image for configuration changes, it will suffice to edit `config.json` and restart the container.

### Backtest with docker

The following assumes that the download/setup of the docker image have been completed successfully.
Also, backtest-data should be available at `~/.earthzetaorg/user_data/`.

```bash
docker run -d \
  --name earthzetaorg \
  -v /etc/localtime:/etc/localtime:ro \
  -v ~/.earthzetaorg/config.json:/earthzetaorg/config.json \
  -v ~/.earthzetaorg/tradesv3.sqlite:/earthzetaorg/tradesv3.sqlite \
  -v ~/.earthzetaorg/user_data/:/earthzetaorg/user_data/ \
  earthzetaorg --strategy AwsomelyProfitableStrategy backtesting
```

Head over to the [Backtesting Documentation](backtesting.md) for more details.

!!! Note
    Additional bot command line parameters can be appended after the image name (`earthzetaorg` in the above example).

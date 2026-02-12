# Catena-D-Demo

## Community Solid Server Setup

Make sure you have [Node.js](https://nodejs.org/en/) 18.0 or higher.
If this is your first time using Node.js,
you can find instructions on how to do this [here](https://nodejs.org/en/download/package-manager).

To persist your pod's contents between restarts, use:

```basd
npx @solid/community-server -c @css:config/file.json -f pod_data
```
Now visit your brand new server at [http://localhost:3000/](http://localhost:3000/)!

Create three users and their corresponding pods called **bosch-pod**, **maintenance-pod**, and **dpp-pod**.

* account1: bosch@test.com
* password: 123456
* pod name: bosch-pod

* account2: maintenance@test.com
* password: 123456
* pod name: maintenance-pod

* account3: dpp@test.com
* password: 123456
* pod name: dpp-pod



The example data is located at [Catena-D_data](./Catena-D_data) folder.
You need to copy ttl files and acl files to corresponding pod folders.


```basd
cp ./Catena-D_data/bosch-pod/heatpump-observation.ttl ./pod_data/bosch-pod/
cp ./Catena-D_data/bosch-pod/heatpump-observation.ttl.acl ./pod_data/bosch-pod/
cp ./Catena-D_data/maintenance-pod/heatpump-maintenance.ttl ./pod_data/maintenance-pod/
cp ./Catena-D_data/maintenance-pod/heatpump-maintenance.ttl.acl ./pod_data/maintenance-pod/
cp ./Catena-D_data/dpp-pod/heatpump-dpp.ttl ./pod_data/dpp-pod/
cp ./Catena-D_data/dpp-pod/heatpump-dpp.ttl.acl ./pod_data/dpp-pod/
```

## Miravi Setup

### Prerequisites

* Node >= 18 with npm
* A Linux platform with a bash shell

### Getting started

To install:

```bash
cd miravi-a-linked-data-viewer
```

```bash
cd main
```

The Web application is located in directory `main`.

```bash
npm install
```

To select the configuration for [Catena-D](./miravi-a-linked-data-viewer/main/configs/Catena-D/):

```bash
node scripts/select-config.cjs Catena-D
```

To run the Web application in development mode:

```bash
npm run dev
```

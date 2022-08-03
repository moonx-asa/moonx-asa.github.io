# SecureWalletAuth
SecureWalletAuth is a complete example implementation of Authentication by Wallet. With the strategies demonstrated by the code in this project, algorand/python developers can allow users to authenticate their accounts by connecting their Algorand Wallets (currently supported are the MyAlgoConnect, Algosigner and WalletConnect APIs). A working demo can be found at [swalletauth.asyte.io](https://swalletauth.asyte.io/).

## How to approach this project
The framework laid out in this project can be used as a starting point for developing python based web applications. However, lets be honest, you probably already have something built for your preferred tech stack. In this case, elements from the frontend can still be used to interface with the supported Algorand wallet connection APIs.

### Using SecureWalletAuth as a starting point
Examples in this project are laid out in a way that can be extended: you can use this to build your python web application! But first you should learn how to launch demo application

#### Setup
SecureWalletAuth requires `python3.9` or greater. It is also suggested that this app be run using a virtual environment.

```
$ git clone https://github.com/airsho/Secure-WalletAuth.git ~/path/to/web/app
$ cd ~/path/to/web/app
$ python3.9 -m venv env
$ source env/bin/activate
(env) $ pip install -r requirements.txt
```

After `pip` installs all the dependencies, it is important to edit the `backend/settings.py` file to reflect your local settings. After this, you can launch the web app.

```
(env) $ python -m backend.launch
```

Further automation such as supervisor setup are recommended for production websites.

#### Important Files
As you have seen, the application settings are loaded from the `backend/settings.py` file. In the sanic framework endpoints are represented by blueprints which can be found in the `backend/blueprints` directory. **When adding new blueprints, it is important to tell the launcher to load the module** by editing `backend/launch.py:enabled_blueprints`

# About
This linkedin data scraper is developed using selenium and flask

# Installation

1. Assumes you have working python installation ( 3.8.10)
2. install virtual env if not already installed
3. create a working directory and create a virtual env inside the working directory and activate it
4. install selenium inside the virtual env
5. install flask inside virtual env
6. install Flask-WTF
7. install requests library for python
8. Extract this repo contents inside the working directory.


## Usage
Inside the working directory, open a terminal and run the following command.
```
flask --app main  --debug run
```
Then go to a browser, navigate to 
```
127.0.0.1:port_number
```  
`Port Number is the port on which flask is running`

It will ask for login, give creds. Creds are stored in users.json inside the repo.
Then it will redirect to linked in login screen, give the creds for linked in, click Signin. Upon successful signin, it will redirect to get data page, where you have option to get connections data or personal data. click the desired button.
<br>
<br>
Personal details page will just display email id.
Get details page will also have pagination option, once you go to page, it will display page 0. To change page number, enter desired page number and click get data.

## License

[MIT](https://choosealicense.com/licenses/mit/)
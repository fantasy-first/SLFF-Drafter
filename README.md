## SLFF-Drafter


##### Setup

Requires Python 3.6+ (may work on earlier versions, we dunno)

Create a file in the `config` folder named `.secrets.yaml`, insert the following code block, and store your Discord bot token:

```yaml
default:	
    discord:	
        token: "YOUR_TOKEN_HERE" 
```

Go to this page and enable the Google Sheets API in order to download a `credentials.json` file:
https://developers.google.com/sheets/api/quickstart/python


We recommend you create a [virtualenv](https://virtualenv.pypa.io/en/latest/) to handle dependencies.

```bash
$ pip install -r requirements.txt
$ python bot.py
```

If you add a new dependency, add it to `requirements.txt`:

```bash
$ pip freeze > requirements.txt
```

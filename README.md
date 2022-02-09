# Restaurant Bot

A Rasa chatbot that finds restaurants and coffee houses using the FOURSQUARE Places API

In order to use the chatbot first install Rasa in a virtual environment. Activate the virtual environment, and then run the following command.

```terminal
rasa train
```

Once the model is trained, in one terminal run the following command.

``` terminal
rasa run actions
```

Then in another terminal run the following command

```` terminal
rasa run --enable-api --cors='*'
```
Finally open the index.html file in the Chatbot-UI folder using your browser.

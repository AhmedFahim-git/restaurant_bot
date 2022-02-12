# Restaurant Bot

Restaurant Bot is a simple chat bot that searches for restaurants, coffee houses, or both near given locations.

This is a sample project. It uses [Rasa](https://rasa.com/) as the chat bot framework and the [FOURSQUARE Places API](https://developer.foursquare.com/docs/places-api-overview) to search for the places of interest.

In order to use the chatbot first install Rasa in a virtual environment and activate it. Clone and move into the repository, and run the following command.

```terminal
rasa train
```

This may take a while as it trains the machine learning model.

Once the model is trained, in one terminal run the following command.

``` terminal
rasa run actions
```

Then in another terminal run the following command

``` terminal
rasa run --enable-api --cors='*'
```

Finally open the index.html file in the Chatbot-UI folder using your browser.

![The final chat bot!](/images/chatbot_UI.gif "The end result")

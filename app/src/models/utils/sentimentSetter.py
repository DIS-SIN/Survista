# Simple utility to set sentiment variables based on 


from neomodel.contrib import SemiStructuredNode
from flask import current_app

class SentimentSetter:
    @staticmethod
    def setSentimentVariables(model: SemiStructuredNode) -> None:
        if current_app.config.get('GoogleAPIKey'):
            model.googleSentimentScore = 0.0
            model.googleMagnitudeScore = 0.0
        if current_app.config.get('AmazonAPIKey'):
            model.amazonSentimentScoreMixed = 0.0
            model.amazonSentimentScorePositive = 0.0
            model.amazonSentimentScoreNeutral = 0.0
            model.amazonSentimentScoreNegative = 0.0
            model.amazonSentimentPrediction = "No Prediction"
        if current_app.config.get('AzureAPIKey'):
            model.azureSentimentScore = 0.0
        model.sentimentCalculated = False
        model.sentimentSet = True

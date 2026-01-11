from textblob import TextBlob
from datetime import datetime
from sqlalchemy.orm import Session
from app.db import models

def analyze_texts(symbol: str, texts: list[str], db: Session):
    results = []

    for text in texts:
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity

        if polarity > 0.1:
            label = "positive"
        elif polarity < -0.1:
            label = "negative"
        else:
            label = "neutral"

        sentiment = models.Sentiment(
            asset=symbol.upper(),
            label=label,
            score=polarity,
            timestamp=datetime.utcnow(),
            source="mock",
            source_url=None,
            meta={"text": text}
        )

        db.add(sentiment)
        results.append(sentiment)

    db.commit()
    return results


def analyze_mock_sentiment(symbol: str, db: Session):
    
    mock_texts = [
        f"{symbol} is doing great!",
        f"People are buying {symbol} a lot today.",
        f"{symbol} market is uncertain.",
        f"Many traders are afraid {symbol} may drop.",
        f"{symbol} looks stable overall."
    ]
    return analyze_texts(symbol, mock_texts, db)

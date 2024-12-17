from src.analysis.sentiment_analyzer import SentimentAnalyzer
import pandas as pd

def test_sentiment_analysis():
    # Initialize the analyzer (using spaCy by default)
    analyzer = SentimentAnalyzer()
    
    # Test single text analysis
    text = "I love this product! It's amazing and works perfectly."
    result = analyzer.analyze_text(text)
    print("\nSingle text analysis:")
    print(f"Text: {text}")
    print(f"Result: {result}")
    
    # Test DataFrame analysis
    df = pd.DataFrame({
        'text': [
            "This is great!",
            "I'm not happy with the service",
            "The product is okay, nothing special",
            "Absolutely fantastic experience!"
        ]
    })
    
    print("\nDataFrame analysis:")
    result_df = analyzer.analyze_dataframe(df, 'text')
    print(result_df[['text', 'sentiment_score', 'sentiment']])
    
    # Test aggregate sentiment
    texts = [
        "Excellent product, highly recommended!",
        "Not what I expected, quite disappointed",
        "It's alright, does the job",
        "Best purchase ever, absolutely love it!"
    ]
    
    print("\nAggregate sentiment analysis:")
    aggregate_result = analyzer.get_aggregate_sentiment(texts)
    print(aggregate_result)

if __name__ == "__main__":
    test_sentiment_analysis()

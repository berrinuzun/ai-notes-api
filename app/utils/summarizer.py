from transformers import pipeline

try:
    summarizer = pipeline(
                            "summarization",
                            model="sshleifer/distilbart-cnn-12-6",
                            device=-1  
    )
except Exception as e:
    raise RuntimeError(f"Failed to load summarization model: {e}")


def summarize_text(text: str) -> str:
    
    try:
        summary_list = summarizer(
            text,
            max_length=60,
            min_length=20,
            do_sample=False
        )
        return summary_list[0]["summary_text"]
    except Exception as e:
        raise RuntimeError(f"Summarization failed: {e}")

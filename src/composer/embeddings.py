from sentence_transformers import SentenceTransformer
from composer.data_types import SentMail

def generate_embeddings(sent_email: SentMail) -> SentMail:
    # Load the sentence transformer model
    model = SentenceTransformer('all-MiniLM-L6-v2')
    # Generate embeddings for the message
    embeddings = model.encode(sent_email.message)
    # Store embeddings in the SentMail object
    sent_email.embeddings = embeddings.tolist()
    return sent_email

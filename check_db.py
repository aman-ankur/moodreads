from pymongo import MongoClient

def main():
    # Connect to MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    db = client['moodreads']
    
    # Get all books
    print("Books in database:")
    for book in db.books.find({}, {'title': 1, 'author': 1, '_id': 0}):
        print(f"- {book['title']} by {book['author']}")

if __name__ == "__main__":
    main() 
from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI()

books = [
    {"id": 1, "title": "Python Crash Course", "author": "Eric Matthes", "pages": 560, "genre": "Programming", "available": True},
    {"id": 2, "title": "Clean Code", "author": "Robert C. Martin", "pages": 464, "genre": "Software Engineering", "available": True},
    {"id": 3, "title": "The Pragmatic Programmer", "author": "Andrew Hunt", "pages": 352, "genre": "Programming", "available": True},
    {"id": 4, "title": "Automate the Boring Stuff", "author": "Al Sweigart", "pages": 504, "genre": "Programming", "available": True},
    {"id": 5, "title": "Design Patterns", "author": "Erich Gamma", "pages": 395, "genre": "Software Engineering", "available": True},
    {"id": 6, "title": "Deep Learning with Python", "author": "Francois Chollet", "pages": 384, "genre": "AI", "available": True},
    {"id": 7, "title": "Introduction to Algorithms", "author": "Thomas H. Cormen", "pages": 1312, "genre": "Computer Science", "available": True},
    {"id": 8, "title": "Effective Python", "author": "Brett Slatkin", "pages": 256, "genre": "Programming", "available": True},
    {"id": 9, "title": "Python Tricks", "author": "Dan Bader", "pages": 302, "genre": "Programming", "available": True},
    {"id": 10, "title": "Fluent Python", "author": "Luciano Ramalho", "pages": 792, "genre": "Programming", "available": True}
]
members = [
    {"id": 1, "name": "Alice Johnson"},
    {"id": 2, "name": "Bob Smith"},
    {"id": 3, "name": "Charlie Lee"},
    {"id": 4, "name": "Diana Prince"},
    {"id": 5, "name": "Ethan Hunt"}
]
borrow_records = [
    {"id": 1, "book_id": 2, "member_id": 1, "status": "borrowed"},
    {"id": 2, "book_id": 4, "member_id": 2, "status": "returned"},
    {"id": 3, "book_id": 5, "member_id": 3, "status": "borrowed"}
]

book_id_counter = 1
member_id_counter = 1
borrow_id_counter = 1

class Book(BaseModel):
    title: str = Field(..., min_length=1)
    author: str = Field(..., min_length=2)
    pages: int = Field(..., gt=0)
    genre: Optional[str] = None

class Member(BaseModel):
    name: str = Field(..., min_length=2)

class Borrow(BaseModel):
    book_id: int
    member_id: int

def find_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book
    return None

def find_member(member_id: int):
    for member in members:
        if member["id"] == member_id:
            return member
    return None

def find_borrow(borrow_id: int):
    for record in borrow_records:
        if record["id"] == borrow_id:
            return record
    return None

def filter_books_logic(author=None, genre=None):
    result = books
    if author is not None:
        result = [b for b in result if author.lower() in b["author"].lower()]
    if genre is not None:
        result = [b for b in result if b.get("genre") and genre.lower() in b["genre"].lower()]
    return result

@app.get("/")
def home():
    return {"message": "Library API Running"}

@app.get("/books")
def get_books():
    return books

@app.get("/books/summary")
def books_summary():
    total = len(books)
    available = len([b for b in books if b["available"]])
    return {"total_books": total, "available_books": available}

@app.get("/members")
def get_members():
    return members

@app.get("/books/search")
def search_books(keyword: str):
    result = [
        b for b in books
        if keyword.lower() in b["title"].lower()
        or keyword.lower() in b["author"].lower()
    ]
    if not result:
        return {"message": "No books found"}
    return result

@app.get("/books/sort")
def sort_books(sort_by: str = "title", order: str = "asc"):
    if sort_by not in ["title", "pages"]:
        raise HTTPException(status_code=400, detail="Invalid sort field")

    reverse = True if order == "desc" else False
    return sorted(books, key=lambda x: x[sort_by], reverse=reverse)

@app.get("/books/paginate")
def paginate_books(page: int = 1, limit: int = 3):
    start = (page - 1) * limit
    end = start + limit
    total_pages = (len(books) + limit - 1) // limit

    return {
        "page": page,
        "total_pages": total_pages,
        "data": books[start:end]
    }

@app.get("/books/browse")
def browse_books(
    search: Optional[str] = None,
    sort_by: Optional[str] = None,
    order: str = "asc",
    page: int = 1,
    limit: int = 3
):
    result = books

    # search
    if search:
        result = [
            b for b in result
            if search.lower() in b["title"].lower()
            or search.lower() in b["author"].lower()
        ]

    # sort
    if sort_by:
        reverse = True if order == "desc" else False
        result = sorted(result, key=lambda x: x.get(sort_by, ""), reverse=reverse)

    # pagination
    start = (page - 1) * limit
    end = start + limit
    total_pages = (len(result) + limit - 1) // limit

    return {
        "total_results": len(result),
        "total_pages": total_pages,
        "data": result[start:end]
    }

@app.get("/books/filter")
def filter_books(author: Optional[str] = None, genre: Optional[str] = None):
    return filter_books_logic(author, genre)

@app.post("/books", status_code=status.HTTP_201_CREATED)
def add_book(book: Book):
    global book_id_counter

    # duplicate check
    for b in books:
        if b["title"].lower() == book.title.lower():
            raise HTTPException(status_code=400, detail="Book already exists")

    new_book = book.dict()
    new_book["id"] = book_id_counter
    new_book["available"] = True

    books.append(new_book)
    book_id_counter += 1

    return new_book

@app.put("/books/{book_id}")
def update_book(book_id: int, book: Book):
    existing = find_book(book_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Book not found")

    update_data = book.dict(exclude_unset=True)
    for key, value in update_data.items():
        existing[key] = value

    return existing

@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    book = find_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    if not book["available"]:
        raise HTTPException(status_code=400, detail="Book is currently borrowed")

    books.remove(book)
    return {"message": "Book deleted successfully"}

@app.get("/books/{book_id}")
def get_book(book_id: int):
    book = find_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@app.post("/members", status_code=201)
def add_member(member: Member):
    global member_id_counter

    new_member = member.dict()
    new_member["id"] = member_id_counter

    members.append(new_member)
    member_id_counter += 1

    return new_member

@app.post("/borrow")
def borrow_book(data: Borrow):
    global borrow_id_counter

    book = find_book(data.book_id)
    member = find_member(data.member_id)

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    if not book["available"]:
        raise HTTPException(status_code=400, detail="Book already borrowed")

    book["available"] = False

    record = {
        "id": borrow_id_counter,
        "book_id": data.book_id,
        "member_id": data.member_id,
        "status": "borrowed"
    }

    borrow_records.append(record)
    borrow_id_counter += 1

    return record


@app.post("/return/{borrow_id}")
def return_book(borrow_id: int):
    record = find_borrow(borrow_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    if record["status"] == "returned":
        raise HTTPException(status_code=400, detail="Already returned")

    book = find_book(record["book_id"])
    book["available"] = True

    record["status"] = "returned"
    return {"message": "Book returned successfully"}


@app.get("/borrow/list")
def get_borrow_records():
    return borrow_records
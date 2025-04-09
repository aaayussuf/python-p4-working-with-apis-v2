import requests
import json
from typing import List, Optional, Dict, Union
from functools import lru_cache
from datetime import datetime


class OpenLibraryAPI:
    """
    A class to interact with the Open Library API for book searches.
    Handles searching for books by title, author, ISBN, etc.
    Includes caching, cover images, descriptions and sorting.
    """
    
    BASE_URL = "https://openlibrary.org/search.json"
    COVER_URL = "https://covers.openlibrary.org/b/id/{}-L.jpg"
    
    def __init__(self):
        self.session = requests.Session()
        self.cache = {}
    
    @lru_cache(maxsize=100)
    def search_books(
        self,
        title: Optional[str] = None,
        author: Optional[str] = None,
        isbn: Optional[str] = None,
        fields: List[str] = ["title", "author_name", "first_publish_year", 
                           "publisher", "isbn", "cover_i", "description"],
        limit: int = 5,
        page: int = 1,
        sort: Optional[str] = None
    ) -> Dict:
        """
        Search for books using various parameters with caching.
        
        Args:
            title: Book title to search for
            author: Author name to search for
            isbn: ISBN to search for
            fields: List of fields to return in results
            limit: Number of results to return (max 100)
            page: Page number for pagination
            sort: Sort field ('new', 'old', 'title')
            
        Returns:
            Dictionary containing search results
            
        Raises:
            ValueError: If no search parameters provided
            requests.exceptions.RequestException: If API request fails
        """
        if not any([title, author, isbn]):
            raise ValueError("At least one search parameter (title, author, or isbn) must be provided")
            
        params = {}
        if title:
            params["title"] = title.replace(" ", "+")
        if author:
            params["author"] = author.replace(" ", "+")
        if isbn:
            params["isbn"] = isbn.replace(" ", "+")
            
        params["fields"] = ",".join(fields)
        params["limit"] = min(limit, 100)  # API max limit is 100
        params["page"] = page
        
        # Add sorting if specified
        if sort == "new":
            params["sort"] = "new"
        elif sort == "old":
            params["sort"] = "old"
        elif sort == "title":
            params["sort"] = "title"
        
        try:
            response = self.session.get(self.BASE_URL, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            raise

    def format_search_result(self, result: Dict) -> str:
        """
        Format a single search result into a readable string with cover image.
        
        Args:
            result: A single book result from the API
            
        Returns:
            Formatted string with book information
        """
        title = result.get("title", "Unknown Title")
        authors = ", ".join(result.get("author_name", ["Unknown Author"]))
        year = result.get("first_publish_year", "Unknown Year")
        publisher = ", ".join(result.get("publisher", ["Unknown Publisher"]))
        isbns = ", ".join(result.get("isbn", ["Unknown ISBN"]))
        cover_id = result.get("cover_i")
        description = result.get("description", "No description available")
        
        if isinstance(description, dict):
            description = description.get("value", "No description available")
        
        output = (
            f"Title: {title}\n"
            f"Author(s): {authors}\n"
            f"First Published: {year}\n"
            f"Publisher(s): {publisher}\n"
            f"ISBN(s): {isbns}\n"
            f"Description: {description[:200]}...\n"
        )
        
        if cover_id:
            output += f"Cover: {self.COVER_URL.format(cover_id)}\n"
            
        return output


def display_menu():
    """Display the interactive menu."""
    print("\nOpen Library Book Search")
    print("1. Search by Title")
    print("2. Search by Author")
    print("3. Search by ISBN")
    print("4. Advanced Search")
    print("5. Exit")
    return input("Enter your choice (1-5): ")

def main():
    """Main function with interactive menu."""
    api = OpenLibraryAPI()
    
    while True:
        choice = display_menu()
        
        if choice == "1":
            title = input("Enter book title: ").strip()
            if not title:
                print("Title cannot be empty")
                continue
                
            sort = input("Sort by (new/old/title/none): ").strip().lower()
            sort = sort if sort in ["new", "old", "title"] else None
            
            results = api.search_books(title=title, sort=sort)
            
        elif choice == "2":
            author = input("Enter author name: ").strip()
            if not author:
                print("Author cannot be empty")
                continue
                
            results = api.search_books(author=author)
            
        elif choice == "3":
            isbn = input("Enter ISBN: ").strip()
            if not isbn:
                print("ISBN cannot be empty")
                continue
                
            results = api.search_books(isbn=isbn)
            
        elif choice == "4":
            title = input("Enter title (optional): ").strip() or None
            author = input("Enter author (optional): ").strip() or None
            isbn = input("Enter ISBN (optional): ").strip() or None
            limit = input("Max results (default 5): ").strip()
            limit = int(limit) if limit.isdigit() else 5
            sort = input("Sort by (new/old/title/none): ").strip().lower()
            sort = sort if sort in ["new", "old", "title"] else None
            
            if not any([title, author, isbn]):
                print("At least one search parameter is required")
                continue
                
            results = api.search_books(
                title=title,
                author=author,
                isbn=isbn,
                limit=limit,
                sort=sort
            )
            
        elif choice == "5":
            print("Goodbye!")
            break
            
        else:
            print("Invalid choice, please try again")
            continue
            
        print("\nSearch Results:")
        for i, book in enumerate(results.get("docs", []), 1):
            print(f"\nResult #{i}:")
            print(api.format_search_result(book))
            
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()

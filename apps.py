import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import time
import random
import plotly.express as px
import plotly.graph_objects as go
from streamlit_lottie import st_lottie
import requests

# set page configuration
st.set_page_config(
    page_title="Personal Library Management System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# styling with custom CSS
st.markdown("""
    <style>
        .main-header{
            font-size: 3rem !important;
            color: #FF5733;
            font-weight: bold;
            margin-bottom: 20px;
            text-align: center;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }

        .sub-header{
            font-size: 2rem !important;
            color: #3B82F6;
            font-weight: 600;
            margin-top: 20px;
            margin-bottom: 20px;
         }

        .success-message{
            padding: 10px;
            background-color: #FEF3C7;
            border-left: 5px solid #103981;
            border-radius: 5px;
            }
        .warning-message{
            padding: 10px;
            background-color: #FFEDD5;
            border-left: 5px solid #FBBF24;
            border-radius: 5px;
            }
        .book-card{
            background-color: #F9FAFB;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            border-left: 5px solid #3B82F6;
            transition: transform 0.3s ease;
        }
        .book-card:hover{
            transform: translateY(-5px);
            box-shadow: 0 10px 15px -3px rgba(0,0,0,0.2);
        }
        .read-badge{
            background-color: #D1FAE5;
            color: #065F46;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        .unread-badge{
            background-color: #FEF3C7;
            color: #92400E;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        .action-button{
            margin-right: 0.5rem;
            padding: 10px 20px;
            background-color: #3B82F6;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1rem;
            font-weight: 600;
            transition: background-color 0.3s ease;
        }
        .stButton>button{
        border-radius: 0.375rem;}
    </style>
    """, unsafe_allow_html=True)

# Load Lottie animation
def load_lottieurl(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

if 'library' not in st.session_state:
    st.session_state.library = []
if 'search_result' not in st.session_state:
    st.session_state.search_result = []
if 'book_added' not in st.session_state:
    st.session_state.book_added = False
if 'book_remove' not in st.session_state:
    st.session_state.book_remove = False
if 'current_view' not in st.session_state:
    st.session_state.current_view = "library"


# Load Library
def load_library():
    try:
        if os.path.exists("library.json"):
            with open("library.json", "r") as file:
                try:
                    st.session_state.library = json.load(file)
                    # Validate the library after loading
                    validate_library()
                    return True
                except json.JSONDecodeError:
                    st.error("Error: library.json file is corrupted. Creating a new library.")
                    st.session_state.library = []
                    save_library()
                    return False
        return False
    except Exception as e:
        st.error(f"Error loading library: {e}")
        return False

# save Library
def save_library():
    try:
        with open("library.json", "w") as file:
            json.dump(st.session_state.library, file)
            return True
    except Exception as e:
        st.error(f"Error saving library: {e}")
        return False

# Add a Book to a Library
def add_book(title, author, publication_year, genre, read_status):
    book = {
        "title": title,
        "author": author,
        "publication_year": publication_year,
        "genre": genre,
        "read_status": read_status,
        "added_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state.library.append(book)
    save_library()
    st.session_state.book_added = True
    time.sleep(0.5) #animation delay

# remove a book from library
def remove_book(index):
    if 0 <= index < len(st.session_state.library):
        del st.session_state.library[index]
        save_library()
        st.session_state.book_remove = True
        return True
    return False

# Search for a book in the library
def search_book(search_term, search_by):
    search_term = search_term.lower()
    results = []

    for book in st.session_state.library:
        if search_by == "title" and search_term in book["title"].lower():
            results.append(book)
        elif search_by == "author" and search_term in book["author"].lower():
            results.append(book)
        elif search_by == "genre" and search_term in book["genre"].lower():
            results.append(book)
        elif search_by == "publication_year" and search_term in str(book["publication_year"]):
            results.append(book)
    st.session_state.search_result = results

# calculate library stats
def get_library_stats():
    total_books = len(st.session_state.library)
    read_books = sum([1 for book in st.session_state.library if book["read_status"] == True])
    percent_read = (read_books / total_books) * 100 if total_books > 0 else 0

    genres = {}
    authors = {}
    decades = {}

    for book in st.session_state.library:
        # count genres
        if book["genre"] in genres:
            genres[book["genre"]] += 1
        else:
            genres[book["genre"]] = 1

        # count authors
        if book["author"] in authors:
            authors[book["author"]] += 1
        else:
            authors[book["author"]] = 1

        # count decades
        decade = (book["publication_year"] // 10) * 10  # Calculate the decade
        if decade in decades:  # Check if the decade is already in the dictionary
            decades[decade] += 1  # Increment the count for this decade
        else:
            decades[decade] = 1  # Initialize the count for this decade

    # sort by count
    genres = dict(sorted(genres.items(), key=lambda item: item[1], reverse=True))
    authors = dict(sorted(authors.items(), key=lambda item: item[1], reverse=True))
    decades = dict(sorted(decades.items(), key=lambda item: item[0]))

    return {
        'total_books': total_books,
        'read_books': read_books,
        'percent_read': percent_read,
        'genres': genres,
        'authors': authors,
        'decades': decades
    }

# Create visualizations
def create_visualization(stats):
    if stats['total_books'] > 0:
        fig_read_status = go.Figure(data=[go.Pie(
            labels=["Read", "Not Read"], 
            values=[stats['read_books'], stats['total_books'] - stats['read_books']],
            hole=0.4,
            marker_colors=['#3B82F6', '#FF5733'],
        )])
        fig_read_status.update_layout(
            title_text="Read Vs Unread Books", 
            showlegend=True,
            height=400,
        )
        st.plotly_chart(fig_read_status, use_container_width=True)

    # Bar Chart for Genres
    if stats['genres']:
        genres_df = pd.DataFrame({
            'Genre': list(stats['genres'].keys()),
            'Count': list(stats['genres'].values())
        })
        fig_genres = px.bar(
            genres_df, 
            x='Genre', 
            y='Count',
            title="Books by Genre",
            color='Count',
            color_continuous_scale=px.colors.sequential.Viridis,
        )

        fig_genres.update_layout(
            title_text="Books by Publication Genres",
            xaxis_title="Genres",
            yaxis_title="Number of Books",
            height=400,
        )
        # Display the genre bar chart
        st.plotly_chart(fig_genres, use_container_width=True)

    # Line Chart for Decades
    if stats['decades']:
        decades_df = pd.DataFrame({
            'Decade': [f"{decade}s" for decade in stats['decades'].keys()],
            'Count': list(stats['decades'].values())
        }) 
        fig_decades = px.line(
            decades_df,
            x='Decade',
            y='Count',
            markers=True,
            line_shape='spline',
        ) 
        fig_decades.update_layout(
            title_text="Books by Publication Decade",
            xaxis_title="Decade",
            yaxis_title="Number of Books",
            height=400,
        )
        # Display the decades line chart
        st.plotly_chart(fig_decades, use_container_width=True)

# Add this function to validate and fix your library data
def validate_library():
    """Validate and fix the library data structure."""
    valid_books = []
    required_fields = ['title', 'author', 'publication_year', 'genre', 'read_status', 'added_date']
    
    for book in st.session_state.library:
        # Check if book is a dictionary
        if not isinstance(book, dict):
            continue
            
        # Check if all required fields exist
        is_valid = True
        for field in required_fields:
            if field not in book:
                is_valid = False
                break
                
        if is_valid:
            valid_books.append(book)
        
    # Update the library with only valid books
    st.session_state.library = valid_books
    save_library()
    return len(valid_books)

# load library
load_library()
st.sidebar.markdown("<h1 style='text-align:center;'>📚 Personal Library Management System</h1>", unsafe_allow_html=True)
lottie_books = load_lottieurl("https://assets3.lottiefiles.com/packages/lf20_2j8g1v4h.json")
if lottie_books:
    with st.sidebar:
        st_lottie(lottie_books, speed=1, width=300, height=200, key="books_animation")

nav_options = st.sidebar.radio(
    "Choose an option",
    ["View library", "Add book", "Search book", "Library statistics"]
)
if nav_options == "View library":
    st.session_state.current_view = "library"
elif nav_options == "Add book":
    st.session_state.current_view = "add_book"
elif nav_options == "Search book":
    st.session_state.current_view = "search_book"
elif nav_options == "Library statistics":
    st.session_state.current_view = "library_statistics"

st.markdown("<h1 class='main-header'> Personal Library Manager </h1>", unsafe_allow_html=True)
if st.session_state.current_view == "add_book": 
    st.markdown("<h2 class='sub-header'> Add a New Book </h2>", unsafe_allow_html=True)

    # adding books input form
    with st.form(key="add_book_form"):
        col1, col2 = st.columns(2)

        with col1:
            title = st.text_input("Book Title", max_chars=100)
            author = st.text_input("Author", max_chars=100)
            publication_year = st.number_input("Publication Year", min_value=1000, max_value=datetime.now().year, step=1, value=datetime.now().year)
            
        with col2:
            genre = st.selectbox("Genre", ["Fiction", "philosophical", "spiritual novel", "Non-Fiction", "Science", "History", "Biography", "Fantasy", "Mystery", "Technology", "Romance", "Self-Help", "Poetry", "Travel", "Art", "Adventure", "Religion", "Cooking", "Health", "Children's", "Graphic Novel", "Comics", "Drama", "Thriller", "Horror", "Classic", "Other"])
            read_status = st.radio("Read Status", ["Read", "Unread"], horizontal=True)
            read_bool = read_status == "Read"
            submit_button = st.form_submit_button(label="Add Book")

        if submit_button and title and author:
            add_book(title, author, publication_year, genre, read_bool)

        if st.session_state.book_added:
            st.markdown("<div class='success-message'>Book added successfully!</div>", unsafe_allow_html=True)
            st.balloons()
            st.session_state.book_added = False
elif st.session_state.current_view == "library":
    st.markdown("<h2 class='sub-header'> Your Library </h2>", unsafe_allow_html=True)

    if not st.session_state.library:
        st.markdown("<div class='warning-message'>Your library is empty. Please add books to your library.</div>", unsafe_allow_html=True)
    else:
        cols = st.columns(2)
        for i, book in enumerate(st.session_state.library):
            # Skip invalid books
            if not isinstance(book, dict):
                continue
                
            with cols[i % 2]:
                # Safely get book values with defaults for missing keys
                title = book.get('title', 'Unknown Title')
                author = book.get('author', 'Unknown Author')
                year = book.get('publication_year', 'Unknown Year')
                genre = book.get('genre', 'Unknown Genre')
                read_status = book.get('read_status', False)
                
                st.markdown(f"""<div class='book-card'> 
                            <h3>{title}</h3>
                            <p><strong>Author:</strong> {author}</p>
                            <p><strong>Publication Year:</strong> {year}</p>
                            <p><strong>Genre:</strong> {genre}</p>
                            <p><span class='{'read-badge' if read_status else 'unread-badge'}'>{'Read' if read_status else 'Unread'}</span></p>
                            </div>""", unsafe_allow_html=True)

                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"Remove", key=f"remove_{i}", use_container_width=True):
                        if remove_book(i):
                            st.rerun()
                with col2:
                    new_status = not read_status
                    status_label = "Mark as Read" if not read_status else "Mark as Unread"
                    if st.button(status_label, key=f"status_{i}", use_container_width=True):
                        st.session_state.library[i]['read_status'] = new_status
                        save_library()
                        st.rerun()

    if st.session_state.book_remove:
        st.markdown("<div class='success-message'>Book removed successfully!</div>", unsafe_allow_html=True)
        st.session_state.book_remove = False
elif st.session_state.current_view == "search_book":
    st.markdown("<h2 class='sub-header'> Search for a Book </h2>", unsafe_allow_html=True)

    search_by = st.selectbox("Search by", ["title", "author", "genre", "publication_year"])
    search_term = st.text_input("Enter search term", max_chars=100)

    if st.button("Search", use_container_width=False):
        with st.spinner("Searching..."):
            time.sleep(0.7)
            search_book(search_term, search_by)
    
    if st.session_state.search_result:
        st.markdown(f"<h3>Found {len(st.session_state.search_result)} Results</h3>", unsafe_allow_html=True)

        for i, book in enumerate(st.session_state.search_result):
            st.markdown(f"""<div class='book-card'> 
                        <h3>{book['title']}</h3>
                        <p><strong>Author:</strong> {book['author']}</p>
                        <p><strong>Publication Year:</strong> {book['publication_year']}</p>
                        <p><strong>Genre:</strong> {book['genre']}</p>
                        <p><span class='{'read-badge' if book['read_status'] else 'unread-badge'}'>{'Read' if book['read_status'] else 'Unread'}</span></p>
                        </div>""", unsafe_allow_html=True)
    elif search_term:
        st.markdown("<div class='warning-message'>No results found.</div>", unsafe_allow_html=True)

elif st.session_state.current_view == "library_statistics":
    st.markdown("<h2 class='sub-header'> Library Statistics </h2>", unsafe_allow_html=True)

    if not st.session_state.library:
        st.markdown("<div class='warning-message'>Your library is empty. Please add books to your library.</div>", unsafe_allow_html=True)
    else:
        stats = get_library_stats()  # Get the stats here
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Total Books", value=stats['total_books'])
        with col2:
            st.metric(label="Read Books", value=stats['read_books'])
        with col3:
            st.metric(label="Percent Read", value=f"{stats['percent_read']:.2f}%")

        # Now pass stats to the create_visualization function
        create_visualization(stats)

        if stats['authors']:
            st.markdown("<h3>Top Authors</h3>", unsafe_allow_html=True)
            top_authors = dict(list(stats['authors'].items())[:5])  # Take top 5 authors
            for author, count in top_authors.items():
                st.markdown(f"**{author}:** {count} book{'s' if count > 1 else ''}", unsafe_allow_html=True)

st.markdown("---")
st.markdown("Copyright &copy; 2025 Asma Jawaid. All rights reserved.", unsafe_allow_html=True)
st.markdown("Made with ❤️ in Pakistan", unsafe_allow_html=True)
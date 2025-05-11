# models.py (New File)
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, timezone
from flask_app.modules.extensions import db
import logging

# Disable SQLAlchemy modification tracking globally for better performance
db.session.configure(autoflush=False)

# Configure SQLAlchemy logging - disable SQL query logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.pool').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.dialects').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.orm').setLevel(logging.WARNING)

# Association table for the many-to-many relationship between Audiobooks and Categories
audiobook_categories = db.Table('audiobook_categories',
    db.Column('audiobook_id', db.Integer, db.ForeignKey('audiobooks.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('categories.id'), primary_key=True)
)

class Category(db.Model):
    """Represents a category for audiobooks."""
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    sort_order = db.Column(db.Integer, nullable=False, default=0)

    # Relationship back to Audiobooks (optional, but good practice)
    audiobooks = db.relationship(
        'Audiobook',
        secondary=audiobook_categories,
        back_populates='categories',
        lazy='dynamic' # Use dynamic loading if you expect many audiobooks per category
    )
    
    # Set default ordering by sort_order
    __mapper_args__ = {
        "order_by": sort_order
    }

    def __repr__(self):
        return f'<Category {self.name}>'

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'sort_order': self.sort_order}


class Author(db.Model):
    """Represents an author of audiobooks."""
    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False, index=True)

    # Relationship back to Audiobooks (one-to-many)
    audiobooks = db.relationship(
        'Audiobook',
        back_populates='author',
        lazy='dynamic' # Use dynamic loading if you expect many audiobooks per author
    )

    def __repr__(self):
        return f'<Author {self.name}>'

    def to_dict(self):
        return {'id': self.id, 'name': self.name}


class SkippedVideo(db.Model):
    """Represents a YouTube video that was skipped during processing."""
    __tablename__ = 'skipped_videos'

    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.String(24), unique=True, nullable=False, index=True)
    reason = db.Column(db.String(255), nullable=True) # Reason why the video was skipped
    # Timestamp managed by the database
    timestamp = db.Column(
        db.DateTime(timezone=True),
        server_default=db.func.now(),
        onupdate=db.func.now(),
        nullable=False
    )

    def __repr__(self):
        return f'<SkippedVideo {self.video_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'video_id': self.video_id,
            'reason': self.reason,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
        }


class Audiobook(db.Model):
    """Represents an audiobook entry in the database, linking YouTube video and Google Books data."""

    __tablename__ = "audiobooks"  # Optional: Explicitly name the table

    id = db.Column(db.Integer, primary_key=True)

    # YouTube Video Data
    video_id = db.Column(
        db.String(24), unique=True, nullable=False, index=True
    )  # Added unique index
    title = db.Column(db.String(255), nullable=False) # Renamed from yt_title
    description = db.Column(db.Text, nullable=True) # Renamed from yt_description
    thumbnail = db.Column(db.String(524), nullable=True)  # Renamed from yt_thumbnail, increased length

    # Author (Foreign Key and Relationship)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=True, index=True)
    author = db.relationship('Author', back_populates='audiobooks', lazy='joined') # Use joined loading

    # Categories (Many-to-Many relationship)
    categories = db.relationship(
        'Category',
        secondary=audiobook_categories,
        back_populates='audiobooks',
        lazy='joined' # Use joined loading for efficiency when accessing categories
    )

    # Metadata
    duration = db.Column(
        db.Integer, nullable=True
    )  # Duration in seconds (if available from YT)
    # Use timezone.utc for compatibility
    timestamp = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )  # When record was added/updated

    def __repr__(self):
        """Provide a helpful representation when printing the object."""
        return f'<Audiobook {self.id}: "{self.title}" (Video ID: {self.video_id})>'

    def to_dict(self):
        """Convert the Audiobook object to a dictionary for JSON serialization."""
        return {
            "id": self.id,
            "video_id": self.video_id,
            "title": self.title,
            "description": self.description,
            "thumbnail": self.thumbnail,
            "author": self.author.name if self.author else None, # Access name via relationship
            "categories": [category.name for category in self.categories], # List of category names
            "duration": self.duration,
            "timestamp": (
                self.timestamp.isoformat()
                if isinstance(self.timestamp, datetime)
                else None
            ),
        }


class YoutubeSearchState(db.Model):
    """Stores state information for the YouTube search process, like the next page token."""
    __tablename__ = 'youtube_search_state'

    id = db.Column(db.Integer, primary_key=True)
    # Use a key to identify the state variable, e.g., 'next_page_token'
    key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    value = db.Column(db.String(255), nullable=True) # Store the token value here
    timestamp = db.Column(
        db.DateTime(timezone=True),
        server_default=db.func.now(),
        onupdate=db.func.now(),
        nullable=False
    )

    def __repr__(self):
        return f'<YoutubeSearchState {self.key}={self.value}>'

    def to_dict(self):
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
        }

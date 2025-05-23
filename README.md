# Music Score PDF Viewer

A PyQt5-based PDF viewer specifically designed for displaying music scores with MusicXML integration.

## Features

- Open and display PDF files containing music scores
- Navigate between pages with Previous and Next buttons
- Zoom in and out functionality for detailed viewing
- Fit to width functionality for better score viewing
- Rotation support (90° increments) for landscape/portrait sheet music
- Multiple view modes: Single Page, Two Pages, Continuous
- Smooth scrolling and panning
- Keyboard shortcuts for efficient navigation
- **MusicXML integration** - automatically loads associated MusicXML files
- Display music score metadata from MusicXML (title, composer, parts)

## Requirements

- Python 3.6 or higher
- PyQt5
- PyMuPDF (fitz)

## Installation

1. Clone this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the application with:

```
python music_pdf_viewer.py
```

Then use the "Open PDF" button to select and view your music score PDF files.

### MusicXML Integration

When opening a PDF file, the application automatically looks for a MusicXML file with the same basename:
- It checks for both `.xml` and `.musicxml` extensions
- If found, it loads and parses the MusicXML file
- A dock panel displays music metadata (title, composer, parts, etc.)
- You can toggle between basic and detailed views of the MusicXML content

To use this feature:
1. Have your music score in both PDF and MusicXML formats
2. Name them identically (e.g., `myscore.pdf` and `myscore.xml` or `myscore.musicxml`)
3. When opening the PDF, the application will automatically detect and load the MusicXML data

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Left Arrow, Page Up | Previous page |
| Right Arrow, Page Down | Next page |
| Home | First page |
| End | Last page |
| Ctrl + Plus (+) | Zoom in |
| Ctrl + Minus (-) | Zoom out |
| Ctrl + 0 | Reset zoom (100%) |
| Ctrl + W | Fit to width |
| Ctrl + R | Rotate right (90° clockwise) |
| Ctrl + L | Rotate left (90° counter-clockwise) |
| Ctrl + O | Open file |

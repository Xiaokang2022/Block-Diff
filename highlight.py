import tkinter

tags_operator = {
    "insert": {
        "background": "lightgreen",
    },
    "delete": {
        "background": "pink",
    },
    "update": {
        "background": "orange",
    },
    "copy": {
        "background": "skyblue",
    },
    "move": {
        "background": "yellow",
    },
    "merge": {
        "background": "violet",
    },
    "split": {
        "background": "cyan",
    }
}

tags_grammar = {
    "comments": {
        "foreground": "#808080",
    },
    "keywords": {
        "foreground": "#CB92C6",
    },
    "variables": {
        "foreground": "#00FF7F",
    },
    "strings": {
        "foreground": "#FF4500",
    },
    "functions": {
        "foreground": "#FFD700",
    },
    "numbers": {
        "foreground": "#87CEEB",
    },
    "operators": {
        "foreground": "#FF6347",
    },
    "classes": {
        "foreground": "#FF69B4",
    },
}

def register_color_tags(*widgets: tkinter.Text) -> None:
    """Register color tags to the `tkinter.Text` widget."""
    for widget in widgets:
        for tag, options in tags_operator.items():
            widget.tag_configure(tag, **options)
        for tag, options in tags_grammar.items():
            widget.tag_configure(tag, **options)

# Streamlit Demo Applications
This repository contains multiple Streamlit demo applications. Follow the instructions below to set up the environment, install the required dependencies, and run each demo app.

## Setup

### 1. Create a Virtual Environment

First, create a virtual environment to manage dependencies:

```sh
python -m venv .venv
```

### 2. Activate the Virtual Environment

Activate the virtual environment:

On Windows:
```sh
.venv\Scripts\activate
```

On macOS and Linux:
```sh
source .venv/bin/activate
```

### 3. Install Requirements

Install the required dependencies using pip:

```sh
pip install -r requirements.txt
```

## Running the Demo Applications

### Streamlit First App

To run the demo applications in the `streamlit_first_app` directory:

- **Demo 1:**
    ```sh
    streamlit run streamlit_first_app/demo1.py
    ```

- **Demo 2:**
    ```sh
    streamlit run streamlit_first_app/demo2.py
    ```

- **Demo 3:**
    ```sh
    streamlit run streamlit_first_app/demo3.py
    ```

### Streamlit Chatbot

To run the chatbot application:

```sh
streamlit run streamlit_chatbot/app.py
```

### Streamlit Object Detection

To run the object detection application:

```sh
streamlit run streamlit_object_detection/app.py
```

### Streamlit Titanic Demo

To run the Titanic demo application:

```sh
streamlit run streamlit_titanic/app.py
```

### Streamlit Uber

To run the Uber demo application:

```sh
streamlit run streamlit_uber/app.py
```

## Additional Information

For more details on each application, refer to the respective Python files in their directories.
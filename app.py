import cv2
import numpy as np
import streamlit as st

st.title("Visual Difference Analysis")
st.write("Environment is ready.")
st.write(f"OpenCV {cv2.__version__} · NumPy {np.__version__} · Streamlit {st.__version__}")

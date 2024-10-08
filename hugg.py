import streamlit as st
import requests
from PIL import Image
import io

# Hugging Face API URL and headers
API_URLS = {
    "FLUX.1-schnell": "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell",
    "FLUX.1-dev": "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-dev",
    "RealismLora": "https://api-inference.huggingface.co/models/XLabs-AI/flux-RealismLora"
}
headers = {"Authorization": "Bearer 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"}

def query(api_url, payload):
    response = requests.post(api_url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.content
    else:
        st.error(f"API request failed with status code {response.status_code}: {response.text}")
        return None

def generate_image(prompt, model_name):
    try:
        api_url = API_URLS[model_name]
        image_bytes = query(api_url, {"inputs": prompt})
        if image_bytes:
            # Check if the response is a valid image
            image = Image.open(io.BytesIO(image_bytes))
            return image
    except IOError:
        st.error("Error: The API response is not a valid image file.")
    except Exception as e:
        st.error(f"Error generating image: {e}")
    return None

def main():
    st.sidebar.title("Select an Option")
    app_mode = st.sidebar.radio("Choose an option", ["Generate Image from Prompt", "Face Swap"])

    if app_mode == "Generate Image from Prompt":
        st.title("Generate Image from Prompt")

        # Model selection
        model_name = st.selectbox("Select a model", ["FLUX.1-schnell", "FLUX.1-dev", "RealismLora"])

        # Prompt input
        prompt = st.text_input("Enter a prompt for the image:")

        # Add a button to generate the image
        if st.button("Generate Image"):
            if prompt:
                with st.spinner('Generating image...'):
                    img = generate_image(prompt, model_name)
                    if img:
                        st.image(img, caption="Generated Image", use_column_width=True)
                        
                        # Prepare image for download
                        buffer = io.BytesIO()
                        img.save(buffer, format="JPEG")
                        buffer.seek(0)

                        st.download_button(
                            label="Download Generated Image",
                            data=buffer,
                            file_name="generated_image.jpg",
                            mime="image/jpeg"
                        )
            else:
                st.error("Please enter a prompt.")

    elif app_mode == "Face Swap":
        st.title("Face Swap App")

        # Upload source image
        st.subheader("Upload Source Image")
        source_image = st.file_uploader("Choose a source image...", type=["jpg", "jpeg"])

        # Upload target image
        st.subheader("Upload Target Image")
        target_image = st.file_uploader("Choose a target image...", type=["jpg", "jpeg"])

        if source_image and target_image:
            st.image(source_image, caption="Source Image", use_column_width=True)
            st.image(target_image, caption="Target Image", use_column_width=True)

            if st.button("Swap Faces"):
                source_img = Image.open(source_image)
                target_img = Image.open(target_image)

                # Convert images to base64 with high quality
                source_b64 = image_to_base64(source_img)
                target_b64 = image_to_base64(target_img)

                # API call for face swapping
                api_key = "SG_00ff2b1abfdc214f"  # Directly included API key
                url = "https://api.segmind.com/v1/faceswap-v2"
                data = {
                    "source_img": source_b64,
                    "target_img": target_b64,
                    "input_faces_index": 0,
                    "source_faces_index": 0,
                    "face_restore": "codeformer-v0.1.0.pth",
                    "base64": False
                }

                headers = {
                    'x-api-key': api_key,
                    'Content-Type': 'application/json'
                }

                response = requests.post(url, json=data, headers=headers)

                if response.status_code == 200:
                    # Handle response as an image
                    image_bytes = io.BytesIO(response.content)
                    swapped_img = Image.open(image_bytes)
                    st.image(swapped_img, caption="Face Swapped Image", use_column_width=True)

                    # Prepare image for download
                    buffer = io.BytesIO()
                    swapped_img.save(buffer, format="JPEG")
                    buffer.seek(0)

                    st.download_button(
                        label="Download Face Swapped Image",
                        data=buffer,
                        file_name="face_swapped_image.jpg",
                        mime="image/jpeg"
                    )
                else:
                    st.error(f"Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    main()
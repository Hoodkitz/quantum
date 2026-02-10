import streamlit as st
import os
import sys
import subprocess
from llm_logic import LLMClient
import packager

st.set_page_config(page_title="TFQ Zero-Code Builder", page_icon="⚛️", layout="wide")

st.title("⚛️ TensorFlow Quantum Zero-Code Builder")
st.markdown("""
Build, visualize, and deploy Quantum Machine Learning applications from a single text prompt.
""")

# Sidebar for Configuration
with st.sidebar:
    st.header("Configuration")
    provider = st.selectbox("AI Provider", ["Gemini", "OpenAI"])
    api_key = st.text_input(f"{provider} API Key", type="password")

    st.info("Get a free Gemini API key from Google AI Studio or use your OpenAI key.")

    st.divider()
    st.markdown("### Deployment Targets")
    st.checkbox("Source Code (.py)", value=True, disabled=True)
    st.checkbox("Windows Executable (.exe)", value=True, disabled=True)
    st.markdown("*Android APK generation requires external build tools, but you can access this web interface from Android.*")

# Main Interface
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Describe your Quantum App")
    prompt = st.text_area(
        "What do you want to build?",
        height=200,
        placeholder="Example: Create a Quantum Neural Network to classify MNIST digits 3 and 6. Use a simple 4-qubit circuit and train for 5 epochs. Plot the loss curve."
    )

    generate_btn = st.button("🚀 Generate App", type="primary")

# Initialize session state
if "generated_code" not in st.session_state:
    st.session_state.generated_code = ""
if "app_generated" not in st.session_state:
    st.session_state.app_generated = False

# Generation Logic
if generate_btn:
    if not api_key:
        st.error("Please provide an API Key in the sidebar.")
    elif not prompt:
        st.error("Please enter a prompt.")
    else:
        with st.spinner(f"Consulting {provider} and writing Quantum Code..."):
            try:
                client = LLMClient(api_key=api_key, provider=provider)
                code = client.generate_code(prompt)

                if code.startswith("# Error"):
                    st.error(code)
                else:
                    st.session_state.generated_code = code
                    st.session_state.app_generated = True

                    # Save to disk immediately
                    packager.save_code(code)
                    st.success("App generated successfully!")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

# Results Area
if st.session_state.app_generated:
    with col2:
        st.subheader("Generated Source Code")
        st.code(st.session_state.generated_code, language="python")

    st.divider()

    # Action Buttons
    c1, c2, c3 = st.columns(3)

    with c1:
        st.subheader("👀 Live Preview")
        if st.button("Run Preview"):
            with st.spinner("Executing Quantum Circuit..."):
                # Save again just to be sure
                script_path = packager.save_code(st.session_state.generated_code)

                # Run the script
                try:
                    # Clean up old plot
                    if os.path.exists("result.png"):
                        os.remove("result.png")

                    result = subprocess.run(
                        [sys.executable, script_path],
                        capture_output=True,
                        text=True,
                        cwd=packager.GENERATED_DIR
                    )

                    st.text("Output Log:")
                    st.code(result.stdout)

                    if result.stderr:
                        st.text("Errors/Warnings:")
                        st.code(result.stderr)

                    # Check for image
                    plot_path = os.path.join(packager.GENERATED_DIR, "result.png")
                    if os.path.exists(plot_path):
                        st.image(plot_path, caption="Resulting Plot")
                    else:
                        st.warning("No 'result.png' generated. Did the script save the plot?")

                except Exception as e:
                    st.error(f"Execution failed: {e}")

    with c2:
        st.subheader("📦 Download Source")
        zip_path = packager.create_zip_package()
        with open(zip_path, "rb") as fp:
            st.download_button(
                label="Download ZIP Package",
                data=fp,
                file_name="quantum_app.zip",
                mime="application/zip"
            )

    with c3:
        st.subheader("🪟 Windows App")
        if st.button("Build .EXE"):
            with st.spinner("Compiling with PyInstaller... (This may take a minute)"):
                script_path = packager.save_code(st.session_state.generated_code)
                exe_path, status = packager.build_exe(script_path)

                if exe_path:
                    st.success(f"Built successfully!")
                    with open(exe_path, "rb") as fp:
                        st.download_button(
                            label="Download .EXE",
                            data=fp,
                            file_name=os.path.basename(exe_path),
                            mime="application/vnd.microsoft.portable-executable"
                        )
                else:
                    st.error(f"Build failed: {status}")

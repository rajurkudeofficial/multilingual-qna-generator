import streamlit as st
from pathlib import Path
import subprocess
import sys
import time
import pandas as pd


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Multilingual Q&A Generator",
    page_icon="🌐",
    layout="wide"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.2rem;
    }

    .subtitle {
        text-align: center;
        color: #888;
        margin-bottom: 2rem;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">🌐 Multilingual Q&A Generator</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Generate context-aware Q&A pairs from PDF, DOCX, and TXT '
    'in English, Hindi, and Marathi.'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.header("⚙️ Configuration")

    num_questions = st.number_input(
        "Number of Questions",
        min_value=1,
        max_value=20,
        value=4,
        step=1
    )

    device = st.selectbox(
        "Compute Device",
        ["cpu", "cuda", "auto"],
        index=0
    )

    model_type = st.selectbox(
        "Model",
        ["q5_k_m", "q4_k_m"],
        index=0
    )

    top_k = st.slider(
        "Context Chunks (Top-K)",
        1,
        10,
        3
    )

    chunk_size = st.number_input(
        "Chunk Size",
        min_value=128,
        max_value=2048,
        value=512,
        step=128
    )

    chunk_overlap = st.number_input(
        "Chunk Overlap",
        min_value=0,
        max_value=512,
        value=128,
        step=32
    )

    st.markdown("---")

    st.caption(
        "💡 CPU mode is recommended for the current setup."
    )


# =========================================================
# FILE UPLOAD
# =========================================================

st.subheader("📄 Upload Document")

uploaded_file = st.file_uploader(
    "Upload a PDF, DOCX, or TXT file",
    type=["pdf", "docx", "txt"]
)


# =========================================================
# GENERATE
# =========================================================

if uploaded_file:

    extension = Path(uploaded_file.name).suffix.lower()

    st.success(
        f"Selected file: **{uploaded_file.name}**"
    )

    st.write(
        f"File type: `{extension.upper()}`"
    )

    generate = st.button(
        "🚀 Generate Q&A",
        type="primary",
        use_container_width=True
    )

    if generate:

        # -------------------------------------------------
        # Save uploaded file
        # -------------------------------------------------

        input_dir = Path("input")
        input_dir.mkdir(exist_ok=True)

        input_path = input_dir / uploaded_file.name

        with open(input_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # -------------------------------------------------
        # Output
        # -------------------------------------------------

        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)

        output_path = output_dir / "QnA.xlsx"

        # -------------------------------------------------
        # Build command
        # -------------------------------------------------

        command = [
            sys.executable,
            "main.py",
            "--input",
            str(input_path),
            "--output",
            str(output_path),
            "--num-questions",
            str(int(num_questions)),
            "--top-k",
            str(int(top_k)),
            "--chunk-size",
            str(int(chunk_size)),
            "--chunk-overlap",
            str(int(chunk_overlap)),
            "--device",
            device,
            "--model-type",
            model_type
        ]

        # -------------------------------------------------
        # Pipeline Progress
        # -------------------------------------------------

        st.subheader("⚙️ Pipeline Progress")

        status = st.status(
            "🚀 Starting Q&A generation...",
            expanded=True
        )

        log_placeholder = st.empty()

        logs = []

        start_time = time.time()

        try:

            # -------------------------------------------------
            # Run main.py as separate process
            # -------------------------------------------------

            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            # -------------------------------------------------
            # Read live logs
            # -------------------------------------------------

            for line in iter(
                process.stdout.readline,
                ""
            ):

                line = line.rstrip()

                if not line:
                    continue

                logs.append(line)

                elapsed = int(
                    time.time() - start_time
                )

                status.update(
                    label=(
                        f"🚀 Generating Q&A... "
                        f"{elapsed}s"
                    ),
                    state="running"
                )

                # Show latest 20 lines
                log_placeholder.code(
                    "\n".join(logs[-20:])
                )

            process.stdout.close()

            return_code = process.wait()

            elapsed = int(
                time.time() - start_time
            )

            # -------------------------------------------------
            # Failure
            # -------------------------------------------------

            if return_code != 0:

                status.update(
                    label="❌ Generation failed",
                    state="error"
                )

                st.error(
                    "Pipeline failed. Check the logs below."
                )

                with st.expander(
                    "🔍 Full Pipeline Logs",
                    expanded=True
                ):

                    st.code(
                        "\n".join(logs)
                    )

                st.stop()

            # -------------------------------------------------
            # Success
            # -------------------------------------------------

            status.update(
                label=(
                    f"✅ Generation completed "
                    f"in {elapsed}s"
                ),
                state="complete"
            )

            st.success(
                f"🎉 Q&A generated successfully "
                f"in **{elapsed} seconds**!"
            )

            # -------------------------------------------------
            # Verify Excel
            # -------------------------------------------------

            if not output_path.exists():

                st.error(
                    "Pipeline completed but "
                    "QnA.xlsx was not found."
                )

                st.stop()

            # -------------------------------------------------
            # Results
            # -------------------------------------------------

            st.subheader(
                "📊 Generated Q&A"
            )

            excel_file = pd.ExcelFile(
                output_path
            )

            tabs = st.tabs(
                [
                    "🇬🇧 English",
                    "🇮🇳 Hindi",
                    "🇮🇳 Marathi"
                ]
            )

            sheets = [
                "English",
                "Hindi",
                "Marathi"
            ]

            for tab, sheet in zip(
                tabs,
                sheets
            ):

                with tab:

                    if sheet in excel_file.sheet_names:

                        df = pd.read_excel(
                            output_path,
                            sheet_name=sheet
                        )

                        st.dataframe(
                            df,
                            use_container_width=True,
                            hide_index=True
                        )

                        st.caption(
                            f"Total Q&A pairs: {len(df)}"
                        )

                    else:

                        st.warning(
                            f"{sheet} sheet not found."
                        )

            # -------------------------------------------------
            # Download
            # -------------------------------------------------

            st.subheader(
                "⬇️ Download Result"
            )

            with open(
                output_path,
                "rb"
            ) as f:

                excel_bytes = f.read()

            st.download_button(
                label="📥 Download QnA.xlsx",
                data=excel_bytes,
                file_name="QnA.xlsx",
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                ),
                use_container_width=True
            )

            # -------------------------------------------------
            # Logs
            # -------------------------------------------------

            with st.expander(
                "📋 Pipeline Logs"
            ):

                st.code(
                    "\n".join(logs)
                )

        except Exception as e:

            status.update(
                label="❌ Application error",
                state="error"
            )

            st.error(
                f"Application error: {e}"
            )

            with st.expander(
                "🐞 Technical Error"
            ):

                st.exception(e)


# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    "Multilingual Q&A Generation System • "
    "PDF / DOCX / TXT → English / Hindi / Marathi"
)
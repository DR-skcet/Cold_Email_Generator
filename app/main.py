import streamlit as st
from langchain_community.document_loaders import WebBaseLoader

from chains import Chain
from portfolio import Portfolio
from utils import clean_text


def create_streamlit_app(llm, portfolio, clean_text):
    st.set_page_config(layout="wide", page_title="Cold Email Generator", page_icon="📧")
    st.title("📧 Cold Mail Generator")
    st.markdown("Generate personalized cold emails from job descriptions using AI + your portfolio!")

    # Sidebar Instructions
    with st.sidebar:
        st.header("🔧 How to Use")
        st.markdown("""
        1. Paste a job URL (from company career pages).
        2. Click **Submit**.
        3. View generated email based on your portfolio.
        """)
        st.markdown("---")
        st.info("✅ Make sure your portfolio CSV is loaded properly.")

    url_input = st.text_input("🔗 Enter a job URL:", 
                              value="https://ibmglobal.avature.net/en_US/careers/JobDetail?jobId=30886&source=WEB_Search_INDIA")

    if st.button("🚀 Submit"):
        with st.spinner("Extracting job details and generating email..."):
            try:
                # Load and clean job description
                loader = WebBaseLoader([url_input])
                raw_content = loader.load().pop().page_content
                data = clean_text(raw_content)

                # Load user portfolio
                portfolio.load_portfolio()

                # Extract jobs
                jobs = llm.extract_jobs(data)

                if not jobs:
                    st.warning("No job info could be extracted. Try another URL.")
                    return

                # Process each job
                for idx, job in enumerate(jobs):
                    st.markdown(f"### 📌 Job #{idx + 1}: {job.get('title', 'Untitled')}")
                    
                    with st.expander("📄 View Extracted Job Description"):
                        st.markdown(job.get('description', 'No description found'))

                    skills = job.get('skills', [])
                    if skills:
                        st.markdown("**🧠 Required Skills:**")
                        st.markdown(", ".join(skills))
                    
                    # Find matching links
                    links = portfolio.query_links(skills)
                    
                    # Generate email
                    email = llm.write_mail(job, links)
                    st.success("✅ Email generated successfully!")
                    st.code(email, language='markdown')
            except Exception as e:
                with st.expander("🚨 Error Details"):
                    st.error(f"An error occurred: {e}")


if __name__ == "__main__":
    chain = Chain()
    portfolio = Portfolio()
    create_streamlit_app(chain, portfolio, clean_text)

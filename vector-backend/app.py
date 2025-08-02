import re
from flask import Flask, request, jsonify
from models import ChatSession, FollowUp, db
from flask import stream_with_context, Response
import uuid
import os
import prompt_checker
from utils import format_llm_prompt
import prompt_optimizer
import google_search
from threading import Thread
import site_loader
import deep_research
import vector_store_modification
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
from flask_cors import CORS
import sys
import time
import format_response
from flask_migrate import Migrate
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# Initialize Flask app and database

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///chat_sessions.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# CORS configuration for production
allowed_origins = [
    "http://localhost:3000",  # Local development
    "https://your-app.vercel.app",  # Replace with your Vercel domain
]

# Add environment variable for additional origins
if os.getenv("FRONTEND_URL"):
    allowed_origins.append(os.getenv("FRONTEND_URL"))

CORS(app, origins=allowed_origins)

db.init_app(app)
migrate = Migrate(app, db)

# Handle missing files gracefully in production
try:
    with open("vector_store_id.txt", "r") as f:
        vector_store_id = f.read().strip()
except FileNotFoundError:
    print("⚠️ vector_store_id.txt not found - some features may not work")
    vector_store_id = "default-store-id"

try:
    with open("assistant_id.txt", "r") as f:
        assistant_id = f.read().strip()
except FileNotFoundError:
    print("⚠️ assistant_id.txt not found - some features may not work")
    assistant_id = "default-assistant-id"

# Global dictionary to store queues for each session's streaming progress
site_progress_queues = {}  # session_id -> Queue
full_response_text = ""

def fetch_links(query):
    print(f"Fetching links for query: {query}", flush=True)
    return google_search.fetch_google_search_links(query)

def clean_query(q: str) -> str:
    # Removes leading numbering and surrounding quotes
    q = re.sub(r'^\d+\.\s*', '', q)
    return q.strip().strip('"')


@app.route('/')
def health_check():
    """Health check endpoint for Railway deployment"""
    return jsonify({
        "status": "healthy",
        "app": "Vector Backend",
        "version": "1.0.0"
    })


@app.route('/session', methods=['POST'])
def create_session():
    data = request.get_json()
    question = data.get("initial_question")

    if not question:
        return jsonify({"error": "Initial question is required"}), 400

    session = ChatSession(initial_question=question)
    prompt_validation = prompt_checker.check_prompt(question)
    is_followup_mode = prompt_validation.research_required

    db.session.add(session)
    db.session.flush()

    if is_followup_mode:
        followups = prompt_validation.follow_up or []
        for i, fq in enumerate(followups):
            db.session.add(FollowUp(
                session_id=session.id,
                question=fq,
                order=i
            ))
        db.session.commit()
        return jsonify({
            "session_id": session.id,
            "mode": "followup",
            "followups": followups
        })
    else:
        session.short_answer = prompt_validation.basic_answer
        db.session.commit()
        return jsonify({
            "session_id": session.id,
            "mode": "short",
            "short_answer": session.short_answer
        })


@app.route('/answer', methods=['POST'])
def submit_answer():
    data = request.get_json()
    session_id = data.get("session_id")
    index = data.get("question_index")
    answer = data.get("answer")

    if not all([session_id, isinstance(index, int), answer]):
        return jsonify({"error": "Missing or invalid parameters"}), 400

    followup = FollowUp.query.filter_by(session_id=session_id, order=index).first()
    if not followup:
        return jsonify({"error": "Follow-up not found"}), 404

    followup.answer = answer
    db.session.commit()

    return jsonify({"message": "Answer saved successfully"})


@app.route('/session/<session_id>/full', methods=['GET'])
def get_full_session(session_id):
    session = ChatSession.query.filter_by(id=session_id).first()
    if not session:
        return jsonify({"error": "Session not found"}), 404

    followups_data = [
        {"question": f.question, "answer": f.answer}
        for f in sorted(session.followups, key=lambda x: x.order)
    ]

    return jsonify({
        "initial_question": session.initial_question,
        "followups": followups_data
    })


@app.route('/session/<session_id>/get_links', methods=['GET'])
def get_links(session_id):
    session = ChatSession.query.filter_by(id=session_id).first()
    if not session:
        return jsonify({"error": "Session not found"}), 404

    formatted_prompt = format_llm_prompt(session)
    searches = prompt_optimizer.prompt_optimization(unfiltered_prompt=formatted_prompt)

    raw_queries = [q.strip() for q in searches.strip().split('\n') if q.strip()]
    queries = [clean_query(q) for q in raw_queries]

    all_links = set()
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(fetch_links, q) for q in queries]
        for future in as_completed(futures):
            try:
                links = future.result()
                all_links.update(links)
            except Exception as e:
                print(f"[ERROR] During fetch: {str(e)}", flush=True)

    return jsonify({"links": list(all_links)})


@app.route('/session/<session_id>/download_sites', methods=['POST'])
def download_sites(session_id):
    session = ChatSession.query.filter_by(id=session_id).first()
    if not session:
        return jsonify({"error": "Session not found"}), 404

    data = request.get_json()
    links = data.get("links", [])
    if not links:
        return jsonify({"error": "No links provided"}), 400

    print(f"[DOWNLOAD] Downloading {len(links)} links", flush=True)

    q = Queue()
    site_progress_queues[session_id] = q

    def site_loader_thread():
        print(f"[THREAD] Starting site loader thread for {session_id}", flush=True)
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = {executor.submit(site_loader.fetch_page_content, link): link for link in links}
            for future in as_completed(futures):
                url = futures[future]
                try:
                    content = future.result()
                    print(f"[THREAD] Got content for {url}", flush=True)
                    q.put(f"loaded: {url}")
                except Exception as e:
                    print(f"[ERROR] Failed to fetch {url}: {e}", flush=True)
                    q.put(f"error: {url} — {str(e)}")

        print(f"[THREAD] Done loading for {session_id}", flush=True)

        # ✅ Run vector store logic only after downloads complete
        try:
            vector_store_modification.collect_and_process_files()
            print(f"[THREAD] Vector store update complete", flush=True)
        except Exception as ve:
            print(f"[ERROR] Vector store update failed: {ve}", flush=True)

        q.put("__done__")

    Thread(target=site_loader_thread).start()

    return jsonify({"message": "Site loading started."}), 202


@app.route('/session/<session_id>/progress_stream')
def stream_progress(session_id):
    def generate():
        q = site_progress_queues.get(session_id)
        if not q:
            yield "data: __done__\n\n"
            return
        while True:
            update = q.get()
            print(f"[SSE] Sending: {update}", flush=True)
            yield f"data: {update}\n\n"
            sys.stdout.flush()
            time.sleep(0.01)

            if update == "__done__":
                break

    return Response(stream_with_context(generate()), mimetype='text/event-stream')


@app.route('/session/<session_id>/deep_research', methods=['POST'])
def deep_research_session(session_id):
    session = ChatSession.query.filter_by(id=session_id).first()
    if not session:
        return jsonify({"error": "Session not found"}), 404

    formatted_prompt = format_llm_prompt(session)

    # Get both thread_id and stream
    thread_id, response_stream = deep_research.run_deep_research(
        prompt=formatted_prompt,
        assistant_id=assistant_id,
    )

    # ✅ Save thread_id to session
    session.thread_id = thread_id
    db.session.commit()

    def generate_response():
        global full_response_text
        full_response_text = ""
        try:
            for chunk in response_stream:
                full_response_text += chunk
                yield chunk
        except Exception as e:
            full_response_text += f"[ERROR] {str(e)}"
            yield f"[ERROR] {str(e)}"

    return Response(generate_response(), mimetype='text/plain')

@app.route('/session/<session_id>/formatted_response', methods=['GET'])
def get_formatted_response(session_id):
    session = ChatSession.query.filter_by(id=session_id).first()
    if not session or not session.thread_id:
        return jsonify({"error": "Session not found or thread not started"}), 404

    try:
        # Retrieve messages from the thread
        messages = client.beta.threads.messages.list(thread_id=session.thread_id)

        if not messages.data:
            return jsonify({"error": "No messages found for thread"}), 404

        # Use the most recent message (adjust index if needed)
        latest_message = messages.data[0]

        # Replace citation placeholders with actual filenames
        formatted_output = format_response.replace_citation_placeholders(latest_message)

        print(f"[FORMAT] Final output: {formatted_output}", flush=True)
        return jsonify({"formatted": formatted_output})

    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == "__main__":
    app.run(debug=True)
